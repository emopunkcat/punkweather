# 1. Start with a lean, official Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy only the requirements file first to leverage Docker's cache
COPY requirements.txt .

# 4. Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application's code into the container
COPY . .

# 6. Copy and make the entrypoint script executable
COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh

# 7. Set the entrypoint script as the command to run when the container starts
ENTRYPOINT ["./entrypoint.sh"]