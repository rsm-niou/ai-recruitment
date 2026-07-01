from shiny import ui

ui = ui.nav_panel(
    "Candidate Profile",

    ui.h2("🧑‍💼 Candidate Dashboard"),

    ui.layout_columns(

        # LEFT PANEL: Resume + Job Selection, Scores, Notes
        ui.card(
            ui.h4("🎯 Evaluation Controls"),
            ui.input_select("job_dropdown_for_doc", "Select Job", choices=[]),
            ui.input_select("candidate_dropdown_for_doc", "Select Candidate", choices=[]),

            ui.tags.hr(),
            ui.h4("📊 Score Summary"),
            ui.output_ui("score"),

            ui.tags.hr(),
            ui.h4("🗒️ Notes & Tags"),
            ui.output_ui("candidate_note_ui"),
            ui.output_ui("candidate_tags_ui"),
            ui.input_action_button("save_note_tags", "💾 Save Notes & Tags"),
            ui.output_text_verbatim("note_tag_status"),
            ui.output_text_verbatim("note_preview"),

            col_width=4
        ),
        # RIGHT PANEL: LLM Summary
        ui.card(
            ui.h4("🧠 Candidate Summary"),
            ui.div(
                ui.input_switch('show_gemini', 'Show Gemini', value=False),
                ui.output_ui("summary"),
                class_="mt-2"
            ),
            col_width=8
        )
    )
)
