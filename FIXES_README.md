# 🔧 CÁC VẤN ĐỀ ĐÃ SỬA - HƯỚNG DẪN NHANH

## 📋 Tổng Quan

Dự án có 2 vấn đề chính đã được sửa:

1. ✅ **UI không load được data** (Manager & Customer views)
2. ✅ **Thanh toán SePay không hoạt động**

---

## 🚀 CÁCH SỬ DỤNG NHANH

### Bước 1: Rebuild các services đã sửa
```bash
./rebuild_fixed_services.sh
```

### Bước 2: (Nếu dùng ngrok) Cập nhật URL mới
```bash
./update_ngrok_url.sh https://your-new-url.ngrok-free.dev
```

Xong! Giờ có thể test lại ứng dụng.

---

## 📚 TÀI LIỆU CHI TIẾT

| File | Mô tả |
|------|-------|
| **FIX_ISSUES_GUIDE.md** | Hướng dẫn chi tiết từng bước |
| **ISSUE_SUMMARY.md** | Phân tích kỹ các vấn đề |
| **QUICK_REFERENCE.txt** | Thẻ tham chiếu nhanh |
| **rebuild_fixed_services.sh** | Script tự động rebuild |
| **update_ngrok_url.sh** | Script cập nhật ngrok URL |

---

## 🐛 CÁC VẤN ĐỀ ĐÃ SỬA

### 1. API Gateway Routing
**Vấn đề:** Route `/billing` bị duplicate → 404 errors  
**Sửa:** `APIGateway/main.py`
- Loại bỏ prefix duplicate
- Thêm CORS middleware
- Thêm error handling + logging

### 2. SePay Return URL
**Vấn đề:** Redirect về `/customer.html` (không tồn tại)  
**Sửa:** `Billing/service/billing_service.py`
- Đổi thành `/ui/Homepage/homepage.html`

### 3. Frontend API Client
**Vấn đề:** Thiếu ngrok bypass headers  
**Sửa:** `UI/Homepage/apiClient.js` và `payment_handler.js`
- Thêm header `ngrok-skip-browser-warning`

---

## 🔍 DEBUG

### Xem logs
```bash
# API Gateway
docker-compose logs -f apigateway

# Billing
docker-compose logs -f billing_api

# Tất cả
docker-compose logs -f
```

### Test health
```bash
# Billing health
curl http://localhost/billing/

# Auth health  
curl http://localhost/auth/
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

### Khi dùng Ngrok:
1. **MỖI KHI restart ngrok** → URL mới
2. Phải cập nhật URL vào 2 files:
   - `Billing/core/.env`
   - `UI/Homepage/homepage.html`
3. Hoặc dùng script: `./update_ngrok_url.sh <URL>`

### Sau khi sửa code:
```bash
./rebuild_fixed_services.sh
```

### Clear browser cache:
- Chrome: `Ctrl+Shift+R`
- Mac: `Cmd+Shift+R`

---

## ✅ CHECKLIST TEST

### Manager View:
- [ ] Login với role "manager"
- [ ] Vào tab "Quản Trị"
- [ ] Chọn facility
- [ ] Thấy danh sách courts
- [ ] Thấy danh sách bookings

### Customer View:
- [ ] Login với role "customer"
- [ ] Vào tab "Đặt & Điều Phối"
- [ ] Chọn facility và date
- [ ] Thấy booking calendar
- [ ] Có thể đặt sân mới

### Payment:
- [ ] Tạo booking
- [ ] Click "Xác nhận đặt sân"
- [ ] Redirect sang SePay
- [ ] Hoàn thành thanh toán
- [ ] Redirect về homepage
- [ ] Thấy thông báo success
- [ ] Booking status = confirmed

---

## 🆘 CẦN HELP?

1. Đọc **FIX_ISSUES_GUIDE.md** (chi tiết nhất)
2. Xem **QUICK_REFERENCE.txt** (commands nhanh)
3. Check logs: `docker-compose logs -f`
4. Browser DevTools → Console + Network tabs

---

## 📊 FILES THAY ĐỔI

```
Modified:
  ✅ APIGateway/main.py
  ✅ APIGateway/requirements.txt
  ✅ Billing/service/billing_service.py
  ✅ UI/Homepage/apiClient.js
  ✅ UI/Homepage/payment_handler.js

Created:
  📄 FIX_ISSUES_GUIDE.md
  📄 ISSUE_SUMMARY.md
  📄 QUICK_REFERENCE.txt
  📄 THIS_README.md
  🔧 rebuild_fixed_services.sh
  🔧 update_ngrok_url.sh
```

---

**👉 BẮT ĐẦU:** Chạy `./rebuild_fixed_services.sh` để rebuild và test!
