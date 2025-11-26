# 🔍 PHÂN TÍCH VẤN ĐỀ DỰ ÁN - TÓM TẮT

## 📊 Tổng Quan

Dự án của bạn có **2 vấn đề chính**:

1. ❌ **UI không load được data** (Manager & Customer)
2. ❌ **Thanh toán SePay không hoạt động**

---

## 🐛 CHI TIẾT CÁC VẤN ĐỀ

### Vấn Đề #1: UI Không Load Data

#### Triệu chứng:
- Manager view: Không hiển thị danh sách sân và bookings
- Customer view: Không load được danh sách facilities, courts
- Console hiển thị lỗi 404 hoặc CORS errors

#### Nguyên nhân gốc rễ:

**1. API Gateway Routing Sai:**
```python
# File: APIGateway/main.py (SAI - TRƯỚC KHI SỬA)
SERVICE_URLS = {
    "billing": "http://billing_api:8002/billing",  # ← Đã có /billing
}

# Khi frontend gọi: /billing/history
# API Gateway proxy thành: http://billing_api:8002/billing/history
# Nhưng nginx đã forward: /billing/history → /billing/billing/history
# → 404 NOT FOUND
```

**2. Thiếu CORS Headers:**
- API Gateway không có CORS middleware
- Requests từ browser bị block

**3. Ngrok Warning:**
- Khi dùng ngrok, cần header `ngrok-skip-browser-warning: true`
- Không có header này → ngrok trả về HTML warning page thay vì JSON

#### Đã sửa:
✅ **APIGateway/main.py**
- Bỏ prefix `/billing` khỏi SERVICE_URLS
- Thêm CORS middleware
- Thêm error handling và logging
- Thêm logic xử lý riêng cho billing service

✅ **UI/Homepage/apiClient.js**
- Thêm header `ngrok-skip-browser-warning` cho mọi request

✅ **APIGateway/requirements.txt**
- Thêm version cụ thể cho dependencies

---

### Vấn Đề #2: Thanh Toán SePay Không Hoạt Động

#### Triệu chứng:
- Click "Xác nhận đặt sân" → không redirect sang SePay
- Hoặc: Redirect sang SePay nhưng sau khi thanh toán không quay về homepage
- Hoặc: Quay về homepage nhưng không hiển thị thông báo thành công

#### Nguyên nhân gốc rễ:

**1. Return URL Sai:**
```python
# File: Billing/service/billing_service.py (SAI - TRƯỚC KHI SỬA)
"redirect_url": f"/customer.html?payment=success{redirect_booking}"
# → File /customer.html không tồn tại!
# → Đúng phải là: /ui/Homepage/homepage.html
```

**2. Backend URL Không Đúng:**
```javascript
// File: UI/Homepage/payment_handler.js (SAI - TRƯỚC KHI SỬA)
const BACKEND_URL = window.location.origin.replace(/:\d+$/, '');
// → Khi chạy qua ngrok, window.location.origin = http://localhost
// → Phải dùng: window.CONFIG.BACKEND_PUBLIC_URL
```

**3. Thiếu Ngrok Bypass Header:**
- Khi gọi API create payment, không có header `ngrok-skip-browser-warning`
- → Ngrok block request

#### Đã sửa:
✅ **Billing/service/billing_service.py**
- Sửa redirect URL: `/customer.html` → `/ui/Homepage/homepage.html`

✅ **UI/Homepage/payment_handler.js**
- Ưu tiên dùng `window.CONFIG.BACKEND_PUBLIC_URL`
- Thêm header `ngrok-skip-browser-warning` khi create payment

---

## 📝 FLOW HOẠT ĐỘNG SAU KHI SỬA

### Flow 1: Load Data (Manager/Customer)

```
Browser → apiClient.js (thêm ngrok header)
  ↓
Nginx :80 → /billing/...
  ↓
API Gateway :5000 (xử lý đúng route, thêm CORS)
  ↓
Billing Service :8002/billing/...
  ↓
Response (JSON) → Browser
```

### Flow 2: Thanh Toán SePay

```
1. User click "Xác nhận đặt sân"
   ↓
2. PaymentHandler.processPayment() gọi:
   POST {BACKEND_PUBLIC_URL}/billing/{invoice_id}/sepay/create-payment
   (với header: ngrok-skip-browser-warning)
   ↓
3. Billing Service tạo payment URL với:
   - returnUrl: {BACKEND_PUBLIC_URL}/billing/sepay/return?booking_id={id}
   - notificationUrl: {BACKEND_PUBLIC_URL}/billing/sepay/ipn
   ↓
4. Browser redirect sang SePay checkout page
   ↓
5. User thanh toán trên SePay
   ↓
6. SePay redirect về: {returnUrl}
   ↓
7. Billing Service xử lý return:
   - Cập nhật invoice status = paid
   - Notify booking service
   - Redirect sang: /ui/Homepage/homepage.html?payment=success&booking_id={id}
   ↓
8. Homepage load và hiển thị thông báo thành công
```

---

## 🎯 ĐIỂM QUAN TRỌNG NHẤT

### ⚠️ Ngrok URL
**Mỗi khi restart ngrok, PHẢI cập nhật URL vào 2 file:**

1. `Billing/core/.env`
```env
BACKEND_PUBLIC_URL=https://YOUR-NEW-NGROK-URL.ngrok-free.dev
```

2. `UI/Homepage/homepage.html`
```html
<script>
    window.CONFIG = {
        BACKEND_PUBLIC_URL: 'https://YOUR-NEW-NGROK-URL.ngrok-free.dev',
        SEPAY_ENABLED: true
    };
</script>
```

### 🔄 Sau khi cập nhật URL
```bash
# Chạy script rebuild
./rebuild_fixed_services.sh
```

---

## ✅ CHECKLIST TEST

### Test Load Data:
- [ ] Manager: Đăng nhập → Tab "Quản Trị" → Chọn cơ sở → Thấy danh sách sân
- [ ] Manager: Thấy danh sách bookings của ngày hiện tại
- [ ] Customer: Tab "Đặt & Điều Phối" → Chọn cơ sở & ngày → Thấy lịch sân

### Test Thanh Toán:
- [ ] Đặt 1 booking mới
- [ ] Click "Xác nhận đặt sân"
- [ ] Redirect sang trang SePay (URL bắt đầu với https://pay-sandbox.sepay.vn)
- [ ] Hoàn thành thanh toán (hoặc cancel)
- [ ] Redirect về homepage
- [ ] Thấy thông báo success/failed
- [ ] Booking status đã update (confirmed/cancelled)

---

## 🛠️ TOOLS DEBUG

### 1. Check Logs
```bash
# API Gateway
docker-compose logs -f apigateway | grep "Proxying"

# Billing
docker-compose logs -f billing_api | grep "SePay"

# Nginx
docker-compose logs -f nginx
```

### 2. Browser DevTools
- **Console**: Xem lỗi JavaScript
- **Network**: Xem status code của requests
- **Application → Local Storage**: Kiểm tra `soa_auth`, `soa_api_base`

### 3. Check Service Health
```bash
# All services
docker-compose ps

# Specific service
docker exec -it api_gateway curl http://localhost:5000/health
```

---

## 📦 FILES ĐÃ SỬA

```
✅ APIGateway/main.py           - Sửa routing, thêm CORS, error handling
✅ APIGateway/requirements.txt  - Thêm versions
✅ Billing/service/billing_service.py  - Sửa redirect URLs
✅ UI/Homepage/apiClient.js     - Thêm ngrok bypass header
✅ UI/Homepage/payment_handler.js  - Sửa BACKEND_URL, thêm headers

📄 FIX_ISSUES_GUIDE.md         - Hướng dẫn chi tiết
📄 ISSUE_SUMMARY.md            - File này
🔧 rebuild_fixed_services.sh   - Script tự động rebuild
```

---

## 🎓 BÀI HỌC RÚT RA

1. **Routing phải nhất quán**: API Gateway, Nginx, và service URLs phải match với nhau
2. **Ngrok cần bypass header**: Luôn thêm `ngrok-skip-browser-warning: true`
3. **CORS quan trọng**: Frontend gọi API từ domain khác cần CORS
4. **URL paths phải chính xác**: `/customer.html` vs `/ui/Homepage/homepage.html`
5. **Config phải sync**: Ngrok URL phải update vào cả frontend và backend

---

**🚀 SẴN SÀNG REBUILD? Chạy:**
```bash
./rebuild_fixed_services.sh
```
