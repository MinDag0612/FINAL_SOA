#!/bin/bash

echo "========================================"
echo "  SEEDING BOOKINGS & INVOICES"
echo "========================================"

# Seed Bookings
echo "Creating bookings..."
docker exec booking_db mysql -u root -proot -e "
USE DB_BOOKING;

INSERT INTO bookings (user_id, facility_id, status, total_amount, payment_status, payment_method, payment_reference, created_at) VALUES
-- Completed bookings (past)
(10, 3, 'completed', 300000, 'paid', 'vnpay', 'MOCK-TXN-001', DATE_SUB(NOW(), INTERVAL 7 DAY)),
(11, 3, 'completed', 280000, 'paid', 'vnpay', 'MOCK-TXN-002', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(12, 4, 'completed', 240000, 'paid', 'vnpay', 'MOCK-TXN-003', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(13, 5, 'completed', 400000, 'paid', 'vnpay', 'MOCK-TXN-004', DATE_SUB(NOW(), INTERVAL 5 DAY)),
(14, 5, 'completed', 360000, 'paid', 'vnpay', 'MOCK-TXN-005', DATE_SUB(NOW(), INTERVAL 5 DAY)),
(15, 6, 'completed', 280000, 'paid', 'vnpay', 'MOCK-TXN-006', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(16, 7, 'completed', 290000, 'paid', 'vnpay', 'MOCK-TXN-007', DATE_SUB(NOW(), INTERVAL 3 DAY)),

-- Confirmed bookings (today/yesterday)
(17, 8, 'confirmed', 250000, 'paid', 'vnpay', 'MOCK-TXN-008', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(18, 3, 'confirmed', 300000, 'paid', 'vnpay', 'MOCK-TXN-009', NOW()),
(19, 4, 'confirmed', 220000, 'paid', 'vnpay', 'MOCK-TXN-010', NOW()),

-- Pending bookings (future)
(10, 5, 'pending', 320000, 'unpaid', NULL, NULL, NOW()),
(11, 6, 'pending', 260000, 'unpaid', NULL, NULL, NOW()),

-- Cancelled
(12, 3, 'cancelled', 150000, 'refunded', 'vnpay', 'MOCK-REF-001', DATE_SUB(NOW(), INTERVAL 2 DAY));
" 2>&1 | grep -v "Warning"

echo "Creating booking items..."
docker exec booking_db mysql -u root -proot -e "
USE DB_BOOKING;

INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
-- Booking 1: 2 hours Court A1
(1, 3, DATE_ADD(DATE_SUB(NOW(), INTERVAL 7 DAY), INTERVAL 14 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 7 DAY), INTERVAL 16 HOUR), 300000),
-- Booking 2: 2 hours Court A3
(2, 5, DATE_ADD(DATE_SUB(NOW(), INTERVAL 6 DAY), INTERVAL 15 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 6 DAY), INTERVAL 17 HOUR), 280000),
-- Booking 3: 2 hours Court B1
(3, 11, DATE_ADD(DATE_SUB(NOW(), INTERVAL 6 DAY), INTERVAL 18 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 6 DAY), INTERVAL 20 HOUR), 240000),
-- Booking 4: 2 hours Court C1
(4, 21, DATE_ADD(DATE_SUB(NOW(), INTERVAL 5 DAY), INTERVAL 16 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 5 DAY), INTERVAL 18 HOUR), 400000),
-- Booking 5: 2 hours Court C3
(5, 23, DATE_ADD(DATE_SUB(NOW(), INTERVAL 5 DAY), INTERVAL 19 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 5 DAY), INTERVAL 21 HOUR), 360000),
-- Booking 6: 2 hours Court D1
(6, 31, DATE_ADD(DATE_SUB(NOW(), INTERVAL 4 DAY), INTERVAL 17 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 4 DAY), INTERVAL 19 HOUR), 280000),
-- Booking 7: 2 hours Court E1
(7, 38, DATE_ADD(DATE_SUB(NOW(), INTERVAL 3 DAY), INTERVAL 18 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 3 DAY), INTERVAL 20 HOUR), 290000),
-- Booking 8: 2 hours Court F1
(8, 56, DATE_ADD(DATE_SUB(NOW(), INTERVAL 1 DAY), INTERVAL 14 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 1 DAY), INTERVAL 16 HOUR), 250000),
-- Booking 9: 2 hours Court A2
(9, 4, DATE_ADD(NOW(), INTERVAL 15 HOUR), DATE_ADD(NOW(), INTERVAL 17 HOUR), 300000),
-- Booking 10: 2 hours Court B2
(10, 12, DATE_ADD(NOW(), INTERVAL 16 HOUR), DATE_ADD(NOW(), INTERVAL 18 HOUR), 220000),
-- Booking 11: 2 hours Court C5
(11, 25, DATE_ADD(NOW(), INTERVAL 17 HOUR), DATE_ADD(NOW(), INTERVAL 19 HOUR), 320000),
-- Booking 12: 2 hours Court D2
(12, 32, DATE_ADD(NOW(), INTERVAL 18 HOUR), DATE_ADD(NOW(), INTERVAL 20 HOUR), 260000),
-- Booking 13: 1 hour Court A1 (cancelled)
(13, 3, DATE_ADD(DATE_SUB(NOW(), INTERVAL 2 DAY), INTERVAL 19 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 2 DAY), INTERVAL 20 HOUR), 150000);
" 2>&1 | grep -v "Warning"

echo "Creating invoices..."
docker exec bill_db mysql -u root -proot -e "
USE DB_BILL;

INSERT INTO invoices (booking_id, user_id, amount, currency, status, payment_method, payment_reference, vnp_txn_ref, vnp_response_code, vnp_transaction_no) VALUES
-- Paid invoices for completed/confirmed bookings
(1, 10, 300000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-001', 'MOCK-TXN-001', '00', 'VNP-14234567890'),
(2, 11, 280000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-002', 'MOCK-TXN-002', '00', 'VNP-14234567891'),
(3, 12, 240000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-003', 'MOCK-TXN-003', '00', 'VNP-14234567892'),
(4, 13, 400000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-004', 'MOCK-TXN-004', '00', 'VNP-14234567893'),
(5, 14, 360000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-005', 'MOCK-TXN-005', '00', 'VNP-14234567894'),
(6, 15, 280000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-006', 'MOCK-TXN-006', '00', 'VNP-14234567895'),
(7, 16, 290000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-007', 'MOCK-TXN-007', '00', 'VNP-14234567896'),
(8, 17, 250000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-008', 'MOCK-TXN-008', '00', 'VNP-14234567897'),
(9, 18, 300000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-009', 'MOCK-TXN-009', '00', 'VNP-14234567898'),
(10, 19, 220000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-010', 'MOCK-TXN-010', '00', 'VNP-14234567899'),
-- Refunded invoice
(13, 12, 150000, 'VND', 'refunded', 'vnpay', 'MOCK-REF-001', 'MOCK-REF-001', '00', 'VNP-REFUND-001');
" 2>&1 | grep -v "Warning"

echo ""
echo "✅ Seeding completed!"
echo ""
echo "📊 Summary:"
docker exec booking_db mysql -u root -proot -e "SELECT COUNT(*) as total_bookings, SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed, SUM(CASE WHEN status='confirmed' THEN 1 ELSE 0 END) as confirmed, SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending, SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) as cancelled FROM DB_BOOKING.bookings WHERE user_id >= 10;" 2>&1 | grep -v "Warning"

docker exec bill_db mysql -u root -proot -e "SELECT COUNT(*) as total_invoices, SUM(amount) as total_revenue FROM DB_BILL.invoices WHERE status='paid';" 2>&1 | grep -v "Warning"
