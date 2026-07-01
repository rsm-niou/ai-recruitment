from shiny import ui

document_creation_ui = ui.nav_panel(
    "Document Creation",
    ui.h2("Generate Offer Letter or Contract"),

    ui.layout_columns(
        # LEFT COLUMN — Form inputs
        ui.card(
            ui.input_select("job_dropdown_doc", "Select Job ID", choices=[]),
            ui.input_select("candidate_dropdown_doc", "Select Resume", choices=[]),
            ui.input_text("override_compensation", "Override Compensation (optional):", placeholder="$140,000 + equity"),
            ui.input_text("override_start_date", "Override Start Date (optional):", placeholder="2025-07-01"),
            ui.input_text_area("override_notes", "Hiring Manager Notes (optional):", rows=3),
            ui.input_action_button("generate_offer", "✉️ Generate Offer Letter", class_="btn-primary"),
            ui.input_action_button("generate_contract", "📄 Generate Contract", class_="btn-secondary"),
        ),

        # RIGHT COLUMN — Results
        ui.card(
            ui.h4("Generated Offer Letter"),
            ui.div(
                ui.output_text("offer_letter_text"),
                ui.download_button("download_offer", "📥 Download Offer Letter as PDF"),
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
                    white-space: pre-wrap;
                    overflow-y: auto;
                """
            ),
            ui.hr(),
            ui.h4("Generated Contract"),
            ui.div(
                ui.output_text("contract_text"),
                ui.download_button("download_contract", "📥 Download Contract as PDF"),
                style="""
                    border: 1px solid #ccc;
                    padding: 1.5em;
                    border-radius: 8px;
                    background-color: #f1f1f1;
                    min-height: 200px;
                    font-size: 1rem;
                    line-height: 1.6;
                    max-width: 900px;
                    margin-top: 1em;
                    white-space: pre-wrap;
                    overflow-y: auto;
                """
            )
        ),
        col_widths=(5, 7)
    )
)
