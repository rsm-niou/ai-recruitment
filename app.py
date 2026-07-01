from shiny import App
from shiny.ui import page_navbar
from shiny import ui
import os

from ui import (
    home,
    interview_scheduler,
    candidate_profile,
    correlation_analysis,
    chart_generation,
    job_creation,
    document_creation  # 👈 NEW
)

from server import (
    home as home_srv,
    interview_scheduler as interview_scheduler_srv,
    candidate_profile as candidate_profile_srv,
    correlation_analysis as correlation_analysis_srv,
    job_creation as job_creation_srv,
    plot_generation as plot_generation_srv,
    document_creation as document_creation_srv  # 👈 NEW
)

ui = ui.page_fluid(
    # HEAD TAGS (global styles/fonts/scripts)
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap"
        ),
        ui.tags.link(
            rel="stylesheet",
            href="/static/custom.css"
        ),
        ui.tags.script(
            """
            document.addEventListener("DOMContentLoaded", function () {
                const navLinks = document.querySelectorAll('.nav-link');
                navLinks.forEach(link => {
                    link.addEventListener('click', function (e) {
                        // Delay default behavior to allow fade-out
                        const targetTab = this.getAttribute('data-bs-target');
                        const current = document.querySelector('.tab-pane.active');
                        if (current && targetTab && targetTab !== `#${current.id}`) {
                            current.classList.remove('active');
                            current.style.opacity = 0;

                            setTimeout(() => {
                                const next = document.querySelector(targetTab);
                                if (next) {
                                    next.classList.add('active');
                                    next.style.opacity = 1;
                                }
                            }, 150); // Match fade-out time
                            e.preventDefault();
                        }
                    });
                });
            });
            """
        )
    ),

    # MAIN NAVBAR
    ui.page_navbar(
        home.ui,
        job_creation.app_ui,
        candidate_profile.ui,
        interview_scheduler.interview_scheduler_ui,
        correlation_analysis.ui,
        chart_generation.plot_ui,
        document_creation.document_creation_ui,
        title="AI Recruitment Hub"
    )
)


def server(input, output, session):
    home_srv.server(input, output, session)
    job_creation_srv.server(input, output, session)
    candidate_profile_srv.server(input, output, session)
    interview_scheduler_srv.server(input, output, session)
    correlation_analysis_srv.server(input, output, session)
    plot_generation_srv.server(input, output, session)
    document_creation_srv.server(input, output, session)

app = App(ui, server, static_assets={'/static': os.path.join(os.path.dirname(__file__), "styles")})
