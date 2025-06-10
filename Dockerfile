# Use the official Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy application files
COPY . .

# COPY Env file
COPY .env .env

# Install uv tool and dependencies
RUN pip install --no-cache-dir uv && \
    uv pip install --requirement pyproject.toml --system

# Expose FastAPI default port
EXPOSE 8000

# Set environment variables file
# Optional: if you're using `python-dotenv` or manually loading envs in code

# Use uvicorn as production server if applicable
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
