# Manager Integration Tests

## 📋 Mô tả

Test suite toàn diện kiểm tra tất cả chức năng của Manager Dashboard:
- ✅ Authentication & JWT validation
- ✅ Facility & Courts loading
- ✅ Booking management (list, create, verify)
- ✅ Report filtering & revenue calculation
- ✅ UI component rendering
- ✅ Automatic cleanup

## 🚀 Cách chạy

### 1. Mở file test trong browser

```bash
# Từ thư mục FINAL_SOA
open UI/Homepage/test_manager_integration.html
```

Hoặc mở trực tiếp bằng File Explorer → Double click `test_manager_integration.html`

### 2. Cấu hình (nếu cần)

Mặc định đã config sẵn:
- **API Gateway**: `https://hyperpathetic-fugally-erin.ngrok-free.dev`
- **Manager Email**: `manager1@badminton.com`
- **Password**: `password123`
- **Test Facility ID**: `3` (Champions Badminton Arena)

### 3. Chạy tests

**Option A: Chạy tất cả (khuyến nghị)**
- Click nút **"▶ Run All Tests"**
- Chờ ~10 giây để hoàn thành

**Option B: Chạy tests đã chọn**
- Uncheck các tests không muốn chạy
- Click nút **"▶ Run Selected Only"**

**Option C: Dừng giữa chừng**
- Click nút **"⏹ Stop"** nếu muốn dừng

## 📊 Danh sách Tests

### Authentication & Setup (2 tests)
1. **Manager Login** - Test đăng nhập và lấy JWT token
2. **JWT Token Structure** - Verify token có đủ fields (sub, infor.role=manager)

### Facility & Courts Management (2 tests)
3. **Load Manager Facilities** - Load danh sách cơ sở của manager
4. **Load Courts for Facility** - Load danh sách sân của facility

### Booking Management (3 tests)
5. **Load Bookings for Date** - Load bookings theo ngày
6. **Create Walk-in Booking** - Tạo booking walk-in mới (14:00-15:00)
7. **Verify Booking Created** - Kiểm tra booking mới có trong list (sau 500ms)

### Report & Analytics (2 tests)
8. **Report Filters Pending/Cancelled** - Verify report chỉ tính confirmed/completed
9. **Revenue Calculation** - Tính tổng doanh thu từ bookings

### UI Components (2 tests)
10. **Courts Timeline Rendering** - Simulate rendering timeline với booked slots
11. **Booking Table Rendering** - Verify booking table data structure

### Cleanup (1 test)
12. **Cancel Test Booking** - Hủy booking test vừa tạo (cleanup)

## 📈 Kết quả mong đợi

Nếu hệ thống hoạt động đúng:
```
Total: 12
Passed: 12 ✅
Failed: 0
Duration: ~8-10s
```

## ❌ Nếu có test fail

### Test 1 (Manager Login) failed
- **Nguyên nhân**: Sai email/password hoặc API Gateway không chạy
- **Fix**: Kiểm tra credentials, restart backend services

### Test 6 (Create Walk-in) failed
- **Nguyên nhân**: Booking service lỗi hoặc validation fail
- **Fix**: Check Booking service logs, verify court_id tồn tại

### Test 7 (Verify Booking Created) failed ⚠️
- **Nguyên nhân**: Booking API không trả về booking mới (CRITICAL!)
- **Fix**: 
  1. Check database có booking mới không: `SELECT * FROM bookings ORDER BY booking_id DESC LIMIT 1;`
  2. Nếu có trong DB nhưng API không trả về → Bug trong `get_bookings_by_facility`
  3. Nếu không có trong DB → Bug trong `create_booking`

### Test 8 (Report Filter) failed
- **Nguyên nhân**: Frontend logic filter status không đúng
- **Fix**: Check `manager_report.js` → `calculateRevenueByCourtId`

## 🔍 Debug Tips

### Xem Console logs
- F12 → Console tab
- Tất cả requests/responses được log chi tiết

### Xem Network requests
- F12 → Network tab
- Filter: `booking`, `court`, `facility`
- Check status codes và response body

### Test thủ công từng endpoint

```javascript
// Trong browser console
const API_BASE = 'https://hyperpathetic-fugally-erin.ngrok-free.dev';

// 1. Login
const loginRes = await fetch(`${API_BASE}/auth/login`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email: 'manager1@badminton.com', password: 'password123'})
}).then(r => r.json());

const token = loginRes.access_token;

// 2. Get bookings
const bookingsRes = await fetch(`${API_BASE}/booking/manager/3/bookings?date=2025-11-27`, {
  headers: {'Authorization': `Bearer ${token}`, 'ngrok-skip-browser-warning': 'true'}
}).then(r => r.json());

console.log('Bookings:', bookingsRes.data);
```

## 📝 Notes

- Test suite tự động tạo và xóa test booking → Không làm ảnh hưởng data thật
- Mỗi lần chạy tạo 1 booking mới với note: `[TEST INTEGRATION] Auto-created...`
- Test 12 (Cleanup) sẽ cancel booking này
- Nếu test fail giữa chừng, có thể còn test bookings → Xóa manual bằng UI hoặc API

## 🎯 Success Criteria

Hệ thống considered "working" nếu:
- ✅ All 12 tests PASSED
- ✅ Duration < 15 seconds
- ✅ No console errors
- ✅ Test booking được tạo VÀ hiện trong list ngay sau đó (Test 7)

## 🐛 Known Issues

Nếu Test 7 fail → Đây chính là bug user đang gặp!
- Walk-in booking báo "thành công"
- Nhưng không xuất hiện trong booking list
- Root cause: API `get_bookings_by_facility` có vấn đề HOẶC database transaction chưa commit

→ Chạy test suite này để reproduce bug và debug!
