import os
import json
import pandas as pd
import numpy as np
import ast
from dotenv import load_dotenv
from shiny import reactive, render, ui
from google import genai
from google.genai import types
import markdown

from context import get_all_candidates, get_all_jobs

load_dotenv()

# === Tool Function ===
def correlate_columns(df: pd.DataFrame, col1: str, col2: str) -> dict:
    if col1 not in df.columns or col2 not in df.columns:
        return {"error": f"One or both columns not found: '{col1}', '{col2}'"}
    if col1 == col2:
        return {"error": "Cannot correlate a column with itself."}
    subset = df[[col1, col2]].dropna()
    for col in [col1, col2]:
        if subset[col].dtype == "object" or pd.api.types.is_categorical_dtype(subset[col]):
            subset[col], _ = pd.factorize(subset[col])
    try:
        return subset.corr(method="pearson").to_dict()
    except Exception as e:
        return {"error": str(e)}

# === Gemini Client Setup ===
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
MODEL_NAME = "gemini-3-flash-preview"

# Tool definition for new SDK - we can just pass the function itself in some contexts, 
# but for manual chat management usually explicit tools list is safer.
# However, for this analysis, the tool is not actually *called* by the model in the chat loop 
# shown in the original code (look at lines 134-136).
# The original code passed `tools=[correlation_tool]` to the model, but then in `correlation_output`, 
# the Python code CALLS the tool `correlate_columns(...)` manually at line 118, 
# gets the result, formats a prompt string with the result, and sends it to Gemini.
# Gemini DOES NOT appear to be calling the tool itself in the `correlation_output` flow.
# In `chat_response` (follow-up), it also just sends prompt + context.
# So the tool definition might be legacy or successfully ignored by the old model.
# I will REMOVE the unused tool definition to simplify migration and avoid errors.


# === Server ===
def server(input, output, session):
    print("✅ Loaded context-aware Gemini correlation server")

    last_corr = reactive.Value(None)
    last_cols = reactive.Value(("", ""))
    chat_status = reactive.Value("")


    @reactive.effect
    def _populate_job_ids():
        raw_candidates = get_all_candidates()
        job_ids_used = {c.get("job_id") for c in raw_candidates.values() if "job_id" in c}

        all_jobs = get_all_jobs()

        # Build label: value mapping
        job_choices = {
            job_id: f"{job_data.get('title', 'Untitled')} ({job_id[:8]})"
            for job_id, job_data in all_jobs.items()
            if job_id in job_ids_used
        }

        print(f"📊 Populating job_id dropdown with {len(job_choices)} items")
        ui.update_select("job_id", choices=job_choices)


    @reactive.Calc
    def candidates():
        raw = get_all_candidates()
        job_id = input.job_id()
        if not job_id:
            return pd.DataFrame()
        df = pd.DataFrame([c for c in raw.values() if c.get("job_id") == job_id])
        #df["Years of Experience"] = pd.to_numeric(df["Years of Experience"], errors="coerce")
        #df["avg_score"] = pd.to_numeric(df["avg_score"], errors="coerce")
        #df["Key Skills"] = df["Key Skills"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        return df

    @reactive.effect
    def _populate_cols():
        df = candidates()
        if df.empty:
            return
        exclude = {
            "Name", "Email", "Key Skills", "Candidate ID", "Application ID", "Resume File",
            "Llama Summary", "Gemini Summary", "Note", "candidate_id", "job_id",
            "application_date", "source"
        }
        cols = [col for col in df.columns if col not in exclude]
        ui.update_select("col1", choices=cols)
        ui.update_select("col2", choices=cols)

    @output
    @render.table
    def candidate_table():
        df = candidates()
        return df.drop(columns=["Resume File", "Llama Summary", "Gemini Summary", "onboarding_docs", "job_id", "Candidate ID"], errors="ignore").head(10)

    @output
    @render.ui
    def correlation_output():
        if input.calc_corr() == 0:
            return ui.p("⬇️ Select columns and click 'Calculate Correlation'.")
        df = candidates()
        col1 = input.col1()
        col2 = input.col2()
        if df.empty or not col1 or not col2:
            return ui.p("⚠️ Please select a job and valid columns.")
        result = correlate_columns(df, col1, col2)
        if "error" in result:
            return ui.p(f"❌ {result['error']}")
        try:
            corr_value = result[col1][col2]
        except:
            return ui.p("❌ Failed to extract correlation value.")

        last_corr.set(corr_value)
        last_cols.set((col1, col2))

        prompt = (
            f"The Pearson correlation between '{col1}' and '{col2}' is {corr_value:.4f}.\n\n"
            f"Explain this for a recruiter: include statistical meaning, hiring implications, and limitations."
        )
        try:
            # We use a fresh chat or generate_content for the initial explanation
            # New SDK format:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.4)
            )
            explanation = markdown.markdown(response.text.strip())
        except Exception as e:
            explanation = f"<b>⚠️ Gemini error:</b> {str(e)}"

        return ui.HTML(f"""
            <div><strong>{col1}</strong> vs <strong>{col2}</strong> correlation: <b>{corr_value:.4f}</b></div>
            <hr><div><strong>LLM Explanation:</strong><br>{explanation}</div>
        """)

    @output
    @render.text
    def chat_status_ui():
        return chat_status.get()

    @output
    @render.ui
    @reactive.event(input.chat_send)
    def chat_response():
        user_msg = input.chat_input().strip()
        col1, col2 = last_cols.get()
        corr_value = last_corr.get()
        df = candidates()

        if not user_msg:
            return ui.HTML("<i>⚠️ Please enter a follow-up question.</i>")
        if df.empty:
            return ui.HTML("<i>⚠️ No candidate data loaded.</i>")
        if not col1 or corr_value is None:
            return ui.HTML("<i>⚠️ Please run a correlation first.</i>")

        chat_status.set("💬 Thinking...")

        # Provide full data context for Gemini: 10 rows, all columns
        cleaned_df = df.drop(columns=["Resume File", "Llama Summary", "Gemini Summary"], errors="ignore")
        sample_json = json.dumps(cleaned_df.head(10).to_dict(orient="records"), indent=2)

        prompt = (
            f"You are helping a recruiter analyze candidate data.\n\n"
            f"The last Pearson correlation was between '{col1}' and '{col2}' = {corr_value:.4f}.\n"
            f"The user asked: \"{user_msg}\"\n\n"
            f"Here is a preview of the first 10 rows of the dataset:\n{sample_json}\n\n"
            f"Use both the correlation and sample data to respond helpfully."
        )

        try:
            # Replicating original behavior: statless single-turn logic
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.4)
            )
            explanation = markdown.markdown(response.text.strip())
        except Exception as e:
            explanation = f"<b>❌ Gemini error:</b> {str(e)}"

        chat_status.set("")
        return ui.HTML(explanation)
