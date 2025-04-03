# Use an official Python runtime as a parent image (>= 3.10)
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project configuration and metadata files
COPY pyproject.toml ./
# COPY README.md ./ # No longer needed as we bypass the local build here

# Install only the external dependencies using uv pip install
# This avoids triggering the hatchling build for the local package
RUN uv pip install --system --no-cache "mcp[cli]>=1.6.0" "PyPDF2"

# Copy the rest of the application code into the container
COPY server.py ./
COPY mosip.pdf ./

# Expose the WebSocket port
EXPOSE 8080

# Command to run the application - server.py now handles the WebSocket part internally
CMD ["uv", "run", "python", "server.py"] 