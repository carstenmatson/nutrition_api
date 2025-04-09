FROM python:3.10-slim

# Avoids interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install tesseract and its language data
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        gcc \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libleptonica-dev && \
    ln -s /usr/bin/tesseract /usr/local/bin/tesseract && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Explicitly add Tesseract to path and set TESSDATA prefix
ENV PATH="/usr/bin:$PATH"
ENV TESSDATA_PREFIX="/usr/share/tesseract-ocr/4.00/tessdata"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port
EXPOSE 10000

# Run the app
CMD ["python", "app.py"]


