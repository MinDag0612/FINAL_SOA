CREATE DATABASE IF NOT EXISTS DB_SESSION;

USE DB_SESSION;

DROP TABLE IF EXISTS Session;

CREATE TABLE Session (
    session_id   INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    device       VARCHAR(100),
    ip_address   VARCHAR(45),
    user_agent   VARCHAR(255),
    is_active    TINYINT(1) DEFAULT 1,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO Session (user_id, device, ip_address, user_agent, is_active)
VALUES
(7, 'Chrome', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 1),
(8, 'Mobile', '192.168.1.10', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)', 1),
(9, 'Tablet', '10.0.0.5', 'Mozilla/5.0 (Linux; Android 13)', 0);
