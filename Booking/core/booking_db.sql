CREATE DATABASE IF NOT EXISTS DB_BOOKING;

USE DB_BOOKING;

DROP TABLE IF EXISTS booking_logs;
DROP TABLE IF EXISTS log_booking;
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
    customer_name    VARCHAR(255),
    customer_phone   VARCHAR(20),
    customer_email   VARCHAR(255),
    note             TEXT,
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

CREATE TABLE log_booking (
    log_id        INT AUTO_INCREMENT PRIMARY KEY,
    booking_id    INT NOT NULL,
    item_id       INT NOT NULL,
    court_id      INT NOT NULL,
    old_start     DATETIME,
    old_end       DATETIME,
    new_start     DATETIME,
    new_end       DATETIME,
    old_price     DECIMAL(12,2),
    new_price     DECIMAL(12,2),
    action        VARCHAR(50) NOT NULL DEFAULT 'reschedule',
    changed_by    INT,
    note          TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_log_booking_booking FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
    CONSTRAINT fk_log_booking_item FOREIGN KEY (item_id) REFERENCES booking_items(item_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_booking_court_time ON booking_items (court_id, start_time, end_time);
CREATE INDEX idx_log_booking_booking ON log_booking (booking_id);

CREATE TABLE booking_logs (
    log_id               INT AUTO_INCREMENT PRIMARY KEY,
    booking_id           INT NOT NULL,
    action_type          VARCHAR(50) NOT NULL,
    old_status           VARCHAR(20),
    new_status           VARCHAR(20),
    old_payment_status   VARCHAR(20),
    new_payment_status   VARCHAR(20),
    changed_by_user_id   INT,
    changed_by_role      VARCHAR(20) DEFAULT 'system',
    reason               TEXT,
    changes_json         JSON,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_booking_logs_booking FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_booking_logs_booking ON booking_logs (booking_id);

INSERT INTO bookings (user_id, facility_id, status, total_amount, payment_status, payment_method, paid_at)
VALUES
(1, 1, 'confirmed', 200000, 'paid', 'cash', NOW()),
(2, 2, 'pending', 350000, 'pending', 'momo', NULL);

INSERT INTO booking_items (booking_id, court_id, start_time, end_time, price)
VALUES
(1, 1, '2025-11-20 07:00:00', '2025-11-20 09:00:00', 200000),
(2, 2, '2025-11-21 19:00:00', '2025-11-21 21:00:00', 350000);
