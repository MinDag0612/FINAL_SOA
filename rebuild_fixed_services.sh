#!/bin/bash

# Script tự động rebuild các services đã sửa
# Usage: ./rebuild_fixed_services.sh

set -e

echo "🚀 Bắt đầu rebuild services đã sửa lỗi..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

cd /Users/zitqan/Documents/FINAL_SOA

echo -e "${YELLOW}📦 Bước 1: Rebuild API Gateway...${NC}"
docker-compose stop apigateway
docker-compose rm -f apigateway
docker-compose build apigateway
docker-compose up -d apigateway
echo -e "${GREEN}✅ API Gateway đã rebuild${NC}"
echo ""

echo -e "${YELLOW}📦 Bước 2: Rebuild Billing Service...${NC}"
docker-compose stop billing_api
docker-compose rm -f billing_api
docker-compose build billing_api
docker-compose up -d billing_api
echo -e "${GREEN}✅ Billing Service đã rebuild${NC}"
echo ""

echo -e "${YELLOW}🔄 Bước 3: Restart Nginx...${NC}"
docker-compose restart nginx
echo -e "${GREEN}✅ Nginx đã restart${NC}"
echo ""

echo -e "${YELLOW}⏳ Đợi services khởi động (10s)...${NC}"
sleep 10
echo ""

echo -e "${GREEN}🎉 Hoàn tất! Kiểm tra trạng thái services:${NC}"
docker-compose ps | grep -E "api_gateway|billing_api|nginx"
echo ""

echo -e "${YELLOW}📋 Kiểm tra logs nếu cần:${NC}"
echo "  - API Gateway: docker-compose logs -f apigateway"
echo "  - Billing:     docker-compose logs -f billing_api"
echo "  - Nginx:       docker-compose logs -f nginx"
echo ""

echo -e "${GREEN}✨ Xong! Bây giờ có thể test lại ứng dụng.${NC}"
