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

# 6. The command to run your application
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:3000", "--preload", "app:app"]