# --- Stage 1: Build & Dependencies ---
FROM python:3.10-slim AS builder

WORKDIR /install
COPY backend/requirements.txt .

# Install packages to a temporary folder
# We use --no-cache-dir to save space
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# --- Stage 2: Runtime Image ---
FROM python:3.10-slim

WORKDIR /app

# Install ONLY runtime system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy
RUN sed -i 's/policy domain="path" rights="none" pattern="@\*"/policy domain="path" rights="read|write" pattern="@\*"/g' /etc/ImageMagick*/policy.xml

# Copy the installed python packages from the builder
COPY --from=builder /install /usr/local

# Copy application files (ignoring large junk via .dockerignore)
COPY backend/ .
COPY recipes_cleaned.csv .

# Verify static/web exists
RUN mkdir -p static/web

EXPOSE 8000
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
