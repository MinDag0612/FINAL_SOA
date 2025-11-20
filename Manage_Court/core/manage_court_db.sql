CREATE DATABASE IF NOT EXISTS DB_MANAGE_COURT;

USE DB_MANAGE_COURT;

DROP TABLE IF EXISTS Facility ;

CREATE TABLE Facility  (
    facility_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,     -- owner
    facility_name   VARCHAR(200) NOT NULL,
    location        VARCHAR(255),
    sport           VARCHAR(100),
    description     TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Court (
    court_id        INT AUTO_INCREMENT PRIMARY KEY,
    facility_id     INT NOT NULL,
    court_name      VARCHAR(200) NOT NULL,
    price_per_hour  DECIMAL(10,2) NOT NULL,
    description     TEXT,

    CONSTRAINT fk_court_facility
        FOREIGN KEY (facility_id) REFERENCES Facility(facility_id)
);

INSERT INTO Facility (user_id, facility_name, location, sport, description)
VALUES
(2, 'Sport Center A', 'Hanoi', 'Badminton', 'Main center with 4 courts'),
(4, 'Sport Club B', 'HCMC', 'Tennis', 'Premium tennis courts'),
(2, 'Sport Hub C', 'Da Nang', 'Football', '5v5 and 7v7 fields available');

INSERT INTO Court (facility_id, court_name, price_per_hour, description)
VALUES
-- Facility 1
(1, 'Badminton Court #1', 100000, 'Wood floor'),
(1, 'Badminton Court #2', 100000, 'Wood floor'),
(1, 'Badminton Court #3', 120000, 'Premium court'),

-- Facility 2
(2, 'Tennis Court #1', 250000, 'Standard clay court'),
(2, 'Tennis Court #2', 350000, 'Premium lighting'),

-- Facility 3
(3, 'Football Field 5v5', 300000, 'Small field'),
(3, 'Football Field 7v7', 450000, 'Large size field');
