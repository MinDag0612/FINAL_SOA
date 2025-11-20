CREATE DATABASE IF NOT EXISTS DB_BOOKING;

USE DB_BOOKING;

DROP TABLE IF EXISTS Booking;

CREATE TABLE Booking (
    booking_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    court_id     INT NOT NULL,
    date_from       DATETIME NOT NULL,
    date_to         DATETIME NOT NULL,
    payment_method  VARCHAR(50),
    pay_at          DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO Booking
(user_id, court_id, date_from, date_to, payment_method, pay_at)
VALUES
(1, 1, '2025-11-20', '2025-11-22', 'cash', '2025-11-20 07:55:00'),
(3, 1, '2025-11-20', '2025-11-21', 'banking', '2025-11-20 12:45:00'),
(1, 2, '2025-11-21', '2025-11-23', 'momo', NULL);
