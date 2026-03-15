#!/bin/bash
# deploy_temp.sh: Temporary deployment using localtunnel

# Clean up existing processes
lsof -ti:8000,8080 | xargs kill -9 2>/dev/null || true

echo "🚀 Starting backend..."
./backend/start.sh > backend.log 2>&1 &
BACKEND_PID=$!

sleep 5

echo "🔗 Starting backend tunnel..."
# Use a temporary file to capture the URL
TUNNEL_OUT=$(mktemp)
npx -y localtunnel --port 8000 > "$TUNNEL_OUT" 2>&1 &
TUNNEL_PID=$!

# Wait for URL to appear
echo "⏳ Waiting for backend URL..."
MAX_RETRIES=20
COUNT=0
BACKEND_URL=""
while [ $COUNT -lt $MAX_RETRIES ]; do
    BACKEND_URL=$(grep "your url is:" "$TUNNEL_OUT" | awk '{print $NF}')
    if [ ! -z "$BACKEND_URL" ]; then
        break
    fi
    sleep 2
    COUNT=$((COUNT+1))
done

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Failed to get backend URL. Check $TUNNEL_OUT"
    kill $BACKEND_PID $TUNNEL_PID
    exit 1
fi

echo "🌐 Backend URL: $BACKEND_URL"

# Update Flutter baseUrl
SERVICE_FILE="frontend_flutter/lib/api/api_service.dart"
if [ -f "$SERVICE_FILE" ]; then
    echo "📝 Updating Flutter API service with $BACKEND_URL ..."
    # Use sed to replace the line
    # Original: static const String baseUrl = "http://localhost:8000";
    sed -i '' "s|static const String baseUrl = .*|static const String baseUrl = \"$BACKEND_URL\";|" "$SERVICE_FILE"
else
    echo "⚠️  Could not find $SERVICE_FILE. Make sure paths are correct."
fi

echo "🛠️ Building Flutter Web..."
cd frontend_flutter
flutter build web --release
cd ..

echo "📂 Serving Web UI on port 8080..."
python3 -m http.server --directory frontend_flutter/build/web 8080 > web_server.log 2>&1 &
WEB_PID=$!

sleep 2

echo "🔗 Starting web tunnel..."
WEB_TUNNEL_OUT=$(mktemp)
npx -y localtunnel --port 8080 > "$WEB_TUNNEL_OUT" 2>&1 &
WEB_TUNNEL_PID=$!

echo "⏳ Waiting for web URL..."
COUNT=0
WEB_URL=""
while [ $COUNT -lt $MAX_RETRIES ]; do
    WEB_URL=$(grep "your url is:" "$WEB_TUNNEL_OUT" | awk '{print $NF}')
    if [ ! -z "$WEB_URL" ]; then
        break
    fi
    sleep 2
    COUNT=$((COUNT+1))
done

if [ -z "$WEB_URL" ]; then
    echo "❌ Failed to get web URL. Check $WEB_TUNNEL_OUT"
    kill $BACKEND_PID $TUNNEL_PID $WEB_PID $WEB_TUNNEL_PID
    exit 1
fi

echo ""
echo "========================================================="
echo "✅  DEPLOYMENT READY!"
echo ""
echo "📱 Share this link with your friend:"
echo "👉 $WEB_URL"
echo ""
echo "⚠️  Note: When they first open it, they might see a simple localtunnel screen."
echo "   They should click 'Click to Continue' to see your app."
echo "========================================================="
echo ""
echo "Monitoring logs... Press Ctrl+C to stop everything."

# Keep running and trap kill
trap 'echo "🛑 Stopping everything..."; kill $BACKEND_PID $TUNNEL_PID $WEB_PID $WEB_TUNNEL_PID; exit 0' INT
wait
