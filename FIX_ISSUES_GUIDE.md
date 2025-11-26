# HƯỚNG DẪN SỬA LỖI DỰ ÁN

## Tóm Tắt Các Vấn Đề Đã Sửa

### 1. ❌ Vấn Đề: UI Không Load Được Data (Manager & Customer)

**Nguyên nhân:**
- API Gateway routing sai: Route `/billing` bị duplicate prefix → `/billing/billing/...` → 404
- Thiếu CORS headers
- Thiếu ngrok bypass headers

**Đã sửa:**
- ✅ `APIGateway/main.py`: Sửa route billing, thêm CORS middleware, thêm error handling và logging
- ✅ `UI/Homepage/apiClient.js`: Thêm header `ngrok-skip-browser-warning`
- ✅ `APIGateway/requirements.txt`: Thêm version cụ thể cho dependencies

### 2. ❌ Vấn Đề: Thanh Toán SePay Không Hoạt Động

**Nguyên nhân:**
- Return URL sai: redirect về `/customer.html` thay vì `/ui/Homepage/homepage.html`
- Backend URL trong payment_handler không đúng (dùng localhost thay vì ngrok URL)
- Thiếu ngrok bypass header khi gọi API

**Đã sửa:**
- ✅ `Billing/service/billing_service.py`: Sửa redirect URL từ `/customer.html` → `/ui/Homepage/homepage.html`
- ✅ `UI/Homepage/payment_handler.js`: 
  - Sửa BACKEND_URL để ưu tiên `window.CONFIG.BACKEND_PUBLIC_URL`
  - Thêm header `ngrok-skip-browser-warning` khi create SePay payment

## Các Bước Deploy Lại

### Bước 1: Rebuild API Gateway
```bash
cd /Users/zitqan/Documents/FINAL_SOA
docker-compose stop apigateway
docker-compose rm -f apigateway
docker-compose build apigateway
docker-compose up -d apigateway
```

### Bước 2: Rebuild Billing Service (vì sửa return URL)
```bash
docker-compose stop billing_api
docker-compose rm -f billing_api
docker-compose build billing_api
docker-compose up -d billing_api
```

### Bước 3: Restart Nginx (để load lại static files)
```bash
docker-compose restart nginx
```

### Bước 4: Kiểm tra logs
```bash
# Xem logs API Gateway
docker-compose logs -f apigateway

# Xem logs Billing
docker-compose logs -f billing_api

# Xem logs Nginx
docker-compose logs -f nginx
```

## Kiểm Tra Ngrok URL

⚠️ **QUAN TRỌNG**: Mỗi khi restart ngrok, phải cập nhật URL mới!

### Bước 1: Lấy URL mới từ ngrok
```bash
# Nếu đang chạy ngrok, xem output để lấy URL
# Ví dụ: https://xyz-abc-def.ngrok-free.dev
```

### Bước 2: Cập nhật vào 2 file:

**File 1: `Billing/core/.env`**
```env
BACKEND_PUBLIC_URL=https://YOUR-NEW-NGROK-URL.ngrok-free.dev
```

**File 2: `UI/Homepage/homepage.html`**
```html
<script>
    window.CONFIG = {
        BACKEND_PUBLIC_URL: 'https://YOUR-NEW-NGROK-URL.ngrok-free.dev',
        SEPAY_ENABLED: true
    };
</script>
```

### Bước 3: Rebuild services
```bash
docker-compose restart billing_api nginx
```

## Test Các Chức Năng

### Test 1: Load Data Manager
1. Đăng nhập với tài khoản manager
2. Vào tab "Quản Trị"
3. Chọn cơ sở từ dropdown
4. **Kỳ vọng**: Hiển thị danh sách sân và bookings

### Test 2: Load Data Customer
1. Đăng nhập với tài khoản customer
2. Vào tab "Đặt & Điều Phối"
3. Chọn cơ sở và ngày
4. **Kỳ vọng**: Hiển thị lịch đặt sân

### Test 3: Thanh Toán SePay
1. Đặt 1 booking
2. Click "Xác nhận đặt sân"
3. **Kỳ vọng**: Redirect sang trang SePay
4. Hoàn thành thanh toán trên SePay
5. **Kỳ vọng**: Redirect về homepage với thông báo thành công

## Debug Các Lỗi Thường Gặp

### Lỗi 1: Still getting 404 errors
**Giải pháp:**
```bash
# Xem logs API Gateway để biết exact URL được gọi
docker-compose logs -f apigateway | grep "Proxying"

# Kiểm tra route trong API Gateway
docker exec -it api_gateway cat /app/main.py
```

### Lỗi 2: SePay không redirect về
**Giải pháp:**
1. Kiểm tra `BACKEND_PUBLIC_URL` trong `.env` có đúng không
2. Kiểm tra logs billing service:
```bash
docker-compose logs -f billing_api | grep "SePay"
```

### Lỗi 3: CORS errors
**Giải pháp:**
```bash
# Rebuild API Gateway với CORS middleware
docker-compose up -d --build apigateway
```

### Lỗi 4: Manager không hiển thị facilities
**Kiểm tra:**
1. User có role "manager" không?
2. Manager có được assign facilities không?
```bash
# Vào database và check
docker exec -it facility_db mysql -uroot -proot DB_FACILITY -e "SELECT * FROM facility_managers;"
```

## URLs Quan Trọng

### Development (Local)
- Frontend: http://localhost/ui/Homepage/homepage.html
- API Gateway: http://localhost:80
- Auth API: http://localhost:8001
- Billing API: http://localhost:8002
- Booking API: http://localhost:8003

### Production (Ngrok)
- Frontend: https://YOUR-NGROK-URL.ngrok-free.dev/ui/Homepage/homepage.html
- All APIs: https://YOUR-NGROK-URL.ngrok-free.dev/{service}/...

## Checklist Trước Khi Test

- [ ] Tất cả containers đang chạy (`docker-compose ps`)
- [ ] Ngrok đang chạy và URL đã cập nhật vào 2 files
- [ ] Đã rebuild API Gateway và Billing service
- [ ] Browser cache đã clear (Ctrl+Shift+R)
- [ ] Check console logs không có errors

## Contact & Support

Nếu vẫn gặp vấn đề, check:
1. Browser Console (F12)
2. API Gateway logs: `docker-compose logs -f apigateway`
3. Billing logs: `docker-compose logs -f billing_api`
4. Network tab trong Chrome DevTools

---

**Cuối cùng**: Nhớ commit các thay đổi!
```bash
git add .
git commit -m "Fix: API Gateway routing, SePay return URL, and add ngrok headers"
git push
```
