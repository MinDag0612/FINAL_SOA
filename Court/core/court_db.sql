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

CREATE TABLE court_log (
    log_id          INT AUTO_INCREMENT PRIMARY KEY,   -- ID định danh log
    court_id        INT NOT NULL,
    facility_id     INT NOT NULL,
    name            VARCHAR(200) NOT NULL,
    surface_type    VARCHAR(100),
    hourly_rate     DECIMAL(10,2),
    description     TEXT,
    available_hours JSON NULL,
    is_active       TINYINT(1) DEFAULT 1,

    status          ENUM('official', 'discarded') DEFAULT 'official', -- trạng thái log
    changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (court_id) REFERENCES Court(court_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Price (
    price_id   INT AUTO_INCREMENT PRIMARY KEY,
    court_id   INT NOT NULL,
    price      DECIMAL(10,2) NOT NULL,
    status     ENUM('official', 'discarded') DEFAULT 'official',

    FOREIGN KEY (court_id) REFERENCES Court(court_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Days (
    days_id   INT AUTO_INCREMENT PRIMARY KEY,
    list_day  JSON NOT NULL COMMENT 'VD: ["Mon","Tue","Wed"]',
    price_id  INT NOT NULL,

    FOREIGN KEY (price_id) REFERENCES Price(price_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE Hours (
    hours_id  INT AUTO_INCREMENT PRIMARY KEY,
    start     TIME NOT NULL,
    end       TIME NOT NULL,
    price_id  INT NOT NULL,

    FOREIGN KEY (price_id) REFERENCES Price(price_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE staff_courts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL COMMENT 'FK to Auth.User_Infor.user_id',
    court_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_staff_court (staff_id, court_id),
    FOREIGN KEY (court_id) REFERENCES Court(court_id) ON DELETE CASCADE,
    INDEX idx_staff_id (staff_id),
    INDEX idx_court_id (court_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DELIMITER $$

CREATE TRIGGER trg_court_update
AFTER UPDATE ON Court
FOR EACH ROW
BEGIN    
    -- 1) Chuyển tất cả log cũ thành discarded
    UPDATE court_log
    SET status = 'discarded'
    WHERE court_id = NEW.court_id;

    -- 2) Thêm log mới ở trạng thái official
    INSERT INTO court_log (
        court_id, facility_id, name, surface_type, hourly_rate,
        description, available_hours, status
    ) VALUES (
        NEW.court_id, NEW.facility_id, NEW.name, NEW.surface_type,
        NEW.hourly_rate, NEW.description,
        NEW.available_hours, 'official'
    );

END$$

DELIMITER ;



INSERT INTO Court (facility_id, name, surface_type, hourly_rate, description, available_hours, is_active)
VALUES
(1, 'Badminton Court #1', 'wood', 100000, 'Wood floor', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1),
(1, 'Badminton Court #2', 'wood', 100000, 'Wood floor', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1),
(2, 'Tennis Court #1', 'hight quanlity', 120000, 'Grass', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1),
(2, 'Tennis Court #2', 'standard', 100000, 'Grass', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1);

-- Court #1: Update mô phỏng (tăng giá, đổi mô tả)
INSERT INTO court_log (
    court_id, facility_id, name, surface_type, hourly_rate,
    description, available_hours, is_active, status
) VALUES
(1, 1, 'Badminton Court #1', 'wood', 100000,
 'Wood floor', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1, 'discarded'),

(1, 1, 'Badminton Court #1', 'wood', 120000,
 'Wood floor – updated price', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1, 'official');

INSERT INTO court_log (
    court_id, facility_id, name, surface_type, hourly_rate,
    description, available_hours, is_active, status
) VALUES
-- Court #3: Update mô phỏng (đổi surface_type, chỉnh description)
(3, 2, 'Tennis Court #1', 'hight quanlity', 120000,
 'Grass', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1, 'discarded'),

(3, 2, 'Tennis Court #1', 'premium grass', 120000,
 'Grass surface upgraded – premium', '["06:00","07:00","08:00","09:00","19:00","20:00"]', 1, 'official');

INSERT INTO court_log (
    court_id, facility_id, name, surface_type, hourly_rate,
    description, available_hours, is_active, status
) VALUES
-- Court #2: mô phỏng sửa giờ mở cửa → discard
(2, 1, 'Badminton Court #2', 'wood', 100000,
 'Wood floor', '["06:00","08:00","09:00","19:00","20:00"]', 1, 'discarded'),

(2, 1, 'Badminton Court #2', 'wood', 100000,
 'Wood floor', '["06:00","07:00","08:00","09:00","19:00","21:00"]', 1, 'official');


INSERT INTO Price (court_id, price, status) VALUES
-- Court 1 (price_id 1–4)
(1, 100000, 'official'),   -- weekday morning
(1, 130000, 'official'),   -- weekday evening
(1, 150000, 'official'),   -- weekend morning
(1, 180000, 'official'),   -- weekend evening

-- Court 2 (price_id 5–8)
(2, 120000, 'official'),
(2, 150000, 'official'),
(2, 170000, 'official'),
(2, 210000, 'official'),

-- Court 3 (price_id 9–12)
(3, 140000, 'official'),
(3, 170000, 'official'),
(3, 190000, 'official'),
(3, 230000, 'official');

INSERT INTO Days (list_day, price_id) VALUES
-- Court 1
('["Mon","Tue","Wed","Thu","Fri"]', 1),
('["Mon","Tue","Wed","Thu","Fri"]', 2),
('["Sat","Sun"]', 3),
('["Sat","Sun"]', 4),

-- Court 2
('["Mon","Tue","Wed","Thu","Fri"]', 5),
('["Mon","Tue","Wed","Thu","Fri"]', 6),
('["Sat","Sun"]', 7),
('["Sat","Sun"]', 8),

-- Court 3
('["Mon","Tue","Wed","Thu","Fri"]', 9),
('["Mon","Tue","Wed","Thu","Fri"]', 10),
('["Sat","Sun"]', 11),
('["Sat","Sun"]', 12);

INSERT INTO Hours (start, end, price_id) VALUES
-- Court 1
('06:00', '17:00', 1),
('17:00', '22:00', 2),
('06:00', '17:00', 3),
('17:00', '22:00', 4),

-- Court 2
('06:00', '17:00', 5),
('17:00', '22:00', 6),
('06:00', '17:00', 7),
('17:00', '22:00', 8),

-- Court 3
('06:00', '17:00', 9),
('17:00', '22:00', 10),
('06:00', '17:00', 11),
('17:00', '22:00', 12);

-- Sample staff_courts assignments
-- Staff 1 (user_id=5) manages Court 1 and 2
-- Staff 2 (user_id=6) manages Court 3 and 4
INSERT INTO staff_courts (staff_id, court_id) VALUES
(5, 1),
(5, 2),
(6, 3),
(6, 4);