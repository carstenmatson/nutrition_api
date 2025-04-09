FROM python:3.10-slim

# Set environment variables to avoid interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /app

# Install system dependencies including Tesseract
RUN apt-get update && \
    apt-get install -y tesseract-ocr gcc libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all remaining app files
COPY . .

# Expose the port your app runs on
EXPOSE 10000

# Command to run the app
CMD ["python", "app.py"]
