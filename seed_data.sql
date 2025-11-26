-- ====================
-- SEED DATA FOR BADMINTON COURT MANAGEMENT SYSTEM
-- ====================

-- 1. AUTH DATABASE - Users
USE DB_AUTH;

-- Clear existing data (careful in production!)
-- DELETE FROM User_Infor WHERE user_id > 6;

-- Insert more users (customers and managers)
INSERT INTO User_Infor (email, hashed_password, fullname, phone_number, address, role, created_at) VALUES
-- Managers
('manager1@badminton.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Nguyen Van Manager', '0901234567', 'Ha Noi', 'manager', NOW()),
('manager2@badminton.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Tran Thi Manager', '0902234567', 'Ho Chi Minh', 'manager', NOW()),
('manager3@badminton.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Le Van Manager', '0903234567', 'Da Nang', 'manager', NOW()),

-- Customers  
('customer1@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Pham Van Customer', '0911234567', 'Ha Noi', 'customer', NOW()),
('customer2@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Hoang Thi Customer', '0912234567', 'Ho Chi Minh', 'customer', NOW()),
('customer3@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Vu Van Customer', '0913234567', 'Da Nang', 'customer', NOW()),
('customer4@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Bui Thi Customer', '0914234567', 'Can Tho', 'customer', NOW()),
('customer5@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Dang Van Customer', '0915234567', 'Hai Phong', 'customer', NOW()),
('customer6@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Ngo Thi Customer', '0916234567', 'Hue', 'customer', NOW()),
('customer7@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Do Van Customer', '0917234567', 'Vinh', 'customer', NOW()),
('customer8@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Trinh Thi Customer', '0918234567', 'Quy Nhon', 'customer', NOW()),
('customer9@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Luong Van Customer', '0919234567', 'Nha Trang', 'customer', NOW()),
('customer10@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GysgJd/YZz9.', 'Mai Thi Customer', '0920234567', 'Vung Tau', 'customer', NOW());

-- Password for all: "password123"

-- 2. FACILITY DATABASE - Facilities
USE DB_FACILITY;

-- Clear existing data
-- DELETE FROM facilities WHERE facility_id > 2;

-- Insert more facilities (assigned to managers)
INSERT INTO facilities (user_id, name, address, sport, description, opening_hours, contact_phone, amenities, is_active) VALUES
-- Manager 1 facilities
(7, 'Champions Badminton Arena', '123 Tran Hung Dao, Ha Noi', 'Badminton', 'Professional badminton center with 8 premium courts', '06:00-23:00', '0901234567', '["Parking", "Locker room", "Shop", "Cafe", "Shower"]', 1),
(7, 'Victory Sports Complex', '456 Nguyen Trai, Ha Noi', 'Badminton', 'Family-friendly badminton center with 6 courts', '07:00-22:00', '0901234568', '["Parking", "Cafe", "Wifi"]', 1),

-- Manager 2 facilities  
(8, 'Elite Badminton Club', '789 Le Lai, Ho Chi Minh', 'Badminton', 'High-end badminton club with 10 courts', '05:00-24:00', '0902234567', '["Parking", "VIP Room", "Spa", "Restaurant", "Shower"]', 1),
(8, 'Phoenix Sports Center', '321 Nguyen Hue, Ho Chi Minh', 'Badminton', 'Modern sports center with 7 badminton courts', '06:00-23:00', '0902234568', '["Parking", "Shop", "Cafe"]', 1),

-- Manager 3 facilities
(9, 'Dragon Badminton Hall', '555 Bach Dang, Da Nang', 'Badminton', 'Spacious badminton hall with 9 courts', '06:00-22:00', '0903234567', '["Parking", "Locker room", "Cafe", "Wifi"]', 1),
(9, 'Ocean View Sports', '777 Vo Nguyen Giap, Da Nang', 'Badminton', 'Seaside badminton center with 5 courts', '07:00-21:00', '0903234568', '["Parking", "Ocean view", "Cafe"]', 1);


-- 3. COURT DATABASE - Courts
USE DB_COURT;

-- Clear existing data
-- DELETE FROM courts WHERE court_id > 10;

-- Insert courts for each facility
-- Facility 3 (Champions Badminton Arena) - 8 courts
INSERT INTO courts (facility_id, name, surface_type, hourly_rate, status, description) VALUES
(3, 'Court A1', 'Professional Synthetic', 150000, 'available', 'Premium court with professional lighting'),
(3, 'Court A2', 'Professional Synthetic', 150000, 'available', 'Premium court with professional lighting'),
(3, 'Court A3', 'Professional Synthetic', 150000, 'available', 'Premium court with air conditioning'),
(3, 'Court A4', 'Professional Synthetic', 150000, 'available', 'Premium court with air conditioning'),
(3, 'Court B1', 'Standard Synthetic', 120000, 'available', 'Standard court'),
(3, 'Court B2', 'Standard Synthetic', 120000, 'available', 'Standard court'),
(3, 'Court B3', 'Standard Synthetic', 120000, 'available', 'Standard court'),
(3, 'Court B4', 'Standard Synthetic', 120000, 'available', 'Standard court');

-- Facility 4 (Victory Sports Complex) - 6 courts
INSERT INTO courts (facility_id, name, surface_type, hourly_rate, status, description) VALUES
(4, 'Court 1', 'Wooden', 130000, 'available', 'Wooden floor court'),
(4, 'Court 2', 'Wooden', 130000, 'available', 'Wooden floor court'),
(4, 'Court 3', 'Synthetic', 110000, 'available', 'Synthetic floor court'),
(4, 'Court 4', 'Synthetic', 110000, 'available', 'Synthetic floor court'),
(4, 'Court 5', 'Synthetic', 110000, 'available', 'Synthetic floor court'),
(4, 'Court 6', 'Synthetic', 110000, 'available', 'Synthetic floor court');

-- Facility 5 (Elite Badminton Club) - 10 courts
INSERT INTO courts (facility_id, name, surface_type, hourly_rate, status, description) VALUES
(5, 'VIP Court 1', 'Professional Synthetic', 200000, 'available', 'VIP court with premium amenities'),
(5, 'VIP Court 2', 'Professional Synthetic', 200000, 'available', 'VIP court with premium amenities'),
(5, 'Premium Court 1', 'Professional Synthetic', 180000, 'available', 'Premium court'),
(5, 'Premium Court 2', 'Professional Synthetic', 180000, 'available', 'Premium court'),
(5, 'Premium Court 3', 'Professional Synthetic', 180000, 'available', 'Premium court'),
(5, 'Premium Court 4', 'Professional Synthetic', 180000, 'available', 'Premium court'),
(5, 'Standard Court 1', 'Synthetic', 140000, 'available', 'Standard court'),
(5, 'Standard Court 2', 'Synthetic', 140000, 'available', 'Standard court'),
(5, 'Standard Court 3', 'Synthetic', 140000, 'available', 'Standard court'),
(5, 'Standard Court 4', 'Synthetic', 140000, 'available', 'Standard court');

-- Facility 6 (Phoenix Sports Center) - 7 courts
INSERT INTO courts (facility_id, name, surface_type, hourly_rate, status, description) VALUES
(6, 'Court Alpha', 'Synthetic', 125000, 'available', 'Modern synthetic court'),
(6, 'Court Beta', 'Synthetic', 125000, 'available', 'Modern synthetic court'),
(6, 'Court Gamma', 'Synthetic', 125000, 'available', 'Modern synthetic court'),
(6, 'Court Delta', 'Synthetic', 125000, 'available', 'Modern synthetic court'),
(6, 'Court Epsilon', 'Wooden', 145000, 'available', 'Wooden court'),
(6, 'Court Zeta', 'Wooden', 145000, 'available', 'Wooden court'),
(6, 'Court Eta', 'Wooden', 145000, 'available', 'Wooden court');

-- Facility 7 (Dragon Badminton Hall) - 9 courts
INSERT INTO courts (facility_id, name, surface_type, hourly_rate, status, description) VALUES
(7, 'Dragon 1', 'Professional Synthetic', 160000, 'available', 'Premium court'),
(7, 'Dragon 2', 'Professional Synthetic', 160000, 'available', 'Premium court'),
(7, 'Dragon 3', 'Professional Synthetic', 160000, 'available', 'Premium court'),
(7, 'Dragon 4', 'Synthetic', 135000, 'available', 'Standard court'),
(7, 'Dragon 5', 'Synthetic', 135000, 'available', 'Standard court'),
(7, 'Dragon 6', 'Synthetic', 135000, 'available', 'Standard court'),
(7, 'Dragon 7', 'Synthetic', 135000, 'available', 'Standard court'),
(7, 'Dragon 8', 'Synthetic', 135000, 'available', 'Standard court'),
(7, 'Dragon 9', 'Synthetic', 135000, 'available', 'Standard court');

-- Facility 8 (Ocean View Sports) - 5 courts
INSERT INTO courts (facility_id, name, surface_type, hourly_rate, status, description) VALUES
(8, 'Ocean Court 1', 'Professional Synthetic', 170000, 'available', 'Court with ocean view'),
(8, 'Ocean Court 2', 'Professional Synthetic', 170000, 'available', 'Court with ocean view'),
(8, 'Ocean Court 3', 'Synthetic', 140000, 'available', 'Standard court'),
(8, 'Ocean Court 4', 'Synthetic', 140000, 'available', 'Standard court'),
(8, 'Ocean Court 5', 'Synthetic', 140000, 'available', 'Standard court');


-- 4. BOOKING DATABASE - Sample Bookings
USE DB_BOOKING;

-- Insert sample bookings (past, present, and future)
-- Past bookings (last week)
INSERT INTO bookings (user_id, facility_id, court_id, start_time, end_time, status, total_price, payment_status, created_at) VALUES
-- Week ago bookings
(10, 3, 11, DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 8 HOUR, DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 10 HOUR, 'completed', 300000, 'paid', DATE_SUB(NOW(), INTERVAL 8 DAY)),
(11, 3, 12, DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 10 HOUR, DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 12 HOUR, 'completed', 300000, 'paid', DATE_SUB(NOW(), INTERVAL 8 DAY)),
(12, 5, 27, DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 14 HOUR, DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 16 HOUR, 'completed', 400000, 'paid', DATE_SUB(NOW(), INTERVAL 8 DAY)),
(13, 5, 28, DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 16 HOUR, DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 18 HOUR, 'completed', 400000, 'paid', DATE_SUB(NOW(), INTERVAL 8 DAY)),
(14, 7, 47, DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 18 HOUR, DATE_SUB(NOW(), INTERVAL 7 DAY) + INTERVAL 20 HOUR, 'completed', 320000, 'paid', DATE_SUB(NOW(), INTERVAL 8 DAY)),

-- 3 days ago
(15, 4, 19, DATE_SUB(NOW(), INTERVAL 3 DAY) + INTERVAL 9 HOUR, DATE_SUB(NOW(), INTERVAL 3 DAY) + INTERVAL 11 HOUR, 'completed', 260000, 'paid', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(16, 6, 37, DATE_SUB(NOW(), INTERVAL 3 DAY) + INTERVAL 15 HOUR, DATE_SUB(NOW(), INTERVAL 3 DAY) + INTERVAL 17 HOUR, 'completed', 250000, 'paid', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(17, 8, 57, DATE_SUB(NOW(), INTERVAL 3 DAY) + INTERVAL 17 HOUR, DATE_SUB(NOW(), INTERVAL 3 DAY) + INTERVAL 19 HOUR, 'completed', 340000, 'paid', DATE_SUB(NOW(), INTERVAL 4 DAY)),

-- Today's bookings
(10, 3, 13, DATE_ADD(CURDATE(), INTERVAL 8 HOUR), DATE_ADD(CURDATE(), INTERVAL 10 HOUR), 'confirmed', 300000, 'paid', NOW()),
(11, 3, 14, DATE_ADD(CURDATE(), INTERVAL 10 HOUR), DATE_ADD(CURDATE(), INTERVAL 12 HOUR), 'confirmed', 300000, 'paid', NOW()),
(12, 3, 15, DATE_ADD(CURDATE(), INTERVAL 14 HOUR), DATE_ADD(CURDATE(), INTERVAL 16 HOUR), 'confirmed', 240000, 'paid', NOW()),
(13, 5, 29, DATE_ADD(CURDATE(), INTERVAL 16 HOUR), DATE_ADD(CURDATE(), INTERVAL 18 HOUR), 'confirmed', 360000, 'paid', NOW()),
(14, 5, 30, DATE_ADD(CURDATE(), INTERVAL 18 HOUR), DATE_ADD(CURDATE(), INTERVAL 20 HOUR), 'confirmed', 360000, 'paid', NOW()),
(15, 7, 48, DATE_ADD(CURDATE(), INTERVAL 19 HOUR), DATE_ADD(CURDATE(), INTERVAL 21 HOUR), 'confirmed', 270000, 'paid', NOW()),

-- Tomorrow's bookings
(16, 4, 20, DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL 9 HOUR, DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL 11 HOUR, 'confirmed', 260000, 'paid', NOW()),
(17, 6, 38, DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL 15 HOUR, DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL 17 HOUR, 'confirmed', 250000, 'paid', NOW()),
(18, 8, 58, DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL 17 HOUR, DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL 19 HOUR, 'pending', 340000, 'unpaid', NOW()),

-- Future bookings (2-5 days ahead)
(10, 3, 16, DATE_ADD(CURDATE(), INTERVAL 2 DAY) + INTERVAL 10 HOUR, DATE_ADD(CURDATE(), INTERVAL 2 DAY) + INTERVAL 12 HOUR, 'confirmed', 240000, 'paid', NOW()),
(11, 5, 31, DATE_ADD(CURDATE(), INTERVAL 3 DAY) + INTERVAL 14 HOUR, DATE_ADD(CURDATE(), INTERVAL 3 DAY) + INTERVAL 16 HOUR, 'pending', 360000, 'unpaid', NOW()),
(12, 7, 49, DATE_ADD(CURDATE(), INTERVAL 4 DAY) + INTERVAL 16 HOUR, DATE_ADD(CURDATE(), INTERVAL 4 DAY) + INTERVAL 18 HOUR, 'confirmed', 270000, 'paid', NOW()),
(13, 4, 21, DATE_ADD(CURDATE(), INTERVAL 5 DAY) + INTERVAL 18 HOUR, DATE_ADD(CURDATE(), INTERVAL 5 DAY) + INTERVAL 20 HOUR, 'pending', 260000, 'unpaid', NOW());

-- 5. BILLING DATABASE - Invoices
USE DB_BILL;

-- Create invoices for paid bookings
-- The booking_ids will need to match the actual IDs from DB_BOOKING
INSERT INTO invoices (booking_id, user_id, amount, currency, status, payment_method, payment_url, payment_reference, created_at, updated_at) VALUES
-- Completed bookings from last week
(1, 10, 300000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-001', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
(2, 11, 300000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-002', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
(3, 12, 400000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-003', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
(4, 13, 400000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-004', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
(5, 14, 320000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-005', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),

-- 3 days ago
(6, 15, 260000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-006', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),
(7, 16, 250000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-007', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),
(8, 17, 340000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-008', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),

-- Today's bookings
(9, 10, 300000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-009', NOW(), NOW()),
(10, 11, 300000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-010', NOW(), NOW()),
(11, 12, 240000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-011', NOW(), NOW()),
(12, 13, 360000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-012', NOW(), NOW()),
(13, 14, 360000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-013', NOW(), NOW()),
(14, 15, 270000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-014', NOW(), NOW()),

-- Tomorrow
(15, 16, 260000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-015', NOW(), NOW()),
(16, 17, 250000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-016', NOW(), NOW()),

-- Future paid
(18, 10, 240000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-017', NOW(), NOW()),
(20, 12, 270000, 'VND', 'paid', 'sepay', NULL, 'MOCK-TXN-SEED-018', NOW(), NOW());


-- Summary queries to verify
USE DB_AUTH;
SELECT 'Total Users' as Info, COUNT(*) as Count FROM User_Infor;
SELECT 'Managers' as Info, COUNT(*) as Count FROM User_Infor WHERE role='manager';
SELECT 'Customers' as Info, COUNT(*) as Count FROM User_Infor WHERE role='customer';

USE DB_FACILITY;
SELECT 'Total Facilities' as Info, COUNT(*) as Count FROM facilities;

USE DB_COURT;
SELECT 'Total Courts' as Info, COUNT(*) as Count FROM courts;

USE DB_BOOKING;
SELECT 'Total Bookings' as Info, COUNT(*) as Count FROM bookings;
SELECT 'Confirmed Bookings' as Info, COUNT(*) as Count FROM bookings WHERE status='confirmed';
SELECT 'Completed Bookings' as Info, COUNT(*) as Count FROM bookings WHERE status='completed';

USE DB_BILL;
SELECT 'Total Invoices' as Info, COUNT(*) as Count FROM invoices;
SELECT 'Paid Invoices' as Info, COUNT(*) as Count FROM invoices WHERE status='paid';
