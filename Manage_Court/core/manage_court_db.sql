CREATE DATABASE IF NOT EXISTS DB_MANAGE_COURT;

USE DB_MANAGE_COURT;

-- Court service giữ riêng bảng Court; facility_id là tham chiếu logic
DROP TABLE IF EXISTS CourtMaintenance;
DROP TABLE IF EXISTS Court;

CREATE TABLE Court (
    court_id        INT AUTO_INCREMENT PRIMARY KEY,
    facility_id     INT NOT NULL,
    court_name      VARCHAR(200) NOT NULL,
    price_per_hour  DECIMAL(10,2) NOT NULL,
    description     TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE CourtMaintenance (
    maintenance_id       INT AUTO_INCREMENT PRIMARY KEY,
    court_id             INT NOT NULL,
    date                 DATE NOT NULL,
    start_time           TIME NOT NULL,
    end_time             TIME NOT NULL,
    reason               VARCHAR(255),
    status               VARCHAR(50) DEFAULT 'scheduled'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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

INSERT INTO CourtMaintenance (court_id, date, start_time, end_time, reason, status) VALUES
(1, '2024-07-01', '10:00', '12:00', 'Vệ sinh sân', 'scheduled'),
(2, '2024-07-01', '08:00', '09:00', 'Bảo trì đèn', 'scheduled');
