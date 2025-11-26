#!/bin/bash

# =============================================================================
# QUICK START SCRIPT WITH STATIC NGROK DOMAIN
# =============================================================================
# Script này tự động:
# 1. Start Docker Compose
# 2. Start Ngrok với static domain
# 3. Không cần update config vì đã config sẵn với static domain
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
#  CONFIGURATION - THAY ĐỔI NÀY THEO STATIC DOMAIN CỦA BẠN
# =============================================================================
# Lấy static domain từ: https://dashboard.ngrok.com/cloud-edge/domains
# Format: your-app-name.ngrok-free.dev
STATIC_NGROK_DOMAIN="bsport-app.ngrok-free.dev"

# =============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN} BSport System - Quick Start with Ngrok${NC}"
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

# Check if static domain is configured
if [ "$STATIC_NGROK_DOMAIN" == "bsport-app.ngrok-free.dev" ]; then
    echo -e "${YELLOW}  Warning: Using default domain${NC}"
    echo -e "${YELLOW}   Please update STATIC_NGROK_DOMAIN in this script${NC}"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${YELLOW} Using static domain: ${BLUE}https://${STATIC_NGROK_DOMAIN}${NC}"
echo ""

# =============================================================================
# Step 1: Check if Docker is running
# =============================================================================
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
# Step 2: Start Docker Compose
# =============================================================================
echo -e "${YELLOW} Starting Docker Compose services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${YELLOW} Waiting for services to be ready...${NC}"
sleep 5

# Check if services are up
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED} Error: Some services failed to start${NC}"
    echo ""
    docker-compose ps
    exit 1
fi

echo -e "${GREEN} All services are running${NC}"
echo ""

# =============================================================================
# Step 3: Verify config files
# =============================================================================
echo -e "${YELLOW} Verifying configuration...${NC}"

ENV_FILE="./Billing/core/.env"
HTML_FILE="./UI/Homepage/homepage.html"

# Check if config files have correct domain
ENV_DOMAIN=$(grep "BACKEND_PUBLIC_URL" "$ENV_FILE" | cut -d'=' -f2)
HTML_DOMAIN=$(grep "BACKEND_PUBLIC_URL" "$HTML_FILE" | grep -o "https://[^']*")

echo -e "${BLUE}Current config:${NC}"
echo -e "  .env:  ${YELLOW}${ENV_DOMAIN}${NC}"
echo -e "  HTML:  ${YELLOW}${HTML_DOMAIN}${NC}"
echo ""

if [[ "$ENV_DOMAIN" != "https://${STATIC_NGROK_DOMAIN}" ]]; then
    echo -e "${YELLOW}  Config mismatch detected!${NC}"
    echo ""
    read -p "Update config to https://${STATIC_NGROK_DOMAIN}? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${YELLOW} Updating configuration...${NC}"
        ./update_ngrok_url.sh "https://${STATIC_NGROK_DOMAIN}"
        
        echo ""
        echo -e "${YELLOW} Rebuilding services...${NC}"
        docker-compose restart billing_api nginx
        sleep 3
        
        echo -e "${GREEN} Configuration updated${NC}"
    fi
fi

# =============================================================================
# Step 4: Start Ngrok
# =============================================================================
echo ""
echo -e "${YELLOW} Starting Ngrok tunnel...${NC}"
echo -e "${BLUE}Domain: https://${STATIC_NGROK_DOMAIN}${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN} System is ready!${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo -e "   Frontend: ${GREEN}https://${STATIC_NGROK_DOMAIN}/ui/Homepage/homepage.html${NC}"
echo -e "   Login:    ${GREEN}https://${STATIC_NGROK_DOMAIN}/ui/Login/Login.html${NC}"
echo -e "   Health:   ${GREEN}https://${STATIC_NGROK_DOMAIN}/health${NC}"
echo -e "   Ngrok UI: ${GREEN}http://localhost:4040${NC}"
echo ""
echo -e "${BLUE}Docker Services:${NC}"
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" | head -n 10
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop Ngrok (Docker will keep running)${NC}"
echo -e "${YELLOW}To stop everything: docker-compose down${NC}"
echo ""

# Start ngrok (foreground - will block until Ctrl+C)
ngrok http 80 --domain="${STATIC_NGROK_DOMAIN}"
