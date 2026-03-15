FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Allow ImageMagick to read/write files (policy fix for video captions)
RUN sed -i 's/policy domain="path" rights="none" pattern="@\*"/policy domain="path" rights="read|write" pattern="@\*"/g' /etc/ImageMagick-6/policy.xml

# Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ .
# Copy Dataset
COPY recipes_cleaned.csv .

# We expect static/web to be populated before pushing to Railway
# This prevents the need to build Flutter inside the small Railway container
COPY backend/static/web /app/static/web

EXPOSE 8000

ENV PORT=8000

# Run with uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
