---
title: AI Recruitment Hub
emoji: 🌍
colorFrom: pink
colorTo: indigo
sdk: docker
pinned: false
license: mit
---

# AI Recruitment Hub 🌍

A modern, end-to-end AI-powered recruitment platform for job creation, candidate management, interview scheduling, analytics, and automated document generation.

---

## Project Structure

```
├── app.py                # Main Shiny app entrypoint
├── Dockerfile            # Container setup
├── pyproject.toml        # Python dependencies
├── data/                 # Source data (resumes, emails, context)
├── code/                 # Core logic (context, LLM connection)
├── server/               # Shiny server logic for each module (backend logic)
│   ├── candidate_profile.py      # Candidate profile backend logic
│   ├── correlation_analysis.py   # Correlation analysis backend logic
│   ├── document_creation.py      # Offer/contract PDF generation backend
│   ├── home.py                   # Home/dashboard backend logic
│   ├── interview_scheduler.py    # Interview scheduling backend logic
│   ├── job_creation.py           # Job creation backend logic
│   ├── plot_generation.py        # Analytics/chart backend logic
├── ui/                   # Shiny UI components for each module (frontend layout)
│   ├── candidate_profile.py      # Candidate profile UI
│   ├── chart_generation.py       # Analytics/chart UI
│   ├── correlation_analysis.py   # Correlation analysis UI
│   ├── document_creation.py      # Offer/contract UI
│   ├── home.py                   # Home/dashboard UI
│   ├── interview_scheduler.py    # Interview scheduling UI
│   ├── job_creation.py           # Job creation UI
├── static/, styles/      # Custom CSS
```

---

## End-to-End Workflow

1. **Job Creation:** Create job postings with details and requirements.
2. **Resume Upload:** Upload and parse candidate resumes, auto-link to jobs.
3. **Candidate Management:** Review, filter, and match candidates to jobs.
4. **Interview Scheduling:** Select candidates, generate LLM-powered interview emails, and send scheduling links (Calendly integration).
5. **Analytics:** Visualize candidate-job fit and correlations with interactive charts.
6. **Document Generation:** Auto-generate offer letters and contracts using LLMs, render as PDFs, and allow editing.
7. **Download & Edit:** Download, preview, and edit all generated documents.

---

## Full Pipeline

- **Data Ingestion:** Upload resumes (PDF), parse and extract candidate info.
- **Job Context:** Create and manage job postings, stored in `data/context.json`.
- **LLM Integration:** Use LLMs for drafting emails, offer letters, and contracts.
- **Scheduling:** Integrate with Calendly for interview scheduling links.
- **PDF Generation:** Render all communications and documents as PDFs, organized by job/candidate.
- **Analytics:** Generate charts and correlation plots for data-driven hiring.

---

## How to Use the App

1. **Navigate:**
   - Use the navbar to access Home, Job Creation, Candidate Profile, Interview Scheduler, Analytics, and Document Creation.
3. **Upload & Manage:**
   - Upload resumes, create jobs, and manage candidate profiles.
4. **Schedule Interviews:**
   - Select candidates, generate and send interview emails with scheduling links.
5. **Generate Documents:**
   - Create offer letters and contracts, preview and download as PDFs.
6. **Edit & Download:**
   - Edit generated documents and download the final versions.

---

## Technical Architecture

- **Frontend:** Shiny for Python (modular UI in `ui/`)
- **Backend:** Shiny server modules (`server/`), LLM integration, PDF generation
- **Data:** All context and files in `/data` and `/tmp/data` (mirrored for runtime)
- **LLM:** Uses Llama (via custom API) or Google Generative AI (Gemini) via `llm_connect.py`
- **Scheduling:** Calendly API integration
- **PDFs:** Generated with FPDF, stored per job/candidate
- **Containerization:** Docker for reproducible deployment

---

## Recently Implemented Improvements

- Robust PDF generation (handles encoding, layout, and font issues)
- Improved error handling for missing files and directories
- Modularized server and UI code for maintainability
- Hugging Face Inference API integration for Llama (no local model needed)
- Improved interview email prompts with structured output and sanitization
- Defensive Calendly API error handling with actionable error messages

---

## Deploying to Hugging Face Spaces

### Prerequisites
1. A Hugging Face account and a new Space (choose "Gradio" or "Custom" SDK)
2. Calendly Personal Access Token (or OAuth credentials)
3. Google Gemini API key (optional, for alternative LLM)
4. Hugging Face token with inference permissions

### Deployment Steps

1. **Push the repository to Hugging Face:**
   ```bash
   # Add HF remote (replace <username>/<space-name>)
   git remote add hf https://huggingface.co/spaces/<username>/<space-name>
   
   # Push code (excludes .env, local models, PII via .gitignore)
   git push hf main
   ```

2. **Configure Secrets in Space Settings:**
   - Go to your Space → Settings → Variables and secrets
   - Add the following secrets (do NOT commit these to the repo):
     ```
     CALENDLY_API_KEY=<your_calendly_personal_access_token>
     GEMINI_API_KEY=<your_gemini_api_key>
     HF_TOKEN=<your_huggingface_token>
     HF_PROVIDER=novita
     HF_MODEL=meta-llama/Llama-3.2-1B-Instruct
     ```
   - Optional OAuth secrets (if using Calendly OAuth):
     ```
     CLIENT_ID=<calendly_oauth_client_id>
     CLIENT_SECRET=<calendly_oauth_client_secret>
     WEBHOOK_SIGNING_KEY=<webhook_signing_key>
     ```

3. **Configure Space Runtime:**
   - If using Dockerfile: the Space will auto-detect `Dockerfile` and build.
   - If using Python runtime directly: ensure `pyproject.toml` or `requirements.txt` is present.
   - Set the run command (in Space settings if needed):
     ```
     python -m shiny run app.py --port 7860
     ```
     (Hugging Face Spaces typically use port 7860)

4. **Create Calendly Event Type:**
   - Log into Calendly and create at least one Event Type (e.g., One-on-one for interviews)
   - The app will auto-fetch the first available event type for scheduling links

5. **Initialize Data (optional):**
   - The app expects `/tmp/data/context.json` at runtime
   - If deploying a clean instance, the app will initialize empty context on first run
   - To pre-populate data, include sanitized sample `data/context.json` (exclude PII)

6. **Test the Deployment:**
   - Open your Space URL: `https://huggingface.co/spaces/<username>/<space-name>`
   - Navigate through the app: Job Creation → Interview Scheduler
   - Verify Calendly links are generated correctly

### Important Notes

- **Never commit `.env` or secrets** — always use HF Space Secrets
- **Exclude large files** — `Llama-3.2-1B-Instruct/` folder is ignored; the app uses HF Inference API instead
- **Exclude PII** — `data/resumes/` and `data/resumes_team/` are excluded via `.gitignore`
- **Rotate exposed secrets** — if any secrets were accidentally committed, rotate them immediately in Calendly/HF/Google
- **Port configuration** — HF Spaces typically use port 7860; adjust if needed

### Troubleshooting

- **App won't start:** Check Space logs for missing env vars or import errors
- **Calendly 401 errors:** Verify `CALENDLY_API_KEY` is set correctly in Space Secrets
- **No event types found:** Create at least one Event Type in your Calendly account
- **LLM errors:** Verify `HF_TOKEN` and `HF_MODEL` are set; check HF Inference API status

---
- Enhanced document editing and download features
- Streamlined LLM prompt engineering for better document quality

---

## PDF Generation Notes

- FPDF is used for all PDF output. Font substitution warnings (e.g., Arial → Helvetica) are normal and do not affect PDF creation.
- Only Latin-1 characters are supported in PDFs due to FPDF limitations. Unsupported characters will be replaced automatically.

---

## Troubleshooting

- **FileNotFoundError:** Ensure all required folders (e.g., `data/resumes`) exist before running.
- **PDF Generation Errors:**
  - If you see "Not enough horizontal space to render a single character", update to the latest code (handles encoding and layout).
  - Font substitution warnings (Arial → Helvetica) are safe to ignore.
  - Only Latin-1 characters are supported in PDFs; other characters will be replaced.
- **LLM/API Issues:** Check API keys in your environment and network access.

## Hugging Face Inference API (optional)

This project supports using the Hugging Face Inference API as an LLM backend without any local model conversion. To use it:

- Set your Hugging Face API token in the environment as `HF_TOKEN`.
- Optionally set `HF_MODEL` to the model id you want to call (defaults to `meta-llama/Llama-3.2-1B-Instruct`).

Example (macOS / zsh):

```bash
export HF_TOKEN="hf_..."
export HF_MODEL="meta-llama/Llama-3.2-1B-Instruct"
```

Run the quick smoke test script which will import the HF helper and, if `HF_TOKEN` is set, run a short integration call:

```bash
/Users/rachelwang/git/recruitment-ai-system/.venv/bin/python scripts/hf_smoke_test.py
```

Note: using the Inference API may incur usage costs on your Hugging Face account depending on the model called.

Tip: not all model repository ids are served via the Inference API. If you see a 404, try a commonly-hosted model such as:

- `gpt2`
- `distilgpt2`
- `google/flan-t5-small`

Or use one of the models listed on your Hugging Face account that explicitly supports Inference API usage.

Hugging Face Inference Providers (migration)
-------------------------------------------

Hugging Face deprecated the old `api-inference.huggingface.co` endpoint in 2025 in favor of the Inference Providers router. This repository's HF helper now uses the new router by default (`https://router.huggingface.co/hf-inference/`).

If you need to override the base URL (for example to point at an enterprise/private endpoint), set:

```bash
export HF_INFERENCE_API_URL="https://router.huggingface.co/hf-inference/"
```

The smoke test (`scripts/hf_smoke_test.py`) will use this base URL automatically.
- **Docker Issues:** Rebuild the image if dependencies change: `docker build --no-cache -t ai-recruitment-hub .`
- **General:** Check logs for detailed error messages and ensure all dependencies in `pyproject.toml` are installed.