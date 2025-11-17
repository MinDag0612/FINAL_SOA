CREATE DATABASE IF NOT EXISTS DB_COURT;

USE DB_COURT;

DROP TABLE IF EXISTS Court;

CREATE TABLE Court (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    fullname VARCHAR(255),
    password VARCHAR(255),
    role VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO Court(fullname, email, password, role) VALUES
    ('Nguyen Van A', 'a@example.com', "$argon2id$v=19$m=65536,t=3,p=4$OwsLMT80myAmcpb5/mpRQg$nFwmpRb9bZFk+Uz01870g2Q/85VORlYrrIUk33/FqEI", "customer"),
    ('Nguyen Van B', 'b@example.com', "$argon2id$v=19$m=65536,t=3,p=4$v1JvpId+k7ZlUpIGpgsfzA$Ttiu6vn0hCid0uLB/o/XXMRjFEZRD4P/OIMshC3Yhts", "manager"),
    ('Nguyen Van C', 'c@example.com', "$argon2id$v=19$m=65536,t=3,p=4$34ow4scCWKefJbT7d7+Sfg$S8f80+LyYqIBgE2Iar1gqxzZf+OJ8sg+VfeQwiOmRWY", "customer"),
    ('Nguyen Van D', 'd@example.com', "$argon2id$v=19$m=65536,t=3,p=4$766X2FajzJWpJcEBHd9BQA$Za5WCg+XUGN9gSl/2RG5lzNc55DUeHu407z+dYMWYAE", "manager");
