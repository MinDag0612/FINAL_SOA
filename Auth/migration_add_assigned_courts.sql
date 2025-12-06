-- Migration: Add assigned_courts to User_Infor table
-- Run this script if you already have the table created

USE DB_AUTH;

-- Add assigned_courts column (ignore error if already exists)
ALTER TABLE User_Infor 
ADD COLUMN assigned_courts JSON DEFAULT NULL 
COMMENT 'Danh sách ID sân được phân công cho staff (ví dụ: [1, 2, 3])';

-- Update staff users with assigned courts
UPDATE User_Infor SET assigned_courts = '[1, 2]' WHERE email = 'staff1@test.com';
UPDATE User_Infor SET assigned_courts = '[3, 4, 5]' WHERE email = 'staff2@test.com';

-- Verify
SELECT user_id, fullname, email, role, assigned_courts FROM User_Infor WHERE role = 'staff';
