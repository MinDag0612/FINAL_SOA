CREATE DATABASE IF NOT EXISTS DB_BOOKING;

USE DB_BOOKING;

DROP TABLE IF EXISTS booking_items;
DROP TABLE IF EXISTS bookings;

CREATE TABLE bookings (
    booking_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT NOT NULL,
    facility_id      INT NOT NULL,
    status           VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_amount     DECIMAL(12,2) NOT NULL,
    payment_status   VARCHAR(20),
    payment_method   VARCHAR(50),
    payment_reference VARCHAR(100),
    note             TEXT,
    hold_expires_at  DATETIME,
    paid_at          DATETIME,
    cancel_reason    TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE booking_items (
    item_id     INT AUTO_INCREMENT PRIMARY KEY,
    booking_id  INT NOT NULL,
    court_id    INT NOT NULL,
    start_time  DATETIME NOT NULL,
    end_time    DATETIME NOT NULL,
    price       DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_booking_item_booking FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_booking_court_time ON booking_items (court_id, start_time, end_time);

-- ======= bookings =======
INSERT INTO bookings (user_id, facility_id, status, total_amount, payment_status, payment_method, hold_expires_at, paid_at)
VALUES
(1, 1, 'confirmed', 200000, 'paid', 'cash', NULL, NOW()),
(2, 1, 'pending', 350000, 'pending', 'momo', DATE_ADD(NOW(), INTERVAL 15 MINUTE), NULL),
(1, 1, 'confirmed', 400000, 'paid', 'momo', NULL, NOW()),
(2, 1, 'confirmed', 150000, 'paid', 'cash', NULL, NOW()),
(1, 1, 'pending', 300000, 'pending', 'momo', DATE_ADD(NOW(), INTERVAL 30 MINUTE), NULL),
(2, 1, 'confirmed', 250000, 'paid', 'cash', NULL, NOW()),
(1, 1, 'confirmed', 350000, 'paid', 'momo', NULL, NOW()),
(2, 1, 'pending', 200000, 'pending', 'cash', DATE_ADD(NOW(), INTERVAL 20 MINUTE), NULL),
(1, 1, 'confirmed', 300000, 'paid', 'cash', NULL, NOW()),
(2, 1, 'confirmed', 400000, 'paid', 'momo', NULL, NOW());

-- ======= booking_items =======
INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price)
VALUES
(1, 1, '2025-11-20 07:00:00', '2025-11-20 09:00:00', 200000),
(2, 2, '2025-11-21 19:00:00', '2025-11-21 21:00:00', 350000),
(3, 1, '2025-11-20 10:00:00', '2025-11-20 12:00:00', 200000),
(3, 2, '2025-11-21 08:00:00', '2025-11-21 10:00:00', 200000),
(4, 1, '2025-11-22 07:00:00', '2025-11-22 08:30:00', 150000),
(5, 2, '2025-11-23 09:00:00', '2025-11-23 11:00:00', 150000),
(5, 1, '2025-11-23 12:00:00', '2025-11-23 13:30:00', 150000),
(6, 2, '2025-11-24 14:00:00', '2025-11-24 16:00:00', 250000),
(7, 1, '2025-11-25 07:00:00', '2025-11-25 09:00:00', 175000),
(7, 2, '2025-11-25 10:00:00', '2025-11-25 12:00:00', 175000),
(8, 1, '2025-11-26 07:00:00', '2025-11-26 09:00:00', 200000),
(9, 2, '2025-11-27 08:00:00', '2025-11-27 10:00:00', 150000),
(9, 1, '2025-11-27 11:00:00', '2025-11-27 13:00:00', 150000),
(10, 2, '2025-11-28 09:00:00', '2025-11-28 11:00:00', 200000),
(10, 1, '2025-11-28 12:00:00', '2025-11-28 14:00:00', 200000);

