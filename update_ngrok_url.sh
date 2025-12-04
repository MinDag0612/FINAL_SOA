#!/bin/bash

# Script to update Ngrok URL in config files
# Usage: ./update_ngrok_url.sh https://your-new-url.ngrok-free.dev

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check argument
if [ -z "$1" ]; then
    echo -e "${RED}[ERROR] Ngrok URL is required${NC}"
    echo ""
    echo "Usage: $0 https://your-ngrok-url.ngrok-free.dev"
    echo ""
    echo "Example:"
    echo "  $0 https://abc-def-ghi.ngrok-free.dev"
    exit 1
fi

NGROK_URL=$1

# Validate URL format
if [[ ! $NGROK_URL =~ ^https://.*\.ngrok-free\.dev$ ]]; then
    echo -e "${RED}[ERROR] Invalid ngrok URL format${NC}"
    echo ""
    echo "Expected format: https://xxx-yyy-zzz.ngrok-free.dev"
    echo "Got: $NGROK_URL"
    exit 1
fi

echo -e "${BLUE}[INFO] Updating Ngrok URL to: ${YELLOW}${NGROK_URL}${NC}"
echo ""

# File paths
ENV_FILE="./Billing/core/.env"
HTML_FILE="./UI/Homepage/homepage.html"

# Check if files exist
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}[ERROR] File not found: ${ENV_FILE}${NC}"
    exit 1
fi

if [ ! -f "$HTML_FILE" ]; then
    echo -e "${RED}[ERROR] File not found: ${HTML_FILE}${NC}"
    exit 1
fi

# Backup files
echo -e "${YELLOW}[BACKUP] Creating backups...${NC}"
cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$HTML_FILE" "${HTML_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}[OK] Backups created${NC}"
echo ""

# Update .env file
echo -e "${YELLOW}[UPDATE] Updating ${ENV_FILE}...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|BACKEND_PUBLIC_URL=.*|BACKEND_PUBLIC_URL=${NGROK_URL}|" "$ENV_FILE"
else
    # Linux
    sed -i "s|BACKEND_PUBLIC_URL=.*|BACKEND_PUBLIC_URL=${NGROK_URL}|" "$ENV_FILE"
fi
echo -e "${GREEN}[OK] Updated ${ENV_FILE}${NC}"
echo ""

# Update HTML file
echo -e "${YELLOW}[UPDATE] Updating ${HTML_FILE}...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|BACKEND_PUBLIC_URL: '.*'|BACKEND_PUBLIC_URL: '${NGROK_URL}'|" "$HTML_FILE"
else
    # Linux
    sed -i "s|BACKEND_PUBLIC_URL: '.*'|BACKEND_PUBLIC_URL: '${NGROK_URL}'|" "$HTML_FILE"
fi
echo -e "${GREEN}[OK] Updated ${HTML_FILE}${NC}"
echo ""

# Verify changes
echo -e "${YELLOW}[VERIFY] Verifying changes...${NC}"
echo ""
echo -e "${BLUE}In ${ENV_FILE}:${NC}"
grep "BACKEND_PUBLIC_URL" "$ENV_FILE"
echo ""
echo -e "${BLUE}In ${HTML_FILE}:${NC}"
grep "BACKEND_PUBLIC_URL" "$HTML_FILE"
echo ""

# Prompt for rebuild
echo -e "${GREEN}[SUCCESS] Ngrok URL updated successfully!${NC}"
echo ""
echo -e "${YELLOW}[NEXT STEPS]${NC}"
echo "1. Rebuild services to apply changes:"
echo "   ${BLUE}./rebuild_fixed_services.sh${NC}"
echo ""
echo "2. Or manually:"
echo "   ${BLUE}docker-compose restart billing_api nginx${NC}"
echo ""

read -p "Do you want to rebuild services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}[REBUILD] Rebuilding services...${NC}"
    if [ -f "./rebuild_fixed_services.sh" ]; then
        ./rebuild_fixed_services.sh
    else
        echo -e "${YELLOW}[INFO] rebuild_fixed_services.sh not found, using docker-compose restart${NC}"
        docker-compose restart billing_api nginx
    fi
else
    echo ""
    echo -e "${YELLOW}[WARNING] Remember to rebuild services later!${NC}"
fi

echo ""
echo -e "${GREEN}[DONE] Update complete!${NC}"
