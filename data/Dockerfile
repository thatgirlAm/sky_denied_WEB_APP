FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install Chromium and ChromeDriver
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    chromium chromium-driver \
    python3-pip python3-setuptools \
    libglib2.0-0 libnss3 libgconf-2-4 libxss1 libasound2 libxtst6 libx11-xcb1 libxcb-dri3-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app
WORKDIR /app

# Expose port for FastAPI
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]