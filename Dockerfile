# --- Stage 1: Build Flutter Web ---
FROM debian:bookworm-slim AS flutter-build

RUN apt-get update && apt-get install -y \
    curl git unzip xz-utils libglu1-mesa libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Flutter
RUN git clone https://github.com/flutter/flutter.git /usr/local/flutter
ENV PATH="/usr/local/flutter/bin:/usr/local/flutter/bin/cache/dart-sdk/bin:${PATH}"
RUN flutter config --no-analytics && flutter doctor

WORKDIR /app/frontend
COPY frontend_flutter/pubspec.yaml .
RUN flutter pub get
COPY frontend_flutter/ .
RUN flutter build web --release --no-tree-shake-icons

# --- Stage 2: Python Backend ---
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for MoviePy and OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Allow ImageMagick to read/write files (policy fix)
RUN sed -i 's/policy domain="path" rights="none" pattern="@\*"/policy domain="path" rights="read|write" pattern="@\*"/g' /etc/ImageMagick-6/policy.xml

# Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ .
# Copy Dataset
COPY recipes_cleaned.csv .

# Copy built flutter app from stage 1 to backend's static/web
RUN mkdir -p static/web
COPY --from=flutter-build /app/frontend/build/web static/web

EXPOSE 8000

# Set dynamic base URL for videos if needed via env var
ENV PORT=8000

# Run with uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
