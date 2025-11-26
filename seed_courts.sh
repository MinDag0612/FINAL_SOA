#!/bin/bash

echo "========================================"
echo "  SEEDING COURTS DATABASE"
echo "========================================"

# Facility 3: Champions Arena - 8 courts
docker exec court_db mysql -u root -proot -e "USE DB_COURT; INSERT INTO Court (facility_id, name, surface_type, hourly_rate, description, is_active) VALUES (3, 'Court A1', 'Rubber', 150000, 'Premium court with professional lighting', 1), (3, 'Court A2', 'Rubber', 150000, 'Premium court with air conditioning', 1), (3, 'Court A3', 'Vinyl', 140000, 'Standard court with good ventilation', 1), (3, 'Court A4', 'Vinyl', 140000, 'Standard court', 1), (3, 'Court A5', 'Vinyl', 130000, 'Economy court', 1), (3, 'Court A6', 'Vinyl', 130000, 'Economy court', 1), (3, 'Court A7', 'Wood', 160000, 'VIP court with premium wood flooring', 1), (3, 'Court A8', 'Wood', 160000, 'VIP court', 1);" 2>&1 | grep -v "Warning"

# Facility 4: Victory Complex - 6 courts
docker exec court_db mysql -u root -proot -e "USE DB_COURT; INSERT INTO Court (facility_id, name, surface_type, hourly_rate, description, is_active) VALUES (4, 'Court B1', 'Rubber', 120000, 'Family-friendly court', 1), (4, 'Court B2', 'Rubber', 120000, 'Family-friendly court', 1), (4, 'Court B3', 'Vinyl', 110000, 'Standard court', 1), (4, 'Court B4', 'Vinyl', 110000, 'Standard court', 1), (4, 'Court B5', 'Vinyl', 110000, 'Economy court', 1), (4, 'Court B6', 'Vinyl', 110000, 'Economy court', 1);" 2>&1 | grep -v "Warning"

# Facility 5: Elite Club - 10 courts
docker exec court_db mysql -u root -proot -e "USE DB_COURT; INSERT INTO Court (facility_id, name, surface_type, hourly_rate, description, is_active) VALUES (5, 'Court C1', 'Wood', 200000, 'Elite VIP court', 1), (5, 'Court C2', 'Wood', 200000, 'Elite VIP court', 1), (5, 'Court C3', 'Wood', 180000, 'Premium court', 1), (5, 'Court C4', 'Wood', 180000, 'Premium court', 1), (5, 'Court C5', 'Rubber', 160000, 'Standard court', 1), (5, 'Court C6', 'Rubber', 160000, 'Standard court', 1), (5, 'Court C7', 'Rubber', 160000, 'Standard court', 1), (5, 'Court C8', 'Vinyl', 150000, 'Economy court', 1), (5, 'Court C9', 'Vinyl', 150000, 'Economy court', 1), (5, 'Court C10', 'Vinyl', 150000, 'Economy court', 1);" 2>&1 | grep -v "Warning"

# Facility 6: Phoenix Center - 7 courts
docker exec court_db mysql -u root -proot -e "USE DB_COURT; INSERT INTO Court (facility_id, name, surface_type, hourly_rate, description, is_active) VALUES (6, 'Court D1', 'Rubber', 140000, 'Modern court with AC', 1), (6, 'Court D2', 'Rubber', 140000, 'Modern court', 1), (6, 'Court D3', 'Vinyl', 130000, 'Standard court', 1), (6, 'Court D4', 'Vinyl', 130000, 'Standard court', 1), (6, 'Court D5', 'Vinyl', 120000, 'Economy court', 1), (6, 'Court D6', 'Vinyl', 120000, 'Economy court', 1), (6, 'Court D7', 'Wood', 170000, 'VIP court', 1);" 2>&1 | grep -v "Warning"

# Facility 7: Dragon Hall - 9 courts
docker exec court_db mysql -u root -proot -e "USE DB_COURT; INSERT INTO Court (facility_id, name, surface_type, hourly_rate, description, is_active) VALUES (7, 'Court E1', 'Rubber', 145000, 'Spacious court', 1), (7, 'Court E2', 'Rubber', 145000, 'Spacious court', 1), (7, 'Court E3', 'Rubber', 145000, 'Spacious court', 1), (7, 'Court E4', 'Vinyl', 135000, 'Standard court', 1), (7, 'Court E5', 'Vinyl', 135000, 'Standard court', 1), (7, 'Court E6', 'Vinyl', 125000, 'Economy court', 1), (7, 'Court E7', 'Vinyl', 125000, 'Economy court', 1), (7, 'Court E8', 'Wood', 165000, 'VIP court', 1), (7, 'Court E9', 'Wood', 165000, 'VIP court', 1);" 2>&1 | grep -v "Warning"

# Facility 8: Ocean View - 5 courts
docker exec court_db mysql -u root -proot -e "USE DB_COURT; INSERT INTO Court (facility_id, name, surface_type, hourly_rate, description, is_active) VALUES (8, 'Court F1', 'Vinyl', 115000, 'Ocean view court', 1), (8, 'Court F2', 'Vinyl', 115000, 'Ocean view court', 1), (8, 'Court F3', 'Vinyl', 115000, 'Standard court', 1), (8, 'Court F4', 'Rubber', 125000, 'Premium ocean view', 1), (8, 'Court F5', 'Rubber', 125000, 'Premium court', 1);" 2>&1 | grep -v "Warning"

echo "✅ Courts seeded successfully!"
docker exec court_db mysql -u root -proot -e "SELECT COUNT(*) as total_courts FROM DB_COURT.Court;" 2>&1 | grep -v "Warning"
docker exec court_db mysql -u root -proot -e "SELECT facility_id, COUNT(*) as court_count FROM DB_COURT.Court GROUP BY facility_id;" 2>&1 | grep -v "Warning"
