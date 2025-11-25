README – Kiến trúc Microservice với Nginx, Database và JWT
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
- Nếu dùng cổng public/ngrok cho SePay, cấu hình front:
  - `localStorage.soa_payment_method = "sepay"`
  - `localStorage.soa_return_url = "https://hyperpathetic-fugally-erin.ngrok-free.dev/ui/Homepage/homepage.html"` (hoặc domain ngrok bạn đang dùng)
  - `localStorage.soa_api_base = "http://localhost"` (gọi API qua Nginx nội bộ)

3. Cấu trúc folder service
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
