README – Kiến trúc Microservice với Nginx, Database và JWT

TAI LIEU THAM KHAO:
- QUICK_START_NGROK.md - Hướng dẫn nhanh chạy hệ thống với Ngrok
- NGROK_SETUP_GUIDE.md - Hướng dẫn chi tiết setup Ngrok
- YEU_CAU_3_DANH_SACH_API.md - Danh sách đầy đủ 53 APIs

QUICK START:
Chạy hệ thống với Static Ngrok Domain (khuyến nghị):
    ./start_with_static_ngrok.sh

Hoặc với Random Domain (tự động update config):
    ./start_with_random_ngrok.sh

Hoặc chỉ localhost (không payment callback):
    docker-compose up -d

============================================================================================

1. Cách hoạt động của Nginx

    - Trong dự án này, Nginx đóng vai trò là reverse proxy:

    - Nginx nghe trên port 80 (host) và nhận tất cả request từ client.

    - Dựa trên URL path, Nginx chuyển tiếp request tới API Gateway hoặc trực tiếp tới các service khác nếu cần.

Ví dụ config Nginx:

location /auth/ {
    proxy_pass http://apigateway/auth/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}


Giải thích:

    - Request http://localhost/auth/login → Nginx chuyển tới http://apigateway/auth/login.

    - proxy_set_header giữ nguyên thông tin client (IP, host, …) để API Gateway hoặc service xử lý.

    - Các service phía sau không cần mở port ra ngoài, Nginx quản lý tập trung.


Client
   |
   v
[Nginx - port 80]
   |
   v
[API Gateway - port 5000]
   |
   +--> Auth API - port 8001
   +--> Billing API - port 8002
   +--> Booking API - port 8003
   +--> Court API - port 8004
   +--> Facility API - port 8005
   +--> Session API - port 8006

---------------------------------------------------------------------------------------------

2. Các port của database và API trong Docker Compose
************************************************************************************************

Trong kiến trúc microservice, mỗi service có database riêng và API riêng:

Service	API Port	DB Port (host)	DB Container Name

Auth	    8001	3306	auth_db
Billing	    8002	3307	bill_db
Booking	    8003	3308	booking_db
Court	    8004	3309	court_db
Facility	8005	3310	facility_db
Session	    8006	3311	session_db

Lưu ý:

API container sẽ được Nginx hoặc API Gateway forward request.

DB container chỉ cần mở port nếu muốn kết nối trực tiếp từ host (ví dụ Workbench).

Trong Docker network, các service kết nối database bằng tên container (auth_db, bill_db, …) và port nội bộ là 3306.

---------------------------------------------------------------------------------------------

Front-end
************************************************************************************************
- Nginx phục vụ UI tĩnh ở port 80. Truy cập:
  - Trang đăng nhập/đăng ký: http://localhost/ui/Login/Login.html
  - Trang dashboard khách hàng: http://localhost/ui/Homepage/homepage.html
- API từ UI gọi qua Nginx cùng cổng 80 (base: http://localhost), các path /auth/, /booking/, /billing/, /court/, /facility/, /session/ đã được proxy sẵn tới API Gateway.

---------------------------------------------------------------------------------------------

4. CẤU HÌNH VÀ SỬ DỤNG NGROK (Cho SePay Payment Gateway)
************************************************************************************************

Ngrok được dùng để expose localhost ra internet, cần thiết cho SePay callback (IPN/Return URL).

CAC FILE CAN CAU HINH NGROK URL:
============================================

1. **Billing/core/.env** (Backend - QUAN TRỌNG NHẤT):
   ```
   BACKEND_PUBLIC_URL=https://your-domain.ngrok-free.dev
   FRONTEND_URL=https://your-domain.ngrok-free.dev/ui
   ```

2. **UI/Homepage/homepage.html** (Frontend config):
   ```javascript
   window.CONFIG = {
       BACKEND_PUBLIC_URL: 'https://your-domain.ngrok-free.dev',
       ...
   }
   ```

CACH CHAY NGROK - BUOC CHI TIET:
============================================

** Bước 1: Start Docker Compose **
```bash
cd /Users/zitqan/Documents/FINAL_SOA
docker-compose up -d
```

** Bước 2: Khởi động Ngrok **
```bash
# Mở terminal mới, chạy ngrok expose port 80
ngrok http 80

# Hoặc nếu có ngrok config với domain tĩnh:
ngrok http 80 --domain=your-static-domain.ngrok-free.dev
```

Ngrok sẽ hiển thị:
```
Forwarding  https://abc-def-ghi.ngrok-free.dev -> http://localhost:80
```

** Bước 3: Copy ngrok URL và cập nhật config **
```bash
# Sử dụng script tự động (KHUYẾN NGHỊ)
./update_ngrok_url.sh https://abc-def-ghi.ngrok-free.dev

# Script sẽ tự động:
# - Backup các file cũ
# - Update BACKEND_PUBLIC_URL trong Billing/core/.env
# - Update BACKEND_PUBLIC_URL trong UI/Homepage/homepage.html
# - Hỏi bạn có muốn rebuild services không
```

** Bước 4: Rebuild services để áp dụng config **
```bash
# Cách 1: Rebuild tất cả services (nhanh nhất)
./rebuild_fixed_services.sh

# Cách 2: Chỉ restart services cần thiết
docker-compose restart billing_api nginx

# Cách 3: Rebuild từng service riêng
docker-compose up -d --build billing_api
docker-compose restart nginx
```

** Bước 5: Verify cấu hình **
```bash
# Kiểm tra .env đã update chưa
cat Billing/core/.env | grep BACKEND_PUBLIC_URL

# Kiểm tra HTML đã update chưa
cat UI/Homepage/homepage.html | grep BACKEND_PUBLIC_URL

# Test truy cập qua ngrok
curl https://your-domain.ngrok-free.dev/health -H "ngrok-skip-browser-warning: true"
```

WORKFLOW KHI TAT MAY VA CHAY LAI:
============================================

** Kịch bản: Ngrok domain thay đổi sau khi restart **

1. **Tắt máy / Stop Docker:**
   ```bash
   docker-compose down
   # Ngrok sẽ tự tắt khi tắt terminal
   ```

2. **Mở máy lại và khởi động:**
   ```bash
   # Bước 1: Start Docker
   cd /Users/zitqan/Documents/FINAL_SOA
   docker-compose up -d
   
   # Bước 2: Start Ngrok (DOMAIN MỚI SẼ KHÁC)
   ngrok http 80
   # Output: https://NEW-RANDOM-DOMAIN.ngrok-free.dev
   
   # Bước 3: Update config với domain mới
   ./update_ngrok_url.sh https://NEW-RANDOM-DOMAIN.ngrok-free.dev
   
   # Bước 4: Rebuild services
   ./rebuild_fixed_services.sh
   ```

3. **Kiểm tra hệ thống:**
   ```bash
   # Test backend health
   curl https://NEW-RANDOM-DOMAIN.ngrok-free.dev/health \
     -H "ngrok-skip-browser-warning: true"
   
   # Test frontend
   open https://NEW-RANDOM-DOMAIN.ngrok-free.dev/ui/Homepage/homepage.html
   ```

GIAI PHAP: SU DUNG NGROK STATIC DOMAIN (KHUYEN NGHI)
============================================

Để KHÔNG phải update config mỗi lần restart, dùng Ngrok Static Domain:

** Bước 1: Đăng ký Ngrok Account (Free/Paid) **
- Truy cập: https://dashboard.ngrok.com/
- Lấy authtoken: https://dashboard.ngrok.com/get-started/your-authtoken

** Bước 2: Config Ngrok với authtoken **
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

** Bước 3: Claim Static Domain **
- Free tier: 1 static domain (ví dụ: my-app-name.ngrok-free.dev)
- Paid tier: Custom domains

** Bước 4: Sử dụng Static Domain **
```bash
# Start ngrok với domain tĩnh
ngrok http 80 --domain=my-app-name.ngrok-free.dev
```

** Bước 5: Config một lần duy nhất **
```bash
# Chỉ cần chạy 1 LẦN với static domain
./update_ngrok_url.sh https://my-app-name.ngrok-free.dev
./rebuild_fixed_services.sh

# Sau này mỗi lần restart chỉ cần:
docker-compose up -d
ngrok http 80 --domain=my-app-name.ngrok-free.dev
# KHÔNG CẦN UPDATE CONFIG LẠI!
```

CHECKLIST: NGROK DA HOAT DONG DUNG?
============================================

[OK] Ngrok đang chạy và hiển thị Forwarding URL
[OK] File Billing/core/.env có BACKEND_PUBLIC_URL đúng
[OK] File UI/Homepage/homepage.html có BACKEND_PUBLIC_URL đúng
[OK] Docker services đã được rebuild sau khi update config
[OK] Truy cập https://your-domain.ngrok-free.dev/health trả về 200
[OK] Truy cập https://your-domain.ngrok-free.dev/ui/Homepage/homepage.html hiển thị UI
[OK] Payment flow hoạt động (tạo booking → thanh toán → callback từ SePay)

LUU Y QUAN TRONG:
============================================

1. **Ngrok Free**: Domain thay đổi mỗi lần restart → Phải update config lại
2. **Ngrok Static Domain**: Domain không đổi → Chỉ config 1 lần
3. **Rebuild services**: BẮT BUỘC sau khi update .env, nếu không services vẫn dùng config cũ
4. **Nginx cần restart**: Để apply config mới từ volume mount
5. **Cache browser**: Clear cache nếu frontend vẫn dùng URL cũ (Ctrl+Shift+R)
6. **SePay Test Mode**: Đang dùng sandbox, không cần domain thật cho production

TROUBLESHOOTING:
============================================

** Vấn đề 1: Payment callback không về **
→ Kiểm tra BACKEND_PUBLIC_URL trong Billing/core/.env
→ Verify SePay đang gọi đúng domain ngrok
→ Check logs: docker-compose logs -f billing_api

** Vấn đề 2: Frontend gọi localhost thay vì ngrok **
→ Check window.CONFIG trong homepage.html
→ Clear browser cache (Ctrl+Shift+R)
→ Verify HTML đã được reload (check View Source)

** Vấn đề 3: Ngrok "ERR_NGROK_6024" (domain changed) **
→ Update config với domain mới
→ Hoặc dùng static domain để tránh issue này

** Vấn đề 4: Services không apply config mới **
→ Rebuild services: ./rebuild_fixed_services.sh
→ Hoặc: docker-compose restart billing_api nginx

** Vấn đề 5: Mixed content error (HTTP/HTTPS) **
→ Đảm bảo tất cả URLs dùng HTTPS khi chạy qua ngrok
→ Check không có hardcoded http:// URLs trong frontend

5. Cấu trúc folder service
************************************************************************************************
service_name/
├── controller/
├── service/
├── repository/
├── messaging/  # sẽ thêm sau khi kết nối Kafka
└── model/

Client (React / API Gateway)
        ↓
[ Controller Layer ]   ← Flask routes, REST API endpoints
        ↓
[ Service Layer ]      ← Xử lý nghiệp vụ (logic chính)
        ↓
[ Repository Layer ]   ← Truy xuất và ghi dữ liệu DB

HOW TO USE JWT

- Khi deploy copy jwt_shared vào container
- Copy lại
jwt_services = jwt_services()

def get_current_user(token: str = Depends(jwt_services.oauth2_scheme)):
    try:
        payload = jwt_services.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload  # hoặc chỉ return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

vào file main, hàm nào cần auth mới được dùng thì thêm 

            --Depends(get_current_user)--
ví dụ 
        @app.get("/health")
        def health_check(user: dict = Depends(get_current_user)):

nếu cần tất cả dùng --router--
Jwt chưa data của user

HOW TO USE Kafka
    1. copy file message dán vào service đó

    2. **send_event** là hàm để gửi data topic như tên hòm thư, data là thông tin gửi đi
    -> Khi nào dùng gọi lại, khong cần chạy thường xuyên

    3. **consume_messages** là hàm liệt kê và ánh xạ các topic <-> định nghĩa hàm phục vụ
    -> Cần chạy suốt đề nghe từ hộp thư nên phải có **@app.on_event("startup")** trong file main và định nghĩa **start_kafka_consumer**

Lí do nó vẫn đáp ứng độc lập:
    - Có thể gửi bình thường mà không có bên nhận
    - Kafka được chạy ở một domain riêng không gọi là service. Đây là nơi luu và xử lí topic + data
    - Khi gửi khong gửi đối tượng hay hàm mà chỉ gửi data. Khong bị coupling
