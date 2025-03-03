# Use an official Python runtime as the base image
FROM python:3.9

# Install system dependencies (ffmpeg and curl)
RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install yt-dlp
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp && \
    chmod a+rx /usr/local/bin/yt-dlp

# Verify yt-dlp installation
RUN yt-dlp --version

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create the download directory and set permissions
RUN mkdir -p /app/download && chmod 777 /app/download

# Expose the port your app runs on
EXPOSE $PORT

# Start the application using gunicorn
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:$PORT"]
