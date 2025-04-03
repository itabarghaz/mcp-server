# Use an official Python runtime as a parent image (>= 3.10)
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy the dependency specification file
COPY pyproject.toml ./

# Install project dependencies using uv into the system environment
# This leverages Docker layer caching - dependencies are only reinstalled if
# pyproject.toml changes.
RUN uv pip sync pyproject.toml --system --no-cache

# Copy the rest of the application code into the container
COPY server.py ./
COPY mosip.pdf ./

# Expose the WebSocket port
EXPOSE 8080

# Command to run the application - server.py now handles the WebSocket part internally
CMD ["uv", "run", "python", "server.py"] 