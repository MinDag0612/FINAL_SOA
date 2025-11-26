#!/bin/bash

echo "======================================"
echo "SEEDING BADMINTON MANAGEMENT SYSTEM"
echo "======================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting database seeding...${NC}"

# Wait for databases to be ready
echo "Waiting for databases to be ready..."
sleep 5

# Run seed script
echo -e "${GREEN}Running seed data SQL script...${NC}"
docker exec -i auth_db mysql -uroot -proot < seed_data.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Seed data imported successfully!${NC}"
    
    echo -e "\n${YELLOW}=== DATA SUMMARY ===${NC}"
    
    # Show statistics
    echo -e "${GREEN}Auth Database:${NC}"
    docker exec auth_db mysql -uroot -proot -D DB_AUTH -e "SELECT 'Managers' as Role, COUNT(*) as Count FROM User_Infor WHERE role='manager' UNION SELECT 'Customers' as Role, COUNT(*) as Count FROM User_Infor WHERE role='customer';" 2>/dev/null | tail -n +2
    
    echo -e "\n${GREEN}Facility Database:${NC}"
    docker exec facility_db mysql -uroot -proot -D DB_FACILITY -e "SELECT 'Total Facilities' as Info, COUNT(*) as Count FROM facilities;" 2>/dev/null | tail -n +2
    
    echo -e "\n${GREEN}Court Database:${NC}"
    docker exec court_db mysql -uroot -proot -D DB_COURT -e "SELECT 'Total Courts' as Info, COUNT(*) as Count FROM courts;" 2>/dev/null | tail -n +2
    
    echo -e "\n${GREEN}Booking Database:${NC}"
    docker exec booking_db mysql -uroot -proot -D DB_BOOKING -e "SELECT status, COUNT(*) as Count FROM bookings GROUP BY status;" 2>/dev/null | tail -n +2
    
    echo -e "\n${GREEN}Billing Database:${NC}"
    docker exec bill_db mysql -uroot -proot -D DB_BILL -e "SELECT 'Total Invoices' as Info, COUNT(*) as Count FROM invoices UNION SELECT 'Paid Invoices' as Info, COUNT(*) as Count FROM invoices WHERE status='paid';" 2>/dev/null | tail -n +2
    
    echo -e "\n${GREEN}=== TEST ACCOUNTS ===${NC}"
    echo -e "Managers:"
    echo -e "  - manager1@badminton.com / password123"
    echo -e "  - manager2@badminton.com / password123"
    echo -e "  - manager3@badminton.com / password123"
    echo -e "\nCustomers:"
    echo -e "  - customer1@gmail.com / password123"
    echo -e "  - customer2@gmail.com / password123"
    echo -e "  - customer3@gmail.com / password123"
    echo -e "  - ... (customer1-10@gmail.com)"
    echo -e "\nExisting:"
    echo -e "  - vquan29905@gmail.com / 12345 (manager)"
    
else
    echo -e "${RED}❌ Error seeding data!${NC}"
    exit 1
fi

echo -e "\n${GREEN}======================================"
echo -e "SEEDING COMPLETED!"
echo -e "======================================${NC}"
