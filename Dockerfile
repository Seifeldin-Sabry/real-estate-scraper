# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install uv (ultra-fast Python package installer)
RUN pip install uv

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and any other necessary files
COPY pyproject.toml .

# Install dependencies using uv
RUN uv sync

# Copy the rest of the application code
COPY . .

# Run the script
CMD ["python", "real_estate_scraper.py"]