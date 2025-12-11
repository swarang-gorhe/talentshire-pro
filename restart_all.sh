#!/bin/bash
set -e

echo "🛑 Stopping all services..."
pkill -9 -f "uvicorn" 2>/dev/null || true
pkill -9 -f "vite" 2>/dev/null || true
pkill -9 -f "npm" 2>/dev/null || true
sleep 3

echo "🧹 Clearing logs..."
rm -f /tmp/backend_*.log /tmp/frontend_*.log

echo ""
echo "🚀 Starting services..."
echo ""

# Start local backend
cd /Users/swarang.gorhe/Documents/Talentshire-main
echo "✓ Starting backend on port 8000..."
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend_live.log 2>&1 &
BACKEND_PID=$!
sleep 3

# Start frontend  
cd /Users/swarang.gorhe/Documents/Talentshire-main/frontend
echo "✓ Starting frontend on port 8080..."
nohup npm run dev > /tmp/frontend_live.log 2>&1 &
FRONTEND_PID=$!
sleep 5

echo ""
echo "🔍 Testing services..."
echo ""

# Test backend
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend ONLINE (port 8000)"
else
    echo "❌ Backend FAILED"
    echo "Last 20 lines of backend log:"
    tail -20 /tmp/backend_live.log
fi

# Test frontend
if curl -s -f http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ Frontend ONLINE (port 8080)"
else
    echo "❌ Frontend FAILED"
    echo "Last 20 lines of frontend log:"
    tail -20 /tmp/frontend_live.log
fi

echo ""
echo "📊 Docker containers status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "═══════════════════════════════════════"
echo "  TALENTSHIRE PLATFORM"
echo "═══════════════════════════════════════"
echo "  Frontend:  http://localhost:8080"
echo "  Backend:   http://localhost:8000/api"
echo "  Health:    http://localhost:8000/health"
echo ""
echo "  PIDs: Backend=$BACKEND_PID Frontend=$FRONTEND_PID"
echo ""
echo "  View logs:"
echo "    tail -f /tmp/backend_live.log"
echo "    tail -f /tmp/frontend_live.log"
echo "═══════════════════════════════════════"
echo ""
