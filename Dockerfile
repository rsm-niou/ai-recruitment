# Dockerfile for Weather Assistant Demo
# This file configures how the application will run on Hugging Face Spaces

# Start with Python 3.12 as our base image
# This gives us a clean Python environment to work with
FROM python:3.12

# Install UV package manager
# UV is a fast, reliable Python package installer written in Rust
# It's much faster than pip for installing dependencies
RUN pip install uv


# Copy all files from our project into the container
# This includes app.py, pyproject.toml, and other necessary files
COPY . .

# Use UV to install all dependencies specified in pyproject.toml
# This ensures we have the same packages as in local development
RUN uv sync

# Configure the container to listen on port 7860
# This is the default port that Hugging Face Spaces expects
EXPOSE 7860

# Command to run when the container starts
# This launches the Shiny app with specific host and port settings
# - host 0.0.0.0 allows connections from outside the container
# - port 7860 matches our EXPOSE setting above
CMD ["/.venv/bin/shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]