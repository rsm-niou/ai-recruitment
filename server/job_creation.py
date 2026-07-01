from shiny import reactive, render, ui
import uuid
import os
import markdown
from llm_connect import get_response
from context import save_job_context
import json

# ✅ Global reactive cache shared across handlers
response_cache = reactive.Value("")


def call_chatbot(user_input: str, session_id: str) -> str:
    prompt = (
        "You are an intelligent recruiting assistant.\n"
        "If the user asks to generate a job description, do so with sections:\n"
        "- About the Role\n- Responsibilities\n- Required Skills\n"
        "- Preferred Qualifications\n- Company Culture Highlights\n"
        "- Salary and Visa Requirements\n\n"
        "If the user asks anything else, just respond helpfully.\n\n"
        f"User: {user_input}"
    )
    return get_response(input=prompt, template=lambda x: x, llm="llama", md=False, temperature=0.9, max_tokens=1000).strip()


def extract_job_metadata(job_description: str) -> dict:
    prompt = f"""
You are a structured data extraction assistant. 
Given a job description, extract these 3 fields:

1. "job_title": (string) The job title.
2. "specialization": (string) The domain or technical area, like 'Data Science', 'Finance', or 'Healthcare'.
3. "years_required": (integer or null) Minimum years of experience mentioned. If not present, return null.

Respond in EXACTLY this JSON format:

{{
  "job_title": "...",
  "specialization": "...",
  "years_required": ...
}}

Job Description:
\"\"\"{job_description}\"\"\"
"""
    response = get_response(
        input=prompt,
        template=lambda x: x,
        llm="llama",
        md=False,
        temperature=0.2,
        max_tokens=200
    )

    try:
        return json.loads(response)
    except Exception as e:
        print(f"⚠️ Failed to parse metadata response: {e}")
        return {
            "job_title": None,
            "specialization": None,
            "years_required": None
        }


def server(input, output, session):
    print("✅ Entered job post creation server()")
    session_id = str(uuid.uuid4())
    chat_status = reactive.Value("")
    save_status = reactive.Value("")

    @output
    @render.ui
    @reactive.event(input.submit_btn)
    def job_chat_response():
        user_input = input.user_input().strip()

        if not user_input:
            return ui.HTML("<i>⚠️ Please enter a prompt.</i>")

        chat_status.set("💬 Thinking...")

        try:
            raw_response = call_chatbot(user_input, session_id)
            response_cache.set(raw_response)
            html = markdown.markdown(raw_response, extensions=["extra", "sane_lists"])
        except Exception as e:
            html = f"<b>❌ Error:</b> {str(e)}"
            response_cache.set("")

        chat_status.set("")
        return ui.HTML(html)


    @reactive.effect()
    @reactive.event(input.save_job_btn)
    def save_generated_job():
        print("💥 Save button clicked")
        raw_response = response_cache.get().strip()
        if not raw_response:
            print("⚠️ No job response cached.")
            save_status.set("⚠️ No job to save.")
            return

        try:
            print("🔍 Extracting metadata from response...")
            metadata = extract_job_metadata(raw_response)
            print("✅ Metadata extracted:")
            print(json.dumps(metadata, indent=2))

            job_id = str(uuid.uuid4())
            job_data = {
                "job_id": job_id,
                "title": metadata.get("job_title") or "Untitled",
                "specialization": metadata.get("specialization") or "General",
                "years_required": metadata.get("years_required"),
                "job_description": raw_response
            }

            save_job_context(job_id, job_data)
            save_status.set(f"✅ Job saved: {job_data['title']}")
            print(f"✅ Job saved to context: {job_id}")

        except Exception as e:
            error_msg = f"❌ Failed to save job: {e}"
            print(error_msg)
            save_status.set(error_msg)

    @output(id="save_status_ui")
    @render.text
    def render_save_status():
        return save_status.get()
