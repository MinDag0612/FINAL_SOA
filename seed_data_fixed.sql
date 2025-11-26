-- =====================================================
-- SEED DATA FOR BADMINTON COURT MANAGEMENT SYSTEM
-- Corrected for actual database schema
-- =====================================================

-- 1. AUTH DATABASE - Users
USE DB_AUTH;

-- Insert users (customers and managers)
-- Password for all: "password123" -> bcrypt hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.

INSERT INTO User_Infor (email, password, fullname, role) VALUES
-- Managers (user_id will be 7, 8, 9 assuming existing users 1-6)
('manager1@badminton.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Nguyen Van Manager', 'manager'),
('manager2@badminton.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Tran Thi Manager', 'manager'),
('manager3@badminton.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Le Van Manager', 'manager'),

-- Customers (user_id will be 10-19)
('customer1@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Pham Van A', 'customer'),
('customer2@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Hoang Thi B', 'customer'),
('customer3@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Vu Van C', 'customer'),
('customer4@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Bui Thi D', 'customer'),
('customer5@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Dang Van E', 'customer'),
('customer6@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Ngo Thi F', 'customer'),
('customer7@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Do Van G', 'customer'),
('customer8@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Trinh Thi H', 'customer'),
('customer9@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Luong Van I', 'customer'),
('customer10@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Mai Thi J', 'customer');


-- 2. FACILITY DATABASE
USE DB_FACILITY;

-- Insert facilities
INSERT INTO Facility (user_id, name, address, sport, description, opening_hours, contact_phone, amenities, is_active) VALUES
-- Manager 1 (user_id=7) facilities
(7, 'Champions Badminton Arena', '123 Tran Hung Dao, Ha Noi', 'Badminton', 'Professional badminton center with 8 premium courts', '06:00-23:00', '0901234567', '["Parking", "Locker", "Shop", "Cafe", "Shower"]', 1),
(7, 'Victory Sports Complex', '456 Nguyen Trai, Ha Noi', 'Badminton', 'Family-friendly badminton center with 6 courts', '07:00-22:00', '0901234568', '["Parking", "Cafe", "Wifi"]', 1),

-- Manager 2 (user_id=8) facilities  
(8, 'Elite Badminton Club', '789 Le Lai, Ho Chi Minh', 'Badminton', 'High-end badminton club with 10 courts', '05:00-24:00', '0902234567', '["Parking", "VIP Room", "Spa", "Restaurant", "Shower"]', 1),
(8, 'Phoenix Sports Center', '321 Nguyen Hue, Ho Chi Minh', 'Badminton', 'Modern sports center with 7 courts', '06:00-23:00', '0902234568', '["Parking", "Shop", "Cafe"]', 1),

-- Manager 3 (user_id=9) facilities
(9, 'Dragon Badminton Hall', '555 Bach Dang, Da Nang', 'Badminton', 'Spacious badminton hall with 9 courts', '06:00-22:00', '0903234567', '["Parking", "Locker", "Cafe", "Wifi"]', 1),
(9, 'Ocean View Sports', '777 Vo Nguyen Giap, Da Nang', 'Badminton', 'Seaside badminton center with 5 courts', '07:00-21:00', '0903234568', '["Parking", "Ocean View", "Cafe"]', 1);


-- 3. COURT DATABASE
USE DB_COURT;

-- Insert courts for each facility
-- Facility 1 (facility_id=3): 8 courts
INSERT INTO Court (facility_id, name, surface_type, hourly_rate, description, available_hours, is_active) VALUES
(3, 'Court A1', 'Rubber', 150000, 'Premium court with professional lighting', '["06:00-23:00"]', 1),
(3, 'Court A2', 'Rubber', 150000, 'Premium court with air conditioning', '["06:00-23:00"]', 1),
(3, 'Court A3', 'Vinyl', 140000, 'Standard court with good ventilation', '["06:00-23:00"]', 1),
(3, 'Court A4', 'Vinyl', 140000, 'Standard court', '["06:00-23:00"]', 1),
(3, 'Court A5', 'Vinyl', 130000, 'Economy court', '["06:00-23:00"]', 1),
(3, 'Court A6', 'Vinyl', 130000, 'Economy court', '["06:00-23:00"]', 1),
(3, 'Court A7', 'Wood', 160000, 'VIP court with premium wood flooring', '["06:00-23:00"]', 1),
(3, 'Court A8', 'Wood', 160000, 'VIP court', '["06:00-23:00"]', 1),

-- Facility 2 (facility_id=4): 6 courts
(4, 'Court B1', 'Rubber', 120000, 'Family-friendly court', '["07:00-22:00"]', 1),
(4, 'Court B2', 'Rubber', 120000, 'Family-friendly court', '["07:00-22:00"]', 1),
(4, 'Court B3', 'Vinyl', 110000, 'Standard court', '["07:00-22:00"]', 1),
(4, 'Court B4', 'Vinyl', 110000, 'Standard court', '["07:00-22:00"]', 1),
(4, 'Court B5', 'Vinyl', 110000, 'Economy court', '["07:00-22:00"]', 1),
(4, 'Court B6', 'Vinyl', 110000, 'Economy court', '["07:00-22:00"]', 1),

-- Facility 3 (facility_id=5): 10 courts
(5, 'Court C1', 'Wood', 200000, 'Elite VIP court', '["05:00-24:00"]', 1),
(5, 'Court C2', 'Wood', 200000, 'Elite VIP court', '["05:00-24:00"]', 1),
(5, 'Court C3', 'Wood', 180000, 'Premium court', '["05:00-24:00"]', 1),
(5, 'Court C4', 'Wood', 180000, 'Premium court', '["05:00-24:00"]', 1),
(5, 'Court C5', 'Rubber', 160000, 'Standard court', '["05:00-24:00"]', 1),
(5, 'Court C6', 'Rubber', 160000, 'Standard court', '["05:00-24:00"]', 1),
(5, 'Court C7', 'Rubber', 160000, 'Standard court', '["05:00-24:00"]', 1),
(5, 'Court C8', 'Vinyl', 150000, 'Economy court', '["05:00-24:00"]', 1),
(5, 'Court C9', 'Vinyl', 150000, 'Economy court', '["05:00-24:00"]', 1),
(5, 'Court C10', 'Vinyl', 150000, 'Economy court', '["05:00-24:00"]', 1),

-- Facility 4 (facility_id=6): 7 courts
(6, 'Court D1', 'Rubber', 140000, 'Modern court with AC', '["06:00-23:00"]', 1),
(6, 'Court D2', 'Rubber', 140000, 'Modern court', '["06:00-23:00"]', 1),
(6, 'Court D3', 'Vinyl', 130000, 'Standard court', '["06:00-23:00"]', 1),
(6, 'Court D4', 'Vinyl', 130000, 'Standard court', '["06:00-23:00"]', 1),
(6, 'Court D5', 'Vinyl', 120000, 'Economy court', '["06:00-23:00"]', 1),
(6, 'Court D6', 'Vinyl', 120000, 'Economy court', '["06:00-23:00"]', 1),
(6, 'Court D7', 'Wood', 170000, 'VIP court', '["06:00-23:00"]', 1),

-- Facility 5 (facility_id=7): 9 courts
(7, 'Court E1', 'Rubber', 145000, 'Spacious court', '["06:00-22:00"]', 1),
(7, 'Court E2', 'Rubber', 145000, 'Spacious court', '["06:00-22:00"]', 1),
(7, 'Court E3', 'Rubber', 145000, 'Spacious court', '["06:00-22:00"]', 1),
(7, 'Court E4', 'Vinyl', 135000, 'Standard court', '["06:00-22:00"]', 1),
(7, 'Court E5', 'Vinyl', 135000, 'Standard court', '["06:00-22:00"]', 1),
(7, 'Court E6', 'Vinyl', 125000, 'Economy court', '["06:00-22:00"]', 1),
(7, 'Court E7', 'Vinyl', 125000, 'Economy court', '["06:00-22:00"]', 1),
(7, 'Court E8', 'Wood', 165000, 'VIP court', '["06:00-22:00"]', 1),
(7, 'Court E9', 'Wood', 165000, 'VIP court', '["06:00-22:00"]', 1),

-- Facility 6 (facility_id=8): 5 courts
(8, 'Court F1', 'Vinyl', 115000, 'Ocean view court', '["07:00-21:00"]', 1),
(8, 'Court F2', 'Vinyl', 115000, 'Ocean view court', '["07:00-21:00"]', 1),
(8, 'Court F3', 'Vinyl', 115000, 'Standard court', '["07:00-21:00"]', 1),
(8, 'Court F4', 'Rubber', 125000, 'Premium ocean view', '["07:00-21:00"]', 1),
(8, 'Court F5', 'Rubber', 125000, 'Premium court', '["07:00-21:00"]', 1);


-- 4. BOOKING DATABASE
USE DB_BOOKING;

-- Insert bookings with varied statuses and dates
-- Status: pending, confirmed, cancelled, completed
-- Date range: 7 days ago to 5 days future

INSERT INTO bookings (user_id, facility_id, status, total_amount, payment_status, payment_method, payment_reference, created_at) VALUES
-- Completed bookings (7-5 days ago)
(10, 3, 'completed', 300000, 'paid', 'vnpay', 'MOCK-TXN-001', DATE_SUB(NOW(), INTERVAL 7 DAY)),
(11, 3, 'completed', 280000, 'paid', 'vnpay', 'MOCK-TXN-002', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(12, 4, 'completed', 220000, 'paid', 'vnpay', 'MOCK-TXN-003', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(13, 5, 'completed', 360000, 'paid', 'vnpay', 'MOCK-TXN-004', DATE_SUB(NOW(), INTERVAL 5 DAY)),
(14, 5, 'completed', 400000, 'paid', 'vnpay', 'MOCK-TXN-005', DATE_SUB(NOW(), INTERVAL 5 DAY)),

-- Confirmed bookings (yesterday and today)
(15, 6, 'confirmed', 280000, 'paid', 'vnpay', 'MOCK-TXN-006', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(16, 7, 'confirmed', 290000, 'paid', 'vnpay', 'MOCK-TXN-007', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(17, 8, 'confirmed', 250000, 'paid', 'vnpay', 'MOCK-TXN-008', NOW()),
(18, 3, 'confirmed', 300000, 'paid', 'vnpay', 'MOCK-TXN-009', NOW()),

-- Pending bookings (tomorrow to 5 days future)
(19, 4, 'pending', 220000, 'unpaid', NULL, NULL, NOW()),
(10, 5, 'pending', 320000, 'unpaid', NULL, NULL, NOW()),
(11, 6, 'pending', 260000, 'unpaid', NULL, NULL, NOW()),

-- Cancelled bookings
(12, 3, 'cancelled', 150000, 'refunded', 'vnpay', 'MOCK-TXN-010', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(13, 4, 'cancelled', 110000, 'cancelled', NULL, NULL, DATE_SUB(NOW(), INTERVAL 2 DAY));

-- Insert booking_items (linking bookings to courts with time slots)
-- Booking 1: 2 hours at Court A1
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(1, 3, DATE_ADD(DATE_SUB(NOW(), INTERVAL 7 DAY), INTERVAL 14 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 7 DAY), INTERVAL 16 HOUR), 300000);

-- Booking 2: 2 hours at Court A3
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(2, 5, DATE_ADD(DATE_SUB(NOW(), INTERVAL 6 DAY), INTERVAL 15 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 6 DAY), INTERVAL 17 HOUR), 280000);

-- Booking 3: 2 hours at Court B1
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(3, 11, DATE_ADD(DATE_SUB(NOW(), INTERVAL 6 DAY), INTERVAL 18 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 6 DAY), INTERVAL 20 HOUR), 220000);

-- Booking 4: 2 hours at Court C1
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(4, 17, DATE_ADD(DATE_SUB(NOW(), INTERVAL 5 DAY), INTERVAL 16 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 5 DAY), INTERVAL 18 HOUR), 360000);

-- Booking 5: 2 hours at Court C2
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(5, 18, DATE_ADD(DATE_SUB(NOW(), INTERVAL 5 DAY), INTERVAL 19 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 5 DAY), INTERVAL 21 HOUR), 400000);

-- Booking 6: 2 hours at Court D1
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(6, 27, DATE_ADD(DATE_SUB(NOW(), INTERVAL 1 DAY), INTERVAL 17 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 1 DAY), INTERVAL 19 HOUR), 280000);

-- Booking 7: 2 hours at Court E1
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(7, 34, DATE_ADD(DATE_SUB(NOW(), INTERVAL 1 DAY), INTERVAL 18 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 1 DAY), INTERVAL 20 HOUR), 290000);

-- Booking 8: 2 hours at Court F1
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(8, 43, DATE_ADD(NOW(), INTERVAL 14 HOUR), DATE_ADD(NOW(), INTERVAL 16 HOUR), 250000);

-- Booking 9: 2 hours at Court A2
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(9, 4, DATE_ADD(NOW(), INTERVAL 15 HOUR), DATE_ADD(NOW(), INTERVAL 17 HOUR), 300000);

-- Booking 10: 2 hours at Court B2
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(10, 12, DATE_ADD(NOW(), INTERVAL 16 HOUR), DATE_ADD(NOW(), INTERVAL 18 HOUR), 220000);

-- Booking 11: 2 hours at Court C3
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(11, 19, DATE_ADD(NOW(), INTERVAL 17 HOUR), DATE_ADD(NOW(), INTERVAL 19 HOUR), 320000);

-- Booking 12: 2 hours at Court D2
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(12, 28, DATE_ADD(NOW(), INTERVAL 18 HOUR), DATE_ADD(NOW(), INTERVAL 20 HOUR), 260000);

-- Booking 13: 1 hour at Court A1 (cancelled)
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(13, 3, DATE_ADD(DATE_SUB(NOW(), INTERVAL 3 DAY), INTERVAL 19 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 3 DAY), INTERVAL 20 HOUR), 150000);

-- Booking 14: 1 hour at Court B1 (cancelled)
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price) VALUES
(14, 11, DATE_ADD(DATE_SUB(NOW(), INTERVAL 2 DAY), INTERVAL 20 HOUR), DATE_ADD(DATE_SUB(NOW(), INTERVAL 2 DAY), INTERVAL 21 HOUR), 110000);


-- 5. BILLING DATABASE
USE DB_BILL;

-- Insert invoices for paid bookings
INSERT INTO invoices (booking_id, user_id, amount, currency, status, payment_method, payment_reference, vnp_txn_ref, vnp_response_code, vnp_transaction_no) VALUES
-- Completed bookings
(1, 10, 300000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-001', 'MOCK-TXN-001', '00', 'VNP-14234567890'),
(2, 11, 280000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-002', 'MOCK-TXN-002', '00', 'VNP-14234567891'),
(3, 12, 220000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-003', 'MOCK-TXN-003', '00', 'VNP-14234567892'),
(4, 13, 360000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-004', 'MOCK-TXN-004', '00', 'VNP-14234567893'),
(5, 14, 400000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-005', 'MOCK-TXN-005', '00', 'VNP-14234567894'),

-- Confirmed bookings
(6, 15, 280000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-006', 'MOCK-TXN-006', '00', 'VNP-14234567895'),
(7, 16, 290000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-007', 'MOCK-TXN-007', '00', 'VNP-14234567896'),
(8, 17, 250000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-008', 'MOCK-TXN-008', '00', 'VNP-14234567897'),
(9, 18, 300000, 'VND', 'paid', 'vnpay', 'MOCK-TXN-009', 'MOCK-TXN-009', '00', 'VNP-14234567898'),

-- Cancelled booking (refunded)
(13, 12, 150000, 'VND', 'refunded', 'vnpay', 'MOCK-TXN-010', 'MOCK-TXN-010', '00', 'VNP-14234567899');


-- =====================================================
-- SEED DATA COMPLETED
-- =====================================================
-- Summary:
-- - 13 new users (3 managers, 10 customers)
-- - 6 new facilities (2 per manager)
-- - 45 new courts (8+6+10+7+9+5)
-- - 14 bookings (5 completed, 4 confirmed, 3 pending, 2 cancelled)
-- - 14 booking items (court time slots)
-- - 10 invoices (9 paid, 1 refunded)
--
-- Test Accounts:
-- Managers: manager1-3@badminton.com / password123
-- Customers: customer1-10@gmail.com / password123
-- =====================================================
