import os
from shiny import reactive, render, ui
from context import (
    get_candidate_context,
    get_job_context,
    get_team_summary,
    save_candidate_context,
    get_all_jobs,
    get_all_candidates
)
from llm_connect import get_response

from fpdf import FPDF
import markdown
import io


def draft_offer_letter(candidate_name, job_title, compensation, start_date, team_summary, job_description, hiring_manager_notes):
    prompt = (
        f"Candidate Name: {candidate_name}\n"
        f"Job Title: {job_title}\n"
        f"Compensation: {compensation}\n"
        f"Start Date: {start_date}\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Team Summary:\n{team_summary}\n\n"
        f"Hiring Manager Notes:\n{hiring_manager_notes}\n\n"
        "Write a professional, clear, and positive offer letter for this candidate. "
        "Include a summary of the role, compensation details, start date, and a warm welcome. "
        "Avoid excessive legal language but maintain formality."
    )

    return get_response(
        input=prompt,
        template=lambda x: x,
        llm="llama",
        md=False,
        temperature=0.5,
        max_tokens=600
    ).strip()


def generate_full_contract(candidate_name, job_title, compensation, start_date, clauses, company_policies, legal_notes):
    prompt = (
        f"Create a standard employment contract document.\n\n"
        f"EMPLOYEE INFORMATION:\n"
        f"Name: {candidate_name}\n"
        f"Position: {job_title}\n"
        f"Compensation: {compensation}\n"
        f"Start Date: {start_date}\n\n"
        f"CONTRACT TERMS:\n{clauses}\n\n"
        f"COMPANY POLICIES:\n{company_policies}\n\n"
        f"LEGAL NOTES:\n{legal_notes}\n\n"
        "Write a professional employment contract with these sections:\n"
        "1. EMPLOYMENT TERMS (job title, start date, reporting structure)\n"
        "2. COMPENSATION (salary, benefits, payment schedule)\n"
        "3. PROPRIETARY INFORMATION (standard confidentiality and IP assignment)\n"
        "4. TERMINATION (notice period, conditions)\n"
        "5. GENERAL PROVISIONS (governing law, dispute resolution)\n\n"
        "Use formal business language. This is a standard employment agreement template."
    )

    return get_response(
        input=prompt,
        template=lambda x: x,
        llm="llama",
        md=False,
        temperature=0.3,
        max_tokens=1500
    ).strip()


def server(input, output, session):
    print("✅ Entered document generation server()")
    # === Update job dropdown from context ===
    @reactive.effect
    def _populate_job_dropdown():
        jobs = get_all_jobs()
        # value = job_id (UUID), label = title
        job_choices = {
            k: f"{v.get('title', 'Untitled')} ({k[:8]})"
            for k, v in jobs.items()
        }
        ui.update_select("job_dropdown_doc", choices=job_choices)


    # === Update candidate dropdown based on selected job ===
    @reactive.effect
    def _populate_candidate_dropdown():
        job_id = input.job_dropdown_doc()
        print("📎 selected job_id:", job_id)

        if not job_id:
            ui.update_select("candidate_dropdown_doc", choices={"⬅️ Select a job first": ""})
            return

        candidates = get_all_candidates()

        filtered = {
            cid: f"{v.get('Name', cid)} ({v.get('Resume File', 'N/A')})"
            for cid, v in candidates.items()
            if v.get("job_id") == job_id and v.get("Resume File")
        }


        print(f"✅ Found {len(filtered)} candidates for job {job_id}")

        if filtered:
            ui.update_select("candidate_dropdown_doc", choices=filtered)
        else:
            ui.update_select("candidate_dropdown_doc", choices={"❌ No matching resumes": ""})




    # === Offer letter generation ===
    @output
    @render.text
    @reactive.event(input.generate_offer)
    def offer_letter_text():
        candidate_id = input.candidate_dropdown_doc()
        job_id = input.job_dropdown_doc()

        print("📦 candidate_id:", candidate_id)
        print("📦 job_id:", job_id)

        if not candidate_id or not job_id:
            return "❌ Select a resume and a job."

        ctx = get_candidate_context(candidate_id)
        job = get_job_context(job_id)

        print("📁 ctx loaded:", bool(ctx))
        print("📁 job loaded:", bool(job))

        if not ctx or not job:
            return "❌ Missing candidate or job context."

        comp_override = input.override_compensation().strip()
        start_override = input.override_start_date().strip()
        notes_override = input.override_notes().strip()

        offer = draft_offer_letter(
            candidate_name=ctx.get("Name", "Candidate"),
            job_title=job.get("title", "Unknown Role"),
            compensation=comp_override or job.get("compensation", "TBD"),
            start_date=start_override or job.get("start_date", "TBD"),
            team_summary=get_team_summary(),
            job_description=job.get("job_description", ""),
            hiring_manager_notes=notes_override or job.get("notes", "")
        )

        # Generate PDF with proper formatting
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        
        # Add title
        pdf.set_font("Arial", "B", size=12)
        title = f"Offer Letter - {ctx.get('Name', 'Candidate')}"
        title_encoded = title.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 10, title_encoded, ln=1, align="C")
        pdf.ln(5)
        
        # Reset font for content
        pdf.set_font("Arial", size=10)
        
        # Get effective page width
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin

        # Process each line with proper encoding
        for line in offer.split("\n"):
            if line.strip():  # Only process non-empty lines
                # Encode text to handle special characters
                encoded_line = line.encode('latin-1', 'replace')
                decoded_line = encoded_line.decode('latin-1')
                pdf.multi_cell(effective_width, 8, decoded_line)
            else:
                pdf.ln(4)  # Add spacing for empty lines

        os.makedirs(f'/tmp/data/{job_id}/offers', exist_ok=True)
        pdf_path = f'/tmp/data/{job_id}/offers/Offer_Letter_{candidate_id}.pdf'
        pdf.output(pdf_path)

        return ui.HTML(f"<pre style='font-family: Georgia; font-size: 1rem'>{offer}</pre>")

    # === Contract generation ===
    @output
    @render.text
    @reactive.event(input.generate_contract)
    def contract_text():
        candidate_id = input.candidate_dropdown_doc()
        job_id = input.job_dropdown_doc()

        if not candidate_id or not job_id:
            return "❌ Select a resume and a job."

        ctx = get_candidate_context(candidate_id)
        job = get_job_context(job_id)

        if not ctx or not job:
            return "❌ Missing candidate or job context."

        comp_override = input.override_compensation().strip()
        start_override = input.override_start_date().strip()

        contract = generate_full_contract(
            candidate_name=ctx.get("Name", "Candidate"),
            job_title=job.get("title", "Unknown Role"),
            compensation=comp_override or job.get("compensation", "TBD"),
            start_date=start_override or job.get("start_date", "TBD"),
            clauses=job.get("clauses", "Standard IP, termination, arbitration clauses."),
            company_policies=job.get("policies", "All standard company HR policies apply."),
            legal_notes=job.get("legal_notes", "Subject to U.S. labor law.")
        )

        # Generate PDF with proper formatting
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        
        # Add title
        pdf.set_font("Arial", "B", size=12)
        title = f"Employment Contract - {ctx.get('Name', 'Candidate')}"
        title_encoded = title.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 10, title_encoded, ln=1, align="C")
        pdf.ln(5)
        
        # Reset font for content
        pdf.set_font("Arial", size=10)
        
        # Get effective page width
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin

        # Process each line with proper encoding
        for line in contract.split("\n"):
            if line.strip():  # Only process non-empty lines
                # Encode text to handle special characters
                encoded_line = line.encode('latin-1', 'replace')
                decoded_line = encoded_line.decode('latin-1')
                pdf.multi_cell(effective_width, 8, decoded_line)
            else:
                pdf.ln(4)  # Add spacing for empty lines

        os.makedirs(f'/tmp/data/{job_id}/contracts', exist_ok=True)
        pdf_path = f'/tmp/data/{job_id}/contracts/Contract_{candidate_id}.pdf'
        pdf.output(pdf_path)

        return ui.HTML(f"<pre style='font-family: Georgia; font-size: 1rem'>{contract}</pre>")

    @output
    @render.download(filename="Offer_Letter.pdf")
    def download_offer():
        candidate_id = input.candidate_dropdown_doc()
        job_id = input.job_dropdown_doc()
        pdf = f'/tmp/data/{job_id}/offers/Offer_Letter_{candidate_id}.pdf'
        
        return pdf


    @output
    @render.download(filename="Contract.pdf")
    def download_contract():
        candidate_id = input.candidate_dropdown_doc()
        job_id = input.job_dropdown_doc()
        pdf = f"/tmp/data/{job_id}/contracts/Contract_{candidate_id}.pdf"
        return pdf


