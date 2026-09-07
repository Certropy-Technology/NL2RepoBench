FROM python:3.12-slim@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /tests /logs/verifier /opt/candidate-site

# Copy requirements lock and install dependencies
COPY requirements.lock.txt /build/requirements.lock.txt
RUN pip install --no-cache-dir -r /build/requirements.lock.txt

# Install pytest for running tests
RUN pip install --no-cache-dir pytest==8.3.2

# Copy test suite
COPY tests.py /tests/tests.py

# Copy verifier script
COPY run.py /verifier/run.py
RUN chmod +x /verifier/run.py

# Set working directory
WORKDIR /verifier

# Verifier runs as separate process
ENTRYPOINT ["python3", "/verifier/run.py"]
