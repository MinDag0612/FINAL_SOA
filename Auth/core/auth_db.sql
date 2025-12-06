CREATE DATABASE IF NOT EXISTS DB_AUTH;

USE DB_AUTH;

DROP TABLE IF EXISTS User_Infor;

CREATE TABLE User_Infor (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    fullname VARCHAR(255),
    password VARCHAR(255),
    role VARCHAR(50),
    assigned_courts JSON DEFAULT NULL COMMENT 'Danh sách ID sân được phân công cho staff (ví dụ: [1, 2, 3])'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO User_Infor(fullname, email, password, role) VALUES
    ('Ton Minh Dang 1', 'tonminhdang9@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"), 
    ('Ton Minh Dang 2', '523h0011@student.tdtu.edu.vn', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "manager"),
    ('Nguyen Van C', 'c@example.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"),
    ('Nguyen Van D', 'd@example.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "manager"),
    ('Staff User 1', 'staff1@test.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "staff"),
    ('Staff User 2', 'staff2@test.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "staff"),
    ('Phan Viet Quan', 'vquan29905@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "manager"),
    ('Phan Viet Quan 2', 'vquan2k5@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "manager"),
    ('Nguyen Van Manager', 'manager1@badminton.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "manager"),
    ('Tran Thi Manager', 'manager2@badminton.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "manager"),
    ('Le Van Manager', 'manager3@badminton.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "manager"),
    ('Pham Van A', 'customer1@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"),
    ('Hoang Thi B', 'customer2@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"),
    ('Vu Van C', 'customer3@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"),
    ('Bui Thi D', 'customer4@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"),
    ('Dang Van E', 'customer5@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"),
    ('Ngo Thi F', 'customer6@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"),
    ('Do Van G', 'customer7@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"),
    ('Trinh Thi H', 'customer8@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"),
    ('Luong Van I', 'customer9@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"),
    ('Mai Thi J', 'customer10@gmail.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer"),
    ('Customer Test', 'customer@test.com', "$2b$12$x/Dmice72PMNERJ8RTB2Q.EtXvfn7F9eFbOtBYRk08f1h2xU.gEHO", "customer");

-- Phân công sân cho staff users
UPDATE User_Infor SET assigned_courts = '[1, 2]' WHERE email = 'staff1@test.com';
UPDATE User_Infor SET assigned_courts = '[3, 4, 5]' WHERE email = 'staff2@test.com';

