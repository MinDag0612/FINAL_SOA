# 🏸 BSport Staff Accounts

## Tài khoản Staff

### Staff 1 (Trực sân 1, 2)
- **Email**: `staff1@test.com`
- **Password**: `123456`
- **Assigned Courts**: Sân 1, Sân 2
- **URL**: http://localhost:8080/UI/Staff/index.html

### Staff 2 (Trực sân 3, 4, 5)
- **Email**: `staff2@test.com`
- **Password**: `123456`
- **Assigned Courts**: Sân 3, Sân 4, Sân 5
- **URL**: http://localhost:8080/UI/Staff/index.html

---

## Tài khoản Manager (để so sánh)
- **Email**: `523h0011@student.tdtu.edu.vn`
- **Password**: `123456`
- **URL**: http://localhost:8080/UI/Manager/index.html

---

## Tài khoản Customer
- **Email**: `customer@test.com`
- **Password**: `123456`
- **URL**: http://localhost:8080/UI/Customer/index.html

---

## Chức năng Staff (So với Manager)

### ✅ Staff CÓ QUYỀN:
- Xem danh sách sân được phân công
- Xem lịch sử booking của sân được phân công
- Tạo booking Walk-in cho sân được phân công
- Cập nhật trạng thái booking (confirmed/cancelled)
- Xem báo cáo doanh thu của ca trực

### ❌ Staff KHÔNG CÓ QUYỀN:
- Xem tất cả sân (chỉ xem sân được phân công)
- Chỉnh sửa thông tin sân (tab Cài Đặt bị ẩn)
- Xem báo cáo toàn bộ cơ sở (chỉ xem ca trực)
- Quản lý staff khác

---

## Database Schema

```sql
CREATE TABLE User_Infor (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    fullname VARCHAR(255),
    password VARCHAR(255),
    role VARCHAR(50),
    assigned_courts JSON DEFAULT NULL -- Mới thêm!
);

-- Example:
UPDATE User_Infor 
SET assigned_courts = '[1, 2]' 
WHERE email = 'staff1@test.com';
```

---

## Test Flow

### 1. Login Staff 1
```
Email: staff1@test.com
Password: 123456
```

### 2. Kiểm tra:
- ✅ Chỉ thấy Sân 1, Sân 2 (không thấy sân 3, 4, 5...)
- ✅ Tab "Cài Đặt" không hiển thị
- ✅ Header title: "NHÂN VIÊN TRỰC SÂN"

### 3. Thử tạo booking Walk-in
- Chọn sân 1 hoặc 2
- Nhập thông tin khách
- Xác nhận booking

### 4. Xem Lịch Sử Booking
- Chỉ hiển thị booking của sân 1, 2
- Có thể cập nhật trạng thái

### 5. Xem Báo Cáo
- Chỉ hiển thị doanh thu của sân 1, 2
- Filter theo ca trực (sẽ implement tiếp)

---

## Next Steps

### TODO:
1. ✅ Add `assigned_courts` column to DB
2. ✅ Update Auth service to return assigned_courts in JWT
3. ✅ Filter courts in Staff UI
4. ⏳ Filter bookings by assigned courts
5. ⏳ Filter reports by shift time (ca trực)
6. ⏳ Add shift management (ca sáng 8h-16h, ca chiều 16h-24h)

---

## Troubleshooting

### Lỗi: "Cannot read property 'assigned_courts'"
→ Check JWT token có chứa assigned_courts không:
```javascript
console.log(auth.user.assigned_courts);
```

### Staff thấy tất cả sân
→ Check `assignedCourts` filter trong staff_main.js:
```javascript
courts = courts.filter(c => assignedCourts.includes(c.id));
```

### Không login được
→ Check Auth service có chạy không:
```bash
docker ps | grep auth
```
