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

INSERT INTO bookings (user_id, facility_id, status, total_amount, payment_status, payment_method, hold_expires_at, paid_at)
VALUES
(1, 1, 'confirmed', 200000, 'paid', 'cash', NULL, NOW()),
(2, 2, 'pending', 350000, 'pending', 'momo', DATE_ADD(NOW(), INTERVAL 15 MINUTE), NULL);

INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price)
VALUES
(1, 1, '2025-11-20 07:00:00', '2025-11-20 09:00:00', 200000),
(2, 3, '2025-11-21 19:00:00', '2025-11-21 21:00:00', 350000);
