FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies, including Tesseract
RUN apt-get update && \
    apt-get install -y tesseract-ocr gcc libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add Tesseract to PATH explicitly (just in case)
ENV PATH="/usr/bin:$PATH"
ENV TESSDATA_PREFIX="/usr/share/tesseract-ocr/4.00/tessdata"

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

EXPOSE 10000

CMD ["python", "app.py"]

