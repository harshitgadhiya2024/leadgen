# Use Ubuntu 20.04 as the base image
FROM ubuntu:20.04

# Set environment variable to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Update package lists and install necessary packages
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    python3-dev \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

# Install Python dependencies
RUN python3.9 -m pip install --no-cache-dir -r requirements.txt

RUN playwright install

RUN playwright install-deps

EXPOSE 8000

ENV NAME World

CMD ["python3.9", "main.py"]
