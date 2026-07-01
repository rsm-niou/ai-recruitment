from shiny import ui

app_ui = ui.nav_panel(
    "Job Creation",
    ui.h2("Generate a Job Description"),

    # Box 1: Prompt Input
    ui.card(
        ui.input_text(
            "user_input",
            "Enter prompt",
            placeholder="e.g. Write a job post for a data analyst",
            width="100%"
        ),
        ui.input_action_button("submit_btn", "Submit"),
        style="margin-bottom: 2em;"
    ),

    # Box 2: LLM Response
    ui.card(
        ui.h4("LLM Response"),
        ui.output_ui("job_chat_response"),
        style="""
            padding: 1.5em;
            background-color: #f9f9f9;
            min-height: 400px;
            font-size: 1rem;
            line-height: 1.6;
            border-radius: 8px;
            border: 1px solid #ccc;
            white-space: normal;
            overflow-y: auto;
            max-width: 800px;
        """
    ),

    # Box 3: Save Job + Status
    ui.card(
        ui.input_action_button("save_job_btn", "Save Job"),
        ui.output_text("save_status_ui"),
        style="margin-top: 2em;"
    )
)
