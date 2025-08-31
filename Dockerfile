# --- Stage 1: The Builder ---
# Use the Alpine Linux variant of the Python image and name this stage 'builder'
FROM python:3.11-alpine AS builder

# Alpine Linux requires some build tools to install certain Python packages
RUN apk add --no-cache gcc musl-dev python3-dev

# Set up a virtual environment in a standard location
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies into the virtual environment
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: The Final Image ---
# Start fresh from a clean Alpine image for the final product
FROM python:3.11-alpine

# Set the working directory
WORKDIR /app

# Copy the virtual environment (with all dependencies) from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy your application code
COPY . .

# Add the virtual environment to the system's PATH
ENV PATH="/opt/venv/bin:$PATH"

# Make the entrypoint script executable (it was copied in the step above)
RUN chmod +x ./entrypoint.sh

# Set the entrypoint to run your application
ENTRYPOINT ["./entrypoint.sh"]