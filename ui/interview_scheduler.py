from shiny import ui

interview_scheduler_ui = ui.nav_panel(
    "Interview Scheduler",
    ui.h2("Generate Interview Invitations"),

    ui.layout_columns(
        # LEFT COLUMN — Input controls
        ui.card(
            ui.h4("Candidate Selection"),
            ui.output_ui("name_selector"),
            ui.input_action_button("generate_links", "✉️ Generate Interview Emails", class_="btn-primary"),
        ),

        # RIGHT COLUMN — Results and Editing
        ui.card(
            ui.h4("Generated Interview Emails"),

            # Output area for hyperlinks + status
            ui.div(
                ui.output_ui("output_links_html"),
                style="""
                    border: 1px solid #ccc;
                    padding: 1.5em;
                    border-radius: 8px;
                    background-color: #f9f9f9;
                    min-height: 200px;
                    font-size: 1rem;
                    line-height: 1.6;
                    max-width: 900px;
                    margin-top: 1em;
                    white-space: normal;
                    overflow-wrap: anywhere;
                """
            ),

            # ZIP download button
            ui.download_button("download_emails", "📥 Download All Emails as ZIP"),

            ui.hr(),
            ui.h4("PDF Preview"),
            ui.output_ui("pdf_selector"),

            ui.div(
                ui.output_ui("pdf_preview"),
                style="""
                    border: 1px solid #ccc;
                    padding: 1.5em;
                    border-radius: 8px;
                    background-color: #f1f1f1;
                    min-height: 400px;
                    max-width: 900px;
                    margin-top: 1em;
                    overflow-y: auto;
                    font-family: Georgia, serif;
                    font-size: 1rem;
                    line-height: 1.6;
                    white-space: normal;
                """
            ),

            ui.hr(),
            ui.h4("Chat to Refine Email"),
            ui.div(
                ui.input_text_area("chat_prompt", "Suggest an edit:", rows=3, placeholder="e.g. make it more concise or formal"),
                ui.input_action_button("submit_chat", "✏️ Apply Change"),
                style="margin-top: 1em;"
            ),
            ui.output_text_verbatim("refined_output"),

            ui.hr(),
            ui.h4("Edit Email"),
            ui.input_action_button("toggle_edit", "✏️ Edit This Email"),

            # ✅ Output UI that will be rendered dynamically
            ui.output_ui("edit_ui_block")
        ),
        col_widths=(5, 7)
    )
)
