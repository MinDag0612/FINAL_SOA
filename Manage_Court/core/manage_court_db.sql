CREATE DATABASE IF NOT EXISTS DB_MANAGE_COURT;

USE DB_MANAGE_COURT;

-- Drop child table first to avoid FK issues
DROP TABLE IF EXISTS Court;
DROP TABLE IF EXISTS Facility;

CREATE TABLE Facility  (
    facility_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,     -- owner
    facility_name   VARCHAR(200) NOT NULL,
    location        VARCHAR(255),
    sport           VARCHAR(100) DEFAULT 'Badminton',
    description     TEXT,
    CHECK (sport = 'Badminton')
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
(2, 'Badminton Center A', 'Ha Noi', 'Badminton', 'Trung tâm 4 sân đạt chuẩn'),
(4, 'Badminton Club B', 'HCMC', 'Badminton', 'Phòng máy lạnh, ánh sáng LED'),
(2, 'Badminton Hub C', 'Da Nang', 'Badminton', 'Có phòng thay đồ và bãi xe');

INSERT INTO Court (facility_id, court_name, price_per_hour, description)
VALUES
-- Facility 1
(1, 'Badminton Court #1', 100000, 'Sàn PVC, tiêu chuẩn thi đấu'),
(1, 'Badminton Court #2', 100000, 'Sàn PVC, ánh sáng LED'),
(1, 'Badminton Court #3', 120000, 'Sàn gỗ, trần cao'),

-- Facility 2
(2, 'Badminton Court #1', 150000, 'Phòng lạnh, thảm mới'),
(2, 'Badminton Court #2', 150000, 'Phòng lạnh, ánh sáng LED'),

-- Facility 3
(3, 'Badminton Court #1', 90000, 'Phù hợp tập luyện'),
(3, 'Badminton Court #2', 90000, 'Ánh sáng tự nhiên');
