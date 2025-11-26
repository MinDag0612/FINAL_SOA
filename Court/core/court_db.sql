CREATE DATABASE IF NOT EXISTS DB_COURT;

USE DB_COURT;

DROP TABLE IF EXISTS Court;

CREATE TABLE Court (
    court_id       INT AUTO_INCREMENT PRIMARY KEY,
    facility_id     INT NOT NULL,
    name            VARCHAR(200) NOT NULL,
    surface_type    VARCHAR(100),
    hourly_rate     DECIMAL(10,2),
    description     TEXT,
    available_hours JSON NULL COMMENT 'NULL = open 24/7, otherwise list of hourly start times',
    is_active       TINYINT(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO Court (facility_id, name, surface_type, hourly_rate, description, available_hours, is_active)
VALUES
(1, 'Badminton Court #1', 'wood', 100000, 'Wood floor', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1),
<<<<<<< HEAD
(1, 'Badminton Court #2', 'wood', 100000, 'Wood floor', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1);
>>>>>>> MAIN
=======
<<<<<<< HEAD
(1, 'Badminton Court #2', 'wood', 100000, 'Wood floor', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1),
(2, 'Tennis Court #1', 'hight quanlity', 120000, 'Grass', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1),
(2, 'Tennis Court #2', 'standard', 100000, 'Grass', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1);
=======
(1, 'Badminton Court #2', 'wood', 100000, 'Wood floor', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1);
>>>>>>> MAIN
>>>>>>> 2f647f178b4616b6ce97b54de11a0468833f0cbb
>>>>>>> 7f3ffaacc95ad918698a4d53a6a3079a1216f6d3
