#!/bin/bash

# =============================================================================
# AUTO START SCRIPT WITH RANDOM NGROK DOMAIN
# =============================================================================
# Script này tự động:
# 1. Start Docker Compose
# 2. Start Ngrok (random domain)
# 3. Detect ngrok URL
# 4. Update config files
# 5. Rebuild services
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN} BSport System - Auto Start with Random Ngrok${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED} Error: Ngrok is not installed${NC}"
    echo ""
    echo "Please install ngrok first:"
    echo "  macOS: brew install ngrok/ngrok/ngrok"
    echo "  Linux: See https://ngrok.com/download"
    exit 1
fi

# Check if Docker is running
echo -e "${YELLOW} Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED} Error: Docker is not running${NC}"
    echo ""
    echo "Please start Docker Desktop first"
    exit 1
fi
echo -e "${GREEN} Docker is running${NC}"
echo ""

# =============================================================================
# Step 1: Start Docker Compose
# =============================================================================
echo -e "${YELLOW} Starting Docker Compose services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${YELLOW} Waiting for services to be ready...${NC}"
sleep 5

echo -e "${GREEN} Docker services started${NC}"
echo ""

# =============================================================================
# Step 2: Start Ngrok in background
# =============================================================================
echo -e "${YELLOW} Starting Ngrok tunnel...${NC}"

# Kill any existing ngrok process
pkill -f ngrok || true

# Start ngrok in background with log file
ngrok http 80 --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

echo -e "${BLUE}Ngrok PID: ${NGROK_PID}${NC}"
echo -e "${YELLOW} Waiting for ngrok to initialize...${NC}"
sleep 5

# =============================================================================
# Step 3: Get Ngrok URL from API
# =============================================================================
echo -e "${YELLOW} Detecting Ngrok URL...${NC}"

MAX_RETRIES=10
RETRY_COUNT=0
NGROK_URL=""

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    # Try to get URL from ngrok API
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o 'https://[^"]*ngrok-free.dev' | head -1 || true)
    
    if [ -n "$NGROK_URL" ]; then
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}  Retry ${RETRY_COUNT}/${MAX_RETRIES}...${NC}"
    sleep 2
done

if [ -z "$NGROK_URL" ]; then
    echo -e "${RED} Error: Failed to detect Ngrok URL${NC}"
    echo ""
    echo "Please check:"
    echo "  1. Ngrok is running: ps aux | grep ngrok"
    echo "  2. Ngrok API is accessible: curl http://localhost:4040/api/tunnels"
    echo "  3. Check ngrok logs: cat /tmp/ngrok.log"
    exit 1
fi

echo -e "${GREEN} Detected Ngrok URL: ${BLUE}${NGROK_URL}${NC}"
echo ""

# =============================================================================
# Step 4: Update Config Files
# =============================================================================
echo -e "${YELLOW} Updating configuration files...${NC}"

if [ ! -f "./update_ngrok_url.sh" ]; then
    echo -e "${RED} Error: update_ngrok_url.sh not found${NC}"
    exit 1
fi

# Make sure script is executable
chmod +x ./update_ngrok_url.sh

# Update config (without prompting for rebuild)
./update_ngrok_url.sh "$NGROK_URL" << EOF
n
EOF

echo -e "${GREEN} Configuration updated${NC}"
echo ""

# =============================================================================
# Step 5: Rebuild Services
# =============================================================================
echo -e "${YELLOW} Rebuilding services to apply new config...${NC}"

# Option 1: Restart only necessary services (faster)
docker-compose restart billing_api nginx

# Wait for services to restart
sleep 3

echo -e "${GREEN} Services restarted${NC}"
echo ""

# =============================================================================
# Step 6: Verify Everything
# =============================================================================
echo -e "${YELLOW} Verifying system...${NC}"

# Check if services are up
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED} Warning: Some services may not be running${NC}"
fi

# Test health endpoint
echo -e "${YELLOW}  Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${NGROK_URL}/health" -H "ngrok-skip-browser-warning: true" || echo "000")

if [ "$HEALTH_RESPONSE" == "200" ]; then
    echo -e "${GREEN}   Health check passed${NC}"
else
    echo -e "${YELLOW}    Health check returned: ${HEALTH_RESPONSE}${NC}"
fi

echo ""

# =============================================================================
# Summary
# =============================================================================
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN} System is ready!${NC}"
echo ""
echo -e "${BLUE} Ngrok URL (SAVE THIS):${NC}"
echo -e "  ${GREEN}${NGROK_URL}${NC}"
echo ""
echo -e "${BLUE} Access URLs:${NC}"
echo -e "  Frontend: ${GREEN}${NGROK_URL}/ui/Homepage/homepage.html${NC}"
echo -e "  Login:    ${GREEN}${NGROK_URL}/ui/Login/Login.html${NC}"
echo -e "  Health:   ${GREEN}${NGROK_URL}/health${NC}"
echo -e "  Ngrok UI: ${GREEN}http://localhost:4040${NC}"
echo ""
echo -e "${BLUE} Docker Services:${NC}"
docker-compose ps --format "table {{.Name}}\t{{.Status}}" | head -n 10
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE} Tips:${NC}"
echo -e "  • View ngrok traffic: ${GREEN}http://localhost:4040${NC}"
echo -e "  • View logs: ${GREEN}docker-compose logs -f billing_api${NC}"
echo -e "  • Stop ngrok: ${GREEN}kill ${NGROK_PID}${NC}"
echo -e "  • Stop docker: ${GREEN}docker-compose down${NC}"
echo ""
echo -e "${YELLOW}  Important:${NC}"
echo -e "  This ngrok URL will CHANGE when you restart ngrok!"
echo -e "  For permanent URL, use static domain: ./start_with_static_ngrok.sh"
echo ""
echo -e "${GREEN}Press Enter to view ngrok logs, or Ctrl+C to continue in background${NC}"

# Wait for user input or timeout
read -t 5 || true

# Show ngrok logs
echo ""
echo -e "${BLUE} Recent Ngrok Logs:${NC}"
tail -20 /tmp/ngrok.log

echo ""
echo -e "${GREEN} Setup complete! Ngrok is running in background (PID: ${NGROK_PID})${NC}"
echo ""
