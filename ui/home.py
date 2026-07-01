from shiny import ui

ui = ui.nav_panel(
    'Home',
    # Top welcome content
    ui.card(
        ui.h2("Welcome to the AI Recruitment Hub"),
        ui.p("This dashboard helps you manage candidate evaluations, visualize trends, and generate documentation with LLMs."),
        ui.tags.ul(
            ui.tags.li("📥 Upload and parse resumes"),
            ui.tags.li("🔎 Evaluate candidate fit for specific roles"),
            ui.tags.li("📊 Analyze trends across candidates"),
            ui.tags.li("🧠 Compare LLM summaries and scores"),
            ui.tags.li("📝 Generate offer letters and contracts")
        ),
        ui.hr(),
        ui.p("Use the navigation bar above to access each module."),
        width=12
    ),

    # Quick-access tool cards
    ui.layout_columns(
        ui.card(
            ui.h4("🚀 Candidate Profile Viewer"),
            ui.p("Explore individual candidate summaries and scores."),
            ui.input_action_button("go_to_candidate", "Go to Candidate Profile", class_="btn btn-primary")
        ),
        ui.card(
            ui.h4("📅 Interview Scheduler"),
            ui.p("Generate Calendly links for interviews."),
            ui.input_action_button("go_to_scheduler", "Go to Scheduler", class_="btn btn-secondary")
        ),
        ui.card(
            ui.h4("📈 Chart Insights"),
            ui.p("Plot correlations and visualize trends."),
            ui.input_action_button("go_to_charts", "Go to Charting", class_="btn btn-info")
        ),
        col_widths=(4, 4, 4)
    ),

    # Resume Upload Section
    ui.card(
        ui.h4("📤 Upload Resume & Link to Job"),
        ui.layout_columns(
            ui.input_file("resume_file", "Upload Resume", accept=[".pdf", ".docx"]),
            ui.input_select("job_id_input", "Select Job", choices=[]),  # To be populated by server
            col_widths=(6, 6)
        ),
        ui.div(
            ui.input_action_button("upload_resume_btn", "Upload & Link", class_="btn btn-success"),
            ui.output_text_verbatim("upload_result"),
            class_="d-flex gap-3 align-items-center mt-3"
        ),
        width=12
    ),

    # JS nav handlers
    ui.tags.script("""
        document.addEventListener('click', function(e) {
            if (e.target.id === 'go_to_candidate') {
                document.querySelector('a[data-value="Candidate Profile"]')?.click();
            }
            if (e.target.id === 'go_to_scheduler') {
                document.querySelector('a[data-value="Interview Scheduler"]')?.click();
            }
            if (e.target.id === 'go_to_charts') {
                document.querySelector('a[data-value="Chart Generation"]')?.click();
            }
        });
    """)
)
