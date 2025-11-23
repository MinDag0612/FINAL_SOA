CREATE DATABASE IF NOT EXISTS DB_FACILITY;
USE DB_FACILITY;

-- Chỉ giữ bảng Facility cho service Facility
DROP TABLE IF EXISTS Facility;

CREATE TABLE Facility (
    facility_id   INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    facility_name VARCHAR(200) NOT NULL,
    location      VARCHAR(255),
    sport         VARCHAR(100) DEFAULT 'Badminton',
    amenities     JSON,
    description   TEXT,
    CHECK (sport = 'Badminton')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO Facility (user_id, facility_name, location, sport, description, amenities) VALUES
(2, 'Badminton Center A', 'Ha Noi', 'Badminton', 'Trung tâm 4 sân đạt chuẩn', JSON_ARRAY('Bãi xe', 'Nước uống', 'Phòng thay đồ')),
(4, 'Badminton Club B', 'HCMC', 'Badminton', 'Phòng máy lạnh, ánh sáng LED', JSON_ARRAY('Máy lạnh', 'Shop dụng cụ')),
(2, 'Badminton Hub C', 'Da Nang', 'Badminton', 'Có phòng thay đồ và bãi xe', JSON_ARRAY('Bãi xe', 'Phòng tắm'));
