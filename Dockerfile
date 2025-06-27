FROM python:3.10-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    curl \
    unzip \
    wget \
    xvfb \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libxss1 \
    libasound2 \
    libgbm-dev \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
# ENV DISPLAY=:99
# ENV PYTHONPATH=/app
# ENV CHROME_BIN=/usr/bin/chromium
# ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Default command to run scraper
CMD ["python", "scraper_handler.py"]