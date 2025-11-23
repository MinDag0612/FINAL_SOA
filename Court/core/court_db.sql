CREATE DATABASE IF NOT EXISTS DB_COURT;

USE DB_COURT;

DROP TABLE IF EXISTS Court;

CREATE TABLE Court (
    court_id        INT AUTO_INCREMENT PRIMARY KEY,
    facility_id     INT NOT NULL,
    name            VARCHAR(200) NOT NULL,
    surface_type    VARCHAR(100),
    hourly_rate     DECIMAL(10,2),
    description     TEXT,
    available_hours JSON,
    is_active       TINYINT(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO Court (facility_id, name, surface_type, hourly_rate, description, available_hours, is_active)
VALUES
(1, 'Badminton Court #1', 'wood', 100000, 'Wood floor', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1),
(1, 'Badminton Court #2', 'wood', 100000, 'Wood floor', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1),
