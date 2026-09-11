#!/bin/bash
set -e

echo "🚀 Starting Phishing Detection System..."

# 1. Open Docker Desktop and wait for it to be ready
echo "⏳ Starting Docker Desktop..."
open -a Docker
until docker info > /dev/null 2>&1; do
  echo "   Waiting for Docker daemon..."
  sleep 2
done
echo "✅ Docker is running"

# 2. Free port 8000 if any stale process is holding it
echo "🧹 Freeing port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 1

# 3. Start all containers
echo "🐳 Starting containers..."
docker compose up -d

# 4. Wait for frontend to be healthy
echo "⏳ Waiting for frontend to be ready..."
for i in {1..20}; do
  if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "✅ Frontend is up at http://localhost:3000"
    break
  fi
  sleep 2
  echo "   ($i) Still starting..."
done

# 5. Check backend
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
  echo "✅ Backend is up at http://localhost:8000"
fi

echo ""
echo "🎉 All services running!"
echo "  📱 Frontend:  http://localhost:3000"
echo "  ⚙️  Backend:   http://localhost:8000/docs"
echo "  🗄️  MongoDB:   localhost:27017"
