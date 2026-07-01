from shiny import ui

ui = ui.nav_panel(
    "Correlation Explorer",

    # === Global CSS Styling ===
    ui.tags.style("""
        .chat-label {
            font-weight: bold;
            margin-top: 1em;
        }
        .response-box {
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            padding: 1em;
            border-radius: 8px;
            margin-top: 1em;
            max-height: 400px;
            overflow-y: auto;
            white-space: normal;
        }
        .markdown p {
            margin: 0.5em 0;
        }
    """),

    # === Header ===
    ui.h2("Correlation Insights from Candidate Data"),

    # === Box 1: Correlation Controls ===
    ui.card(
        ui.input_select("job_id", "Select Job ID", choices=[]),
        ui.input_select("col1", "Column 1", choices=[]),
        ui.input_select("col2", "Column 2", choices=[]),
        ui.input_action_button("calc_corr", "Calculate Correlation"),
        style="margin-bottom: 2em;"
    ),

    # === Box 2: Gemini Correlation Output ===
    ui.card(
        ui.h4("Gemini Correlation Insight"),
        ui.output_ui("correlation_output"),
        style="margin-bottom: 2em;"
    ),

    # === Box 3: Follow-up Chat and LLM Response ===
    ui.card(
        ui.h4("Ask a Follow-up Question"),
        ui.input_text("chat_input", "Your question:", placeholder="e.g. Does this apply to junior candidates?"),
        ui.input_action_button("chat_send", "Send"),
        ui.output_text("chat_status_ui"),
        ui.div(
            ui.h4("Gemini Response"),
            ui.output_ui("chat_response"),
            class_="response-box"
        ),
        style="margin-bottom: 2em;"
    ),

    # === Box 4: Candidate Table Preview ===
    ui.card(
        ui.h4("Candidate Data Preview"),
        ui.output_table("candidate_table", width="100%"),
        style="margin-bottom: 2em;"
    )
)
