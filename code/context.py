import json
import os
import shutil
    
CONTEXT_PATH = "/tmp/data/context.json"

def init_context():
    if not os.path.exists("/tmp/data"):
        os.makedirs("/tmp/data")
    if not os.path.exists(CONTEXT_PATH):
        with open(CONTEXT_PATH, "w") as f:
            json.dump({"jobs": {}, "candidates": {}, 'employees': {}}, f)

def load_context():
    with open(CONTEXT_PATH, "r") as f:
        return json.load(f)

def save_job_context(job_id, job_data):
    init_context()
    context = load_context()
    context["jobs"][job_id] = job_data
    with open(CONTEXT_PATH, "w") as f:
        json.dump(context, f, indent=2)

def save_candidate_context(candidate_id, candidate_data):
    init_context()
    context = load_context()
    context["candidates"][candidate_id] = candidate_data
    with open(CONTEXT_PATH, "w") as f:
        json.dump(context, f, indent=2)

def get_job_context(job_id):
    context = load_context()
    return context["jobs"].get(job_id, {})

def get_candidate_context(candidate_id):
    context = load_context()
    return context["candidates"].get(candidate_id, {})

def get_all_jobs():
    return load_context()["jobs"]

def get_all_candidates():
    return load_context()["candidates"]

def save_employee_context(employee_id, employee_data):
    init_context()
    context = load_context()
    context["employees"][employee_id] = employee_data
    with open(CONTEXT_PATH, "w") as f:
        json.dump(context, f, indent=2)

def get_employee_context(employee_id):
    context = load_context()
    return context["employees"].get(employee_id, {})

def get_all_employees():
    return load_context()["employees"]

def clear_context():
    """Forcefully clears all saved job and candidate data in the context file."""
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(CONTEXT_PATH, "w") as f:
        json.dump({"jobs": {}, "candidates": {}, 'employees': {}}, f, indent=2)

def save_team_summary(summary_text):
    init_context()
    context = load_context()
    context["team_summary"] = summary_text
    with open(CONTEXT_PATH, "w") as f:
        json.dump(context, f, indent=2)

def get_team_summary():
    context = load_context()
    return context.get("team_summary", "")

def save_candidate_offer(candidate_id, offer_text):
    init_context()
    context = load_context()
    candidate = context["candidates"].get(candidate_id, {})
    if "onboarding_docs" not in candidate:
        candidate["onboarding_docs"] = {}
    candidate["onboarding_docs"]["offer_letter"] = offer_text
    context["candidates"][candidate_id] = candidate
    with open(CONTEXT_PATH, "w") as f:
        json.dump(context, f, indent=2)

def get_candidate_offer(candidate_id):
    context = load_context()
    return context["candidates"].get(candidate_id, {}).get("onboarding_docs", {}).get("offer_letter", "")

