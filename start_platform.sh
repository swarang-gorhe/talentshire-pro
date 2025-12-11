#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  TALENTSHIRE PLATFORM STARTUP${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Stop any existing processes
echo -e "${YELLOW}⏹  Stopping existing services...${NC}"
pkill -9 -f "uvicorn" 2>/dev/null || true
pkill -9 -f "vite" 2>/dev/null || true
pkill -9 -f "npm run dev" 2>/dev/null || true
sleep 2

# Clear old logs
rm -f /tmp/talentshire_backend.log /tmp/talentshire_frontend.log

echo -e "${GREEN}✓ Services stopped${NC}"
echo ""

# Start Backend
echo -e "${YELLOW}🚀 Starting Backend...${NC}"
cd /Users/swarang.gorhe/Documents/Talentshire-main
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/talentshire_backend.log 2>&1 &
BACKEND_PID=$!
sleep 3

# Verify Backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend running on port 8000 (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}✗ Backend failed to start${NC}"
    tail -20 /tmp/talentshire_backend.log
    exit 1
fi
echo ""

# Start Frontend
echo -e "${YELLOW}🚀 Starting Frontend...${NC}"
cd /Users/swarang.gorhe/Documents/Talentshire-main/frontend
nohup npm run dev > /tmp/talentshire_frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 5

# Verify Frontend
if curl -s http://localhost:8080 | grep -q "root"; then
    echo -e "${GREEN}✓ Frontend running on port 8080 (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}✗ Frontend failed to start${NC}"
    tail -20 /tmp/talentshire_frontend.log
    exit 1
fi
echo ""

# Summary
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ TALENTSHIRE PLATFORM ONLINE${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Access Points:${NC}"
echo -e "  Frontend:    ${GREEN}http://localhost:8080${NC}"
echo -e "  Backend API: ${GREEN}http://localhost:8000/api${NC}"
echo -e "  Health:      ${GREEN}http://localhost:8000/health${NC}"
echo ""
echo -e "${YELLOW}Credentials:${NC}"
echo -e "  Email:    admin@talentshire.com"
echo -e "  Password: admin123"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo -e "  Backend:  tail -f /tmp/talentshire_backend.log"
echo -e "  Frontend: tail -f /tmp/talentshire_frontend.log"
echo ""
echo -e "${YELLOW}Stop Services:${NC}"
echo -e "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
