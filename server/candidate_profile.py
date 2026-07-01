import os
import fitz
import json
import re
from shiny import reactive, render, ui
from context import get_candidate_context, save_candidate_context, get_team_summary, get_job_context, get_all_jobs, get_all_candidates
from llm_connect import get_response
import html
import markdown


RESUME_DIR = "/tmp/data/"

def extract_text_from_pdf(filename, job_id):
    # Remove .pdf extension if it exists, we'll add it back
    if filename.endswith('.pdf'):
        filename = filename[:-4]
    
    path = os.path.join(RESUME_DIR, job_id, 'resumes', filename) + '.pdf'
    if not os.path.exists(path):
        print(f"❌ Resume not found: {path}")
        return None, None
    try:
        doc = fitz.open(path)
        return "\n".join([page.get_text() for page in doc]), path
    except Exception as e:
        print(f"❌ PDF error: {e}")
        return None, None

def parse_resume_with_llm(resume_text, job_description_text, team_profiles, team_summary):
    # Simplified prompt focusing on extraction only
    prompt = (
        f"Extract information from this resume:\n\n"
        f"{resume_text[:2000]}\n\n"  # Limit resume text to avoid token limits
        "Return ONLY this JSON format with actual values from the resume:\n"
        '{"Name": "Full Name", "Email": "email@domain.com", "Years of Experience": 5, "Key Skills": ["skill1", "skill2"], "Llama Score": 7}\n\n'
        "Rules:\n"
        "- Name: Extract the candidate's full name from the top of the resume\n"
        "- Email: Find the email address\n"
        "- Years of Experience: Count total years of work experience (integer)\n"
        "- Key Skills: List 3-5 main technical skills\n"
        f"- Llama Score: Rate 1-10 how well candidate fits this job: {job_description_text[:300]}\n\n"
        "Return ONLY the JSON object, nothing else."
    )

    response_text = get_response(
        input=prompt,
        template=lambda x: x,
        llm="llama",
        md=False,
        temperature=0.0,  # More deterministic
        max_tokens=500,  # Shorter response
    )

    print(f"📝 LLM Response: {response_text[:300]}")

    # Clean up response
    response_text = response_text.strip().replace("```json", "").replace("```", "").strip()
    
    # Try to extract JSON with better regex
    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
    if not match:
        print(f"❌ No JSON found in response: {response_text[:200]}")
        # Try to extract name manually from resume
        name_match = re.search(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', resume_text, re.MULTILINE)
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
        
        return {
            "Name": name_match.group(1) if name_match else "Unknown Candidate",
            "Email": email_match.group(0) if email_match else "no-email@example.com",
            "Years of Experience": 3,
            "Key Skills": ["General"],
            "Llama Score": 5
        }
    
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        print(f"Response text: {match.group(0)[:200]}")
        # Fallback extraction
        name_match = re.search(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', resume_text, re.MULTILINE)
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
        
        return {
            "Name": name_match.group(1) if name_match else "Unknown Candidate",
            "Email": email_match.group(0) if email_match else "no-email@example.com",
            "Years of Experience": 3,
            "Key Skills": ["General"],
            "Llama Score": 5
        }
    
    # Validate and fix fields
    if "Name" not in parsed or not parsed["Name"] or parsed["Name"] == "candidate full name":
        # Try to extract from resume
        name_match = re.search(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', resume_text, re.MULTILINE)
        parsed["Name"] = name_match.group(1) if name_match else "Unknown Candidate"
    
    if "Email" not in parsed or not parsed["Email"]:
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
        parsed["Email"] = email_match.group(0) if email_match else "no-email@example.com"
    
    if "Llama Score" not in parsed:
        parsed["Llama Score"] = 5
    
    # Convert score to int if it's a string
    if isinstance(parsed["Llama Score"], str):
        try:
            parsed["Llama Score"] = int(parsed["Llama Score"])
        except ValueError:
            parsed["Llama Score"] = 5
    
    print(f"✅ Parsed: {parsed}")
    return parsed

def review_llama_score(resume_text, job_description_text, score, team_profiles, team_summary):
    prompt = (
        f"You are evaluating a candidate for the following posting:\n\n"
        f"{job_description_text}\n\n"
        f"Resume:\n{resume_text}\n\n"
        f"Team Profiles:\n{team_profiles}\n\n"
        f"Team Summary:\n{team_summary}\n\n"
        f"Llama gave this candidate a score of {score}/10.\n"
        "What is your score (1–10)? Only return the number."
    )

    response = get_response(
        input=prompt,
        template=lambda x: x,
        llm="gemini",
        md=False,
        temperature=0.0,
        max_tokens=10,
        model_name ='gemini-3-flash-preview'
    )
    return str(response).strip() if response else "5"

def summarize_entire_resume(resume_text, job_description_text, score, team_profiles, team_summary):
    prompt = (
        f"Job Description:\n{job_description_text}\n\n"
        f"Resume:\n{resume_text}\n\n"
        f"Team Profiles:\n{team_profiles}\n\n"
        f"Team Summary:\n{team_summary}\n\n"
        f"The candidate received a score of {score}/10.\n"
        "Write a detailed, honest summary of this candidate's qualifications and fit."
    )

    return get_response(
        input=prompt,
        template=lambda x: x,
        llm="llama",
        md=False,
        temperature=0.7,
        max_tokens=500
    ).strip()

def review_llama_summary(resume_text, job_description_text, score, llama_review, team_profiles, team_summary):
    prompt = (
        f"You are reviewing this Llama summary for a candidate:\n\n"
        f"Job Description:\n{job_description_text}\n\n"
        f"Resume:\n{resume_text}\n\n"
        f"Llama Summary:\n{llama_review}\n\n"
        f"Team Profiles:\n{team_profiles}\n\n"
        f"Team Summary:\n{team_summary}\n\n"
        f"Llama scored this candidate {score}/10.\n"
        "Write your own short evaluation and state if you agree or disagree with Llama’s score."
    )

    response = get_response(
        input=prompt,
        template=lambda x: x,
        llm="gemini",
        md=False,
        temperature=0.7,
        max_tokens=2000,
        model_name='gemini-3-flash-preview'
    )
    return str(response).strip() if response else "Gemini review unavailable."

def server(input, output, session):


    @reactive.effect
    def _populate_job_dropdown():
        jobs = get_all_jobs()
        job_choices = {
            k: f"{v.get('title', 'Untitled')} ({k[:8]})"
            for k, v in jobs.items()
        }
        print(job_choices)
        ui.update_select("job_dropdown_for_doc", choices=job_choices)


    @reactive.effect
    def _populate_candidate_dropdown():
        job_id = input.job_dropdown_for_doc()
        print("📎 selected job_id:", job_id)

        if not job_id:
            ui.update_select("candidate_dropdown_for_doc", choices={"⬅️ Select a job first": ""})
            return

        candidates = get_all_candidates()

        filtered = {
            cid: f"{v.get('Name', cid)} ({v.get('Resume File', 'N/A')})"
            for cid, v in candidates.items()
            if str(v.get("job_id")) == str(job_id) and v.get("Resume File")
        }

        print(f"✅ Found {len(filtered)} candidates for job {job_id}")

        if filtered:
            ui.update_select("candidate_dropdown_for_doc", choices=filtered)
        else:
            ui.update_select("candidate_dropdown_for_doc", choices={"❌ No matching resumes": ""})




    @output
    @render.ui
    def summary():
        input.show_gemini()             # ✅ force reactive trigger
        input.job_dropdown_for_doc()
        input.candidate_dropdown_for_doc()

        filename = input.candidate_dropdown_for_doc()
        job_id = input.job_dropdown_for_doc()  # 🔧 ADD THIS LINE
        use_gemini = input.show_gemini() 

        if not filename or not job_id:
            return "Please select both resume and job ID."

        job_context = get_job_context(job_id)  # ✅ This now works
        job_description_text = job_context.get("job_description", "No job description available.")
        team_profiles = job_context.get("team_profiles", "No team profile available.")
        team_summary = get_team_summary()

        candidate_id = os.path.splitext(filename)[0]
        ctx = get_candidate_context(candidate_id)


        # ✅ If already evaluated for this job, return cached summary
        if ctx.get("job_id") == job_id and "Llama Summary" in ctx:
            use_gemini = input.show_gemini()
            print(f"🧪 Cached summary found for {candidate_id} / job {job_id} | Gemini: {use_gemini}")

            if 'Note' not in ctx.keys():
                ctx['Note'] = ''
                save_candidate_context(candidate_id, ctx)

            # If user wants Gemini but we don't have it yet, generate it now
            if use_gemini and "Gemini Summary" not in ctx:
                print("🔄 Generating Gemini review on demand...")
                resume_text, _ = extract_text_from_pdf(filename, job_id)
                if resume_text:
                    try:
                        llama_score = ctx.get("Llama Score", 5)
                        llama_summary = ctx.get("Llama Summary", "")
                        
                        gemini_score = review_llama_score(resume_text, job_description_text, llama_score, team_profiles, team_summary)
                        try:
                            gemini_score = int(gemini_score)
                        except:
                            gemini_score = None
                        
                        gemini_review = review_llama_summary(resume_text, job_description_text, llama_score, llama_summary, team_profiles, team_summary)
                        
                        # Update context with Gemini results
                        ctx["Gemini Score"] = gemini_score
                        ctx["Gemini Summary"] = gemini_review
                        
                        # Update avg_score
                        if isinstance(llama_score, int) and isinstance(gemini_score, int):
                            ctx["avg_score"] = (llama_score + gemini_score) / 2
                        
                        save_candidate_context(candidate_id, ctx)
                    except Exception as e:
                        print(f"❌ Gemini generation failed: {e}")
                        # Fall back to Llama summary
                        use_gemini = False

            raw = ctx.get("Gemini Summary" if use_gemini else "Llama Summary", "No summary available")
            rendered = markdown.markdown(raw.strip())

            return ui.HTML(
                f"""
                <div style="
                    font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', sans-serif;
                    font-size: 1rem;
                    line-height: 1.6;
                    white-space: normal;
                    word-wrap: break-word;
                    max-width: 900px;
                ">
                    {rendered}
                </div>
                """
            )



        # ✅ Run full pipeline - ONLY LLAMA initially
        resume_text, resume_path = extract_text_from_pdf(filename, job_id)
        if not resume_text:
            return "Failed to extract resume."

        try:
            parsed = parse_resume_with_llm(resume_text, job_description_text, team_profiles, team_summary)
        except Exception as e:
            return f"❌ LLM field extraction failed: {e}"

        if "Llama Score" not in parsed:
            return f"❌ LLM did not return a score. Please try again."
        
        llama_score = parsed["Llama Score"]
        llama_summary = summarize_entire_resume(resume_text, job_description_text, llama_score, team_profiles, team_summary)

        # ✅ Save Llama results first (no Gemini yet)
        ctx.update({
            "job_id": job_id,
            "Resume File": filename,
            "Name": parsed.get("Name"),
            "Email": parsed.get("Email"),
            "Years of Experience": parsed.get("Years of Experience"),
            "Key Skills": parsed.get("Key Skills", []),
            "Llama Score": llama_score,
            "avg_score": llama_score,  # Initially just use Llama score
            "Llama Summary": llama_summary,
            "Note": ""
        })

        save_candidate_context(candidate_id, ctx)

        # Return Llama summary
        rendered = markdown.markdown(llama_summary)

        return ui.HTML(f"""
            <div style="
                font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', sans-serif;
                font-size: 1rem;
                line-height: 1.6;
                white-space: normal;
                word-wrap: break-word;
                max-width: 900px;
            ">
                {rendered}
            </div>
        """)

    
    @output
    @render.ui
    def score():
        filename = input.candidate_dropdown_for_doc()
        job_id = input.job_dropdown_for_doc()

        if not filename or not job_id:
            return ui.HTML("<p style='color: #888;'>Select a resume and job to view score.</p>")

        candidate_id = os.path.splitext(filename)[0]
        ctx = get_candidate_context(candidate_id)

        if ctx.get("job_id") == str(job_id) and "avg_score" in ctx:
            score = ctx["avg_score"]

            # Choose a color based on the score
            if isinstance(score, (int, float)):
                color = (
                    "green" if score >= 8 else
                    "orange" if score >= 5 else
                    "red"
                )
            else:
                color = "gray"

            return ui.HTML(f"""
                <div style="
                    background-color: {color};
                    color: white;
                    font-weight: bold;
                    font-size: 1.1rem;
                    padding: 0.6rem 1.2rem;
                    border-radius: 8px;
                    display: inline-block;
                ">
                    Average Score: {score}
                </div>
            """)

        return ui.HTML("<p style='color: #888;'>Score not available. Generate profile first.</p>")

    
    @output
    @render.text
    def candidate_note_ui():
        filename = input.candidate_dropdown_for_doc()
        job_id = input.job_dropdown_for_doc()
        if not filename or not job_id:
            return ui.input_text_area("candidate_note", "Add a note:", rows=3)

        candidate_id = os.path.splitext(filename)[0]
        ctx = get_candidate_context(candidate_id)
        note = ctx.get("Note", "") if ctx.get("job_id") == job_id else ""
        return ui.input_text_area("candidate_note", "Add a note:", value=note, rows=3)

    @output
    @render.ui
    def candidate_tags_ui():
        filename = input.candidate_dropdown_for_doc()
        job_id = input.job_dropdown_for_doc()
        if not filename or not job_id:
            return ui.input_text("candidate_tags", "Tags (comma-separated):")

        candidate_id = os.path.splitext(filename)[0]
        ctx = get_candidate_context(candidate_id)
        tags = ", ".join(ctx.get("Tags", [])) if ctx.get("job_id") == job_id else ""
        return ui.input_text("candidate_tags", "Tags (comma-separated):", value=tags)


    @output
    @render.text
    def note_preview():
        filename = input.candidate_dropdown_for_doc()
        job_id = input.job_dropdown_for_doc()
        if not filename or not job_id:
            return ""

        candidate_id = os.path.splitext(filename)[0]
        ctx = get_candidate_context(candidate_id)

        if ctx.get("job_id") != job_id:
            return ""

        note = ctx.get("Note", "[No note]")
        tags = ctx.get("Tags", [])
        return f"📝 Note:\n{note}\n\n🏷️ Tags: {', '.join(tags)}"
    
    @output
    @render.text
    @reactive.event(input.save_note_tags)
    def note_tag_status():
        filename = input.candidate_dropdown_for_doc()
        job_id = input.job_dropdown_for_doc()
        if not filename or not job_id:
            return "❌ Please select both a resume and a job ID."

        candidate_id = os.path.splitext(filename)[0]
        ctx = get_candidate_context(candidate_id)

        # Only update if job_id matches
        if ctx.get("job_id") != job_id:
            return "⚠️ Cannot save notes — no profile generated for this candidate/job combination."

        # Get input
        note = input.candidate_note().strip()
        tags_raw = input.candidate_tags()
        tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]

        # Save to context
        ctx["Note"] = note
        ctx["Tags"] = tags
        save_candidate_context(candidate_id, ctx)

        return "✅ Note and tags saved."

