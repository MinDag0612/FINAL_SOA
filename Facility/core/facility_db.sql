CREATE DATABASE IF NOT EXISTS DB_FACILITY;

USE DB_FACILITY;

DROP TABLE IF EXISTS Facility;

CREATE TABLE Facility  (
    facility_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    name            VARCHAR(200) NOT NULL,
    address         VARCHAR(255),
    sport           VARCHAR(100),
    description     TEXT,
    opening_hours   VARCHAR(100),
    contact_phone   VARCHAR(50),
    amenities       JSON,
    is_active       TINYINT(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO Facility (user_id, name, address, sport, description, opening_hours, contact_phone, amenities, is_active)
VALUES
(2, 'Sport Center A', 'Hanoi', 'Badminton', 'Main center with 4 courts', '06:00-23:00', '0123 456 789', '["Parking","Locker room","Shop"]', 1),
(4, 'Sport Club B', 'HCMC', 'Tennis', 'Premium tennis courts', '06:00-22:00', '0987 654 321', '["Parking","Coffee"]', 1),
(2, 'Sport Hub C', 'Da Nang', 'Football', '5v5 and 7v7 fields available', '07:00-23:00', '0909 888 777', '["Parking"]', 1);
