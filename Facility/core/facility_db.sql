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
    opening_hours   VARCHAR(100) DEFAULT '24/7',
    contact_phone   VARCHAR(50),
    amenities       JSON,
    is_active       TINYINT(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE facility_log (
    log_id          INT AUTO_INCREMENT PRIMARY KEY,
    facility_id     INT NOT NULL,
    user_id         INT NOT NULL,
    name            VARCHAR(200) NOT NULL,
    address         VARCHAR(255),
    sport           VARCHAR(100),
    description     TEXT,
    opening_hours   VARCHAR(100),
    contact_phone   VARCHAR(50),
    amenities       JSON,
    is_active       TINYINT(1),
    status          ENUM('official', 'discarded') DEFAULT 'official',
    changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (facility_id) REFERENCES Facility(facility_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DELIMITER $$

CREATE TRIGGER trg_facility_update
AFTER UPDATE ON Facility
FOR EACH ROW
BEGIN      
    -- 1) Đổi tất cả log cũ thành discarded
    UPDATE facility_log
    SET status = 'discarded'
    WHERE facility_id = NEW.facility_id;

    -- 2) Tạo bản log mới chính thức
    INSERT INTO facility_log (
        facility_id, user_id, name, address, sport, description,
        opening_hours, contact_phone, amenities, status
    ) VALUES (
        NEW.facility_id, NEW.user_id, NEW.name, NEW.address, NEW.sport,
        NEW.description, NEW.opening_hours, NEW.contact_phone,
        NEW.amenities, 'official'
    );
END$$

DELIMITER ;


INSERT INTO Facility (user_id, name, address, sport, description, opening_hours, contact_phone, amenities, is_active)
VALUES
(2, 'Sport Center A', 'Hanoi', 'Badminton', 'Main center with 4 courts', '24/7', '0123 456 789', '["Parking","Locker room","Shop"]', 1),
(4, 'Sport Club B', 'HCMC', 'Tennis', 'Premium tennis courts', '24/7', '0987 654 321', '["Parking","Coffee"]', 1),
(2, 'Sport Hub C', 'Da Nang', 'Football', '5v5 and 7v7 fields available', '24/7', '0909 888 777', '["Parking"]', 1);

INSERT INTO facility_log (
    facility_id, user_id, name, address, sport, description,
    opening_hours, contact_phone, amenities, is_active, status
) VALUES
-- Log chính thức ban đầu của Facility 1
(1, 2, 'Sport Center A', 'Hanoi', 'Badminton',
 'Main center with 4 courts',
 '24/7', '0123 456 789', '["Parking","Locker room","Shop"]', 1, 'official'),

-- Log cũ bị thay thế của Facility 1
(1, 2, 'Sport Center A', 'Hanoi', 'Badminton',
 'Updated description',
 '24/7', '0123 456 789', '["Parking","Locker room","Shop"]', 1, 'discarded'),

-- Log chính thức ban đầu của Facility 2
(2, 4, 'Sport Club B', 'HCMC', 'Tennis',
 'Premium tennis courts',
 '24/7', '0987 654 321', '["Parking","Coffee"]', 1, 'official'),

-- Log cũ bị thay thế của Facility 2
(2, 4, 'Sport Club B', 'HCMC', 'Tennis',
 'Premium courts updated',
 '24/7', '0987 654 321', '["Parking","Coffee"]', 1, 'discarded'),

-- Log chính thức ban đầu của Facility 3
(3, 2, 'Sport Hub C', 'Da Nang', 'Football',
 '5v5 and 7v7 fields available',
 '24/7', '0909 888 777', '["Parking"]', 1, 'official');

