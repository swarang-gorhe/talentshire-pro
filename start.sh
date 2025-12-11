#!/bin/bash

# Kill any existing processes
pkill -9 -f "uvicorn" 2>/dev/null
pkill -9 -f "vite" 2>/dev/null
pkill -9 -f "npm run dev" 2>/dev/null
sleep 2

echo "Starting Talentshire Platform..."
echo ""

# Start Backend on port 8000
cd /Users/swarang.gorhe/Documents/Talentshire-main
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1 > /tmp/backend_run.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started on port 8000 (PID: $BACKEND_PID)"

# Start Frontend on port 8080
cd /Users/swarang.gorhe/Documents/Talentshire-main/frontend
npm run dev > /tmp/frontend_run.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started on port 8080 (PID: $FRONTEND_PID)"

echo ""
echo "Waiting for services to be ready..."
sleep 8

# Test backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is responding"
else
    echo "❌ Backend failed to start"
    tail -20 /tmp/backend_run.log
fi

# Test frontend
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ Frontend is responding"
else
    echo "❌ Frontend failed to start"
    tail -20 /tmp/frontend_run.log
fi

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║  🚀 TALENTSHIRE PLATFORM READY                        ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "  Frontend:  http://localhost:8080"
echo "  Backend:   http://localhost:8000/api"
echo "  Health:    http://localhost:8000/health"
echo ""
echo "  Login: admin@talentshire.com / admin123"
echo ""
echo "To stop services:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
