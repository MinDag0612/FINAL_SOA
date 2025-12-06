-- Migration: Add customer fields to bookings table
-- Date: 2025-12-06
-- Description: Add customer_name, customer_phone, customer_email columns to store customer information directly

USE DB_BOOKING;

-- Add new columns
ALTER TABLE bookings
ADD COLUMN customer_name VARCHAR(255) AFTER payment_reference,
ADD COLUMN customer_phone VARCHAR(20) AFTER customer_name,
ADD COLUMN customer_email VARCHAR(255) AFTER customer_phone;

-- Optional: Migrate existing data from note field to new columns
-- This is a best-effort migration for old data using SUBSTRING_INDEX
UPDATE bookings
SET 
    customer_name = CASE 
        WHEN note LIKE '%Khách:%' THEN 
            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(note, 'Khách: ', -1), ' |', 1))
        ELSE NULL
    END,
    customer_phone = CASE 
        WHEN note LIKE '%SDT:%' THEN 
            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(note, 'SDT: ', -1), ' |', 1))
        ELSE NULL
    END,
    customer_email = CASE 
        WHEN note LIKE '%Email:%' THEN 
            TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(note, 'Email: ', -1), ' |', 1))
        ELSE NULL
    END
WHERE note IS NOT NULL AND note LIKE '%Khách:%';

-- Verify migration
SELECT 
    booking_id,
    customer_name,
    customer_phone,
    customer_email,
    note
FROM bookings
LIMIT 10;
