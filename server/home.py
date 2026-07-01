import uuid
from pathlib import Path
import tempfile
from shiny import reactive, ui, render
import shutil

import os
import sys
sys.path.append('code')

from context import (
    get_all_jobs,
    get_all_candidates,
    save_candidate_context,
    init_context
)

init_context()

UPLOAD_DIR = f"/tmp/data/"

def server(input, output, session):
    print("✅ Entered homepage server()")
    @output
    @render.text
    @reactive.event(input.upload_resume_btn)

    def upload_result():
        print("🚨 upload_result triggered")

        fileinfo = input.resume_file()
        job_id = input.job_id_input()
        print(f"📥 fileinfo = {fileinfo}")
        print(f"📌 job_id = {job_id}")

        if not fileinfo or not job_id:
            return "❌ Missing file or job ID."

        file_meta = fileinfo[0]
        resume_bytes = Path(file_meta["datapath"]).read_bytes()

        candidate_id = str(uuid.uuid4())
        filename = f"{candidate_id}.pdf"
        target_path = os.path.join(UPLOAD_DIR, job_id, 'resumes') 
        os.makedirs(target_path, exist_ok=True)
        
        file_path = Path(target_path) / filename
        file_path.write_bytes(resume_bytes)

        print(f"📂 Full path: {file_path.resolve()}")


        candidate_data = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "Resume File": filename,
            "Application ID": str(uuid.uuid4())
        }

        save_candidate_context(candidate_id, candidate_data)

        print(f"✅ Uploaded {file_meta['name']} → job_id: {job_id}")
        return f"✅ Resume uploaded and linked to `{job_id[:8]}`.\nCandidate ID: `{candidate_id}`"

    @reactive.effect
    def _populate_job_ids():
        all_jobs = get_all_jobs()

        chart_choices = {
            job_id: f"{job_data.get('title', 'Untitled')} ({str(job_id)[:8]})"
            for job_id, job_data in all_jobs.items()
        }

        print(f"Job IDs: {len(chart_choices)} loaded")
        ui.update_select("job_id_input", choices=chart_choices, selected=None)
