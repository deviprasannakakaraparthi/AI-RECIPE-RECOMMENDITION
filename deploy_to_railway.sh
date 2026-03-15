#!/bin/bash

# Configuration
FRONTEND_DIR="frontend_flutter"
BACKEND_STATIC_WEB="backend/static/web"

echo "🚀 Starting Automated Production Build..."

# 1. Build Flutter Web locally
echo "🛠️ Building Flutter Web..."
cd $FRONTEND_DIR
flutter build web --release --no-tree-shake-icons
cd ..

# 2. Sync files to backend static directory
echo "📂 Syncing files to backend..."
mkdir -p $BACKEND_STATIC_WEB
rm -rf $BACKEND_STATIC_WEB/*
cp -r $FRONTEND_DIR/build/web/* $BACKEND_STATIC_WEB/

# 3. Add, Commit and Push to GitHub
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Production update: Pre-built Flutter web UI"
git push origin main

echo "========================================================="
echo "✅ BUILD AND PUSH COMPLETE!"
echo "Railway should now start a new deployment automatically."
echo "Since we build the UI locally, it will be much faster!"
echo "========================================================="
