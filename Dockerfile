# Use a slim Python base image
FROM python:3.11-slim

# Set environment variables to reduce image size
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required packages
RUN pip install --no-cache-dir requests python-jenkins

# Create working directory
WORKDIR /app

# Copy your sync script into the container
COPY rancher_to_jenkins.py .

# Run the script by default when the container starts
CMD ["python", "rancher_to_jenkins.py"]
