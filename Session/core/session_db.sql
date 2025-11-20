CREATE DATABASE IF NOT EXISTS DB_SESSION;

USE DB_SESSION;

DROP TABLE IF EXISTS Session;

CREATE TABLE Session (
    session_id  INT AUTO_INCREMENT PRIMARY KEY,
    booking_id  INT NOT NULL,
    court_id    INT NOT NULL,
    time_from   TIME NOT NULL,
    time_to     TIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO Session (booking_id, court_id, time_from, time_to)
VALUES
(1, 1, '08:00:00', '10:00:00'),
(2, 2, '13:00:00', '15:00:00'),
(3, 3, '17:00:00', '18:00:00');
