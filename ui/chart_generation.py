from shiny import ui

# ✅ Define the chart tab panel ONCE
plot_ui = ui.nav_panel(
    "Chart Generation",  # tab label
    ui.h2("Visualise Trends Between Chosen Candidate Variables"),
    ui.layout_columns(
        ui.card(
            ui.input_select("chart_job_id", "Select Job ID", choices=[], selected=None),
            ui.input_select("chart_x", "X-axis variable", choices=[], selected=None),
            ui.input_select("chart_y", "Y-axis variable", choices=[], selected=None),
            ui.input_radio_buttons('chart_type', 'Chart Type', choices=['scatter', 'bar', 'line', 'histogram'], selected='scatter'),


            ui.div(
                ui.output_ui("generate_display_plot"),
                id="plot_wrapper",
                class_="plot-wrapper",
                style="padding-top: 1rem; border: 1px solid #ddd; background-color: #fff; width: 100%; overflow-x: auto;"
            ),


            ui.input_action_button("generate_plot", "Generate Chart & Explanation"),
        ),
        ui.card(
            ui.h4("LLM Explanation"),
            ui.output_ui("llm_explain_plot")
        ),
        ui.card(
            ui.h4("Ask a Follow-up Question"),
            ui.input_text_area("chart_chat_input", "Ask anything:", rows=2, width="100%"),
            ui.input_action_button("chart_chat_send", "Send"),
            ui.h4("Gemini Response"),
            ui.div(
                ui.output_ui("chat_followup"),
                style="""
                    min-height: 300px;
                    max-height: 700px;
                    overflow-y: auto;
                    resize: vertical;
                    padding: 1rem;
                    font-size: 1rem;
                    border: 1px solid #ccc;
                    background-color: #fefefe;
                    box-shadow: 0 0 4px rgba(0,0,0,0.1);
                """
            ),
            class_="response-box",
            style="""
                min-height: 600px;
                width: 100%;
            """
        ),
        col_widths=(5, 5, 5)
    )
)
