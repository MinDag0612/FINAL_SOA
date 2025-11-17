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

