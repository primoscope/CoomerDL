# Use Python 3.10 slim as base
FROM python:3.10-slim

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# - xvfb: Virtual Framebuffer for headless display
# - x11vnc: VNC server to expose the X11 display
# - fluxbox: Lightweight Window Manager
# - novnc & websockify: Web-based VNC viewer
# - ffmpeg: Required for media processing
# - chromium & firefox-esr: Browsers for Selenium/Playwright scrapers
# - tk: Tkinter support for the GUI
# - net-tools, procps: Utilities for supervision and debugging
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    ffmpeg \
    chromium \
    chromium-driver \
    firefox-esr \
    python3-tk \
    tk \
    curl \
    unzip \
    supervisor \
    net-tools \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables for Display
ENV DISPLAY=:0
ENV RESOLUTION=1280x800x24
ENV VNC_PASSWORD=coomerdl

# Expose ports
# 8080: Main entry (noVNC or HTTP placeholder)
# 5900: VNC server (direct)
EXPOSE 8080 5900

# Copy configuration files
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY entrypoint.sh /app/entrypoint.sh

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Define entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
