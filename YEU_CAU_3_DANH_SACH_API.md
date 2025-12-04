# YÊU CẦU 3: DANH SÁCH API HỆ THỐNG BSPORT

**Ngày tạo**: 27/11/2025  
**Hệ thống**: BSport - Hệ thống đặt sân Badminton  
**Architecture**: Microservices với API Gateway (Nginx)

---

## MỤC LỤC
1. [Auth Service - Xác thực & Phân quyền](#1-auth-service---xác-thực--phân-quyền)
2. [Facility Service - Quản lý Cơ sở](#2-facility-service---quản-lý-cơ-sở)
3. [Court Service - Quản lý Sân](#3-court-service---quản-lý-sân)
4. [Booking Service - Quản lý Đặt sân](#4-booking-service---quản-lý-đặt-sân)
5. [Billing Service - Quản lý Thanh toán](#5-billing-service---quản-lý-thanh-toán)
6. [Notification Service - Thông báo](#6-notification-service---thông-báo)
7. [Session Service - Quản lý Phiên](#7-session-service---quản-lý-phiên)
8. [Report Service - Báo cáo & Thống kê](#8-report-service---báo-cáo--thống-kê)

---

## 1. AUTH SERVICE - Xác thực & Phân quyền
**Base URL**: `http://localhost:8001`  
**Chức năng chính**: Xử lý đăng nhập, đăng ký, phát hành JWT token

### 1.1 Đăng nhập
**URI**: `POST /login`  
**Mô tả**: Xác thực thông tin đăng nhập và trả về JWT token để truy cập các API khác

**Input**:
```json
{
  "username": "string (email)",
  "password": "string"
}
```

**Output Success (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "role": "customer", // hoặc "manager"
  "fullname": "Nguyen Van A",
  "email": "customer@test.com"
}
```

**Output Error (401)**:
```json
{
  "detail": "Invalid credentials"
}
```

**Quyền truy cập**: Public (không cần token)

---

### 1.2 Đăng ký tài khoản
**URI**: `POST /register`  
**Mô tả**: Tạo tài khoản mới cho customer hoặc manager

**Input**:
```json
{
  "fullname": "string",
  "email": "string (email format)",
  "password": "string (min 6 ký tự)",
  "role": "customer" // hoặc "manager"
}
```

**Output Success (201)**:
```json
{
  "user_id": 1,
  "fullname": "Nguyen Van A",
  "email": "customer@test.com",
  "role": "customer",
  "created_at": "2025-11-27T10:00:00"
}
```

**Output Error (400)**:
```json
{
  "detail": "Email already exists"
}
```

**Quyền truy cập**: Public

---

### 1.3 Lấy OAuth2 Token
**URI**: `POST /token`  
**Mô tả**: Endpoint OAuth2 để lấy access token (alternative cho /login)

**Input** (Form Data):
```
username: "customer@test.com"
password: "test123"
```

**Output Success (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Quyền truy cập**: Public

---

### 1.4 Test Connection
**URI**: `GET /test`  
**Mô tả**: Kiểm tra kết nối Auth service

**Input**: Không có

**Output Success (200)**:
```json
{
  "message": "Auth service is running"
}
```

**Quyền truy cập**: Public

---

### 1.5 Test Database
**URI**: `GET /db-test`  
**Mô tả**: Kiểm tra kết nối database của Auth service

**Input**: Không có

**Output Success (200)**:
```json
{
  "status": "connected",
  "database": "DB_AUTH"
}
```

**Quyền truy cập**: Public

---

## 2. FACILITY SERVICE - Quản lý Cơ sở
**Base URL**: `http://localhost:8004`  
**Chức năng chính**: Quản lý thông tin các cơ sở thể thao (địa điểm có nhiều sân)

### 2.1 Lấy danh sách facilities
**URI**: `GET /facility`  
**Mô tả**: Lấy danh sách tất cả các cơ sở thể thao (dùng cho customer chọn địa điểm)

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Output Success (200)**:
```json
[
  {
    "id": 1,
    "name": "Victory Sports Complex",
    "address": "123 Nguyen Trai, Thanh Xuan",
    "location": "Ha Noi",
    "phone": "0123456789",
    "operating_hours": "06:00 - 23:00",
    "created_at": "2025-11-27T10:00:00"
  },
  {
    "id": 2,
    "name": "Champion Sports Center",
    "address": "456 Le Duan, Dong Da",
    "location": "Ha Noi",
    "phone": "0987654321",
    "operating_hours": "05:30 - 22:30"
  }
]
```

**Quyền truy cập**: Customer, Manager (cần JWT token)

---

### 2.2 Tạo facility mới
**URI**: `POST /facility`  
**Mô tả**: Manager tạo cơ sở thể thao mới

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Input** (Body):
```json
{
  "name": "Victory Sports Complex",
  "address": "123 Nguyen Trai, Thanh Xuan, Ha Noi",
  "location": "Ha Noi",
  "phone": "0123456789",
  "operating_hours": "06:00 - 23:00"
}
```

**Output Success (201)**:
```json
{
  "id": 1,
  "name": "Victory Sports Complex",
  "address": "123 Nguyen Trai, Thanh Xuan, Ha Noi",
  "location": "Ha Noi",
  "phone": "0123456789",
  "operating_hours": "06:00 - 23:00",
  "created_at": "2025-11-27T10:00:00"
}
```

**Output Error (403)**:
```json
{
  "detail": "Manager role required"
}
```

**Quyền truy cập**: Manager only

---

### 2.3 Lấy facilities của manager
**URI**: `GET /manager/facilities`  
**Mô tả**: Manager lấy danh sách các facility mà mình quản lý

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Output Success (200)**:
```json
[
  {
    "id": 1,
    "name": "Victory Sports Complex",
    "address": "123 Nguyen Trai",
    "location": "Ha Noi",
    "total_courts": 5,
    "active_courts": 4,
    "maintenance_courts": 1
  }
]
```

**Quyền truy cập**: Manager only

---

### 2.4 Lấy chi tiết facility
**URI**: `GET /facility/{facility_id}`  
**Mô tả**: Xem thông tin chi tiết 1 facility

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Input** (Path Parameters):
```
facility_id: integer (ID của facility)
```

**Output Success (200)**:
```json
{
  "id": 1,
  "name": "Victory Sports Complex",
  "address": "123 Nguyen Trai, Thanh Xuan, Ha Noi",
  "location": "Ha Noi",
  "phone": "0123456789",
  "operating_hours": "06:00 - 23:00",
  "description": "Cơ sở thể thao hiện đại với 5 sân cầu lông",
  "created_at": "2025-11-27T10:00:00"
}
```

**Output Error (404)**:
```json
{
  "detail": "Facility not found"
}
```

**Quyền truy cập**: Customer, Manager

---

### 2.5 Cập nhật facility
**URI**: `PUT /facility/{facility_id}`  
**Mô tả**: Manager cập nhật thông tin facility

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Input** (Body):
```json
{
  "name": "Victory Sports Complex - Updated",
  "address": "123 Nguyen Trai, Thanh Xuan, Ha Noi",
  "phone": "0123456789",
  "operating_hours": "05:30 - 23:30"
}
```

**Output Success (200)**:
```json
{
  "id": 1,
  "name": "Victory Sports Complex - Updated",
  "updated_at": "2025-11-27T11:00:00"
}
```

**Quyền truy cập**: Manager only

---

### 2.6 Xóa facility
**URI**: `DELETE /facility/{facility_id}`  
**Mô tả**: Manager xóa facility (cascade delete các court thuộc facility này)

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Output Success (200)**:
```json
{
  "message": "Facility deleted successfully"
}
```

**Quyền truy cập**: Manager only

---

### 2.7 Test Database
**URI**: `GET /db-test`  
**Mô tả**: Kiểm tra kết nối database

**Output Success (200)**:
```json
{
  "status": "connected",
  "database": "DB_FACILITY"
}
```

**Quyền truy cập**: Public

---

## 3. COURT SERVICE - Quản lý Sân
**Base URL**: `http://localhost:8006`  
**Chức năng chính**: Quản lý thông tin các sân cầu lông trong mỗi facility

### 3.1 Lấy danh sách tất cả courts
**URI**: `GET /court`  
**Mô tả**: Lấy danh sách tất cả các sân (customer dùng để chọn sân)

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Input** (Query Parameters - Optional):
```
facility_id: integer (lọc theo facility)
status: string (available, maintenance, unavailable)
```

**Output Success (200)**:
```json
[
  {
    "id": 1,
    "facility_id": 1,
    "facility_name": "Victory Sports Complex",
    "name": "Court B1",
    "surface_type": "Rubber",
    "hourly_rate": 100000,
    "status": "available",
    "description": "Sân cầu lông mặt cao su chất lượng cao"
  },
  {
    "id": 2,
    "facility_id": 1,
    "facility_name": "Victory Sports Complex",
    "name": "Court B2",
    "surface_type": "Vinyl",
    "hourly_rate": 120000,
    "status": "available"
  }
]
```

**Quyền truy cập**: Customer, Manager

---

### 3.2 Tạo court mới
**URI**: `POST /court`  
**Mô tả**: Manager tạo sân mới trong facility

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Input** (Body):
```json
{
  "facility_id": 1,
  "name": "Court B1",
  "surface_type": "Rubber", // Rubber, Vinyl, Wood
  "hourly_rate": 100000,
  "status": "available", // available, maintenance, unavailable
  "description": "Sân cầu lông mặt cao su"
}
```

**Output Success (201)**:
```json
{
  "id": 1,
  "facility_id": 1,
  "name": "Court B1",
  "surface_type": "Rubber",
  "hourly_rate": 100000,
  "status": "available",
  "created_at": "2025-11-27T10:00:00"
}
```

**Quyền truy cập**: Manager only

---

### 3.3 Lấy courts theo facility (Manager)
**URI**: `GET /manager/{facility_id}/courts`  
**Mô tả**: Manager xem danh sách courts trong facility của mình

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Input** (Path Parameters):
```
facility_id: integer
```

**Output Success (200)**:
```json
[
  {
    "id": 1,
    "name": "Court B1",
    "surface_type": "Rubber",
    "hourly_rate": 100000,
    "status": "available",
    "total_bookings_today": 5,
    "revenue_today": 500000
  },
  {
    "id": 2,
    "name": "Court B2",
    "surface_type": "Vinyl",
    "hourly_rate": 120000,
    "status": "maintenance",
    "total_bookings_today": 0,
    "revenue_today": 0
  }
]
```

**Quyền truy cập**: Manager only

---

### 3.4 Lấy chi tiết court
**URI**: `GET /court/{court_id}`  
**Mô tả**: Xem thông tin chi tiết của 1 sân

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Output Success (200)**:
```json
{
  "id": 1,
  "facility_id": 1,
  "facility_name": "Victory Sports Complex",
  "name": "Court B1",
  "surface_type": "Rubber",
  "hourly_rate": 100000,
  "status": "available",
  "description": "Sân cầu lông mặt cao su chất lượng cao",
  "amenities": ["Điều hòa", "Ánh sáng LED", "Lưới tiêu chuẩn"],
  "created_at": "2025-11-27T10:00:00"
}
```

**Quyền truy cập**: Customer, Manager

---

### 3.5 Cập nhật court
**URI**: `PUT /court/{court_id}`  
**Mô tả**: Manager cập nhật thông tin sân

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Input** (Body):
```json
{
  "name": "Court B1 - VIP",
  "hourly_rate": 150000,
  "status": "maintenance",
  "description": "Đang bảo trì"
}
```

**Output Success (200)**:
```json
{
  "id": 1,
  "name": "Court B1 - VIP",
  "hourly_rate": 150000,
  "status": "maintenance",
  "updated_at": "2025-11-27T11:00:00"
}
```

**Quyền truy cập**: Manager only

---

### 3.6 Xóa court
**URI**: `DELETE /court/{court_id}`  
**Mô tả**: Manager xóa sân (cần kiểm tra không có booking active)

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Output Success (200)**:
```json
{
  "message": "Court deleted successfully"
}
```

**Output Error (400)**:
```json
{
  "detail": "Cannot delete court with active bookings"
}
```

**Quyền truy cập**: Manager only

---

### 3.7 Kiểm tra tình trạng sân
**URI**: `GET /court/{court_id}/availability`  
**Mô tả**: Kiểm tra các khung giờ còn trống của sân

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Input** (Query Parameters):
```
date: string (YYYY-MM-DD, default: today)
```

**Output Success (200)**:
```json
{
  "court_id": 1,
  "court_name": "Court B1",
  "date": "2025-11-27",
  "available_slots": [
    {
      "start_time": "06:00",
      "end_time": "07:00",
      "price": 100000,
      "available": true
    },
    {
      "start_time": "07:00",
      "end_time": "08:00",
      "price": 100000,
      "available": false,
      "booking_id": 123
    },
    {
      "start_time": "08:00",
      "end_time": "09:00",
      "price": 100000,
      "available": true
    }
  ]
}
```

**Quyền truy cập**: Customer, Manager

---

### 3.8 Health Check
**URI**: `GET /health`  
**Mô tả**: Kiểm tra trạng thái service

**Output Success (200)**:
```json
{
  "status": "healthy",
  "service": "court"
}
```

**Quyền truy cập**: Public

---

### 3.9 Test Database
**URI**: `GET /db-test`  
**Mô tả**: Kiểm tra kết nối database

**Output Success (200)**:
```json
{
  "status": "connected",
  "database": "DB_COURT"
}
```

**Quyền truy cập**: Public

---

## 4. BOOKING SERVICE - Quản lý Đặt sân
**Base URL**: `http://localhost:8003`  
**Chức năng chính**: Xử lý đặt sân, quản lý trạng thái booking, timeline sân

### 4.1 Lấy danh sách bookings của user
**URI**: `GET /booking`  
**Mô tả**: Customer xem bookings của mình, Manager xem tất cả bookings

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Input** (Query Parameters - Optional):
```
status: string (pending, confirmed, cancelled, completed, expired)
facility_id: integer
date: string (YYYY-MM-DD)
```

**Output Success (200)**:
```json
[
  {
    "id": 1,
    "user_id": 5,
    "user_name": "Nguyen Van A",
    "facility_id": 1,
    "facility_name": "Victory Sports Complex",
    "court_id": 1,
    "court_name": "Court B1",
    "start_time": "2025-11-27T09:00:00",
    "end_time": "2025-11-27T10:00:00",
    "price": 100000,
    "status": "confirmed",
    "payment_status": "paid",
    "payment_method": "sepay",
    "note": "Đặt cho nhóm 4 người",
    "created_at": "2025-11-26T15:30:00"
  },
  {
    "id": 2,
    "user_id": 5,
    "facility_id": 1,
    "facility_name": "Victory Sports Complex",
    "court_id": 2,
    "court_name": "Court B2",
    "start_time": "2025-11-28T14:00:00",
    "end_time": "2025-11-28T15:00:00",
    "price": 120000,
    "status": "pending",
    "payment_status": "unpaid",
    "created_at": "2025-11-27T10:00:00"
  }
]
```

**Quyền truy cập**: Customer (xem của mình), Manager (xem tất cả)

---

### 4.2 Tạo booking mới
**URI**: `POST /booking`  
**Mô tả**: Customer đặt sân (có thể đặt nhiều slot cùng lúc)

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Input** (Body):
```json
{
  "facility_id": 1,
  "items": [
    {
      "court_id": 1,
      "start_time": "2025-11-28T09:00:00",
      "end_time": "2025-11-28T10:00:00",
      "price": 100000
    },
    {
      "court_id": 1,
      "start_time": "2025-11-28T10:00:00",
      "end_time": "2025-11-28T11:00:00",
      "price": 100000
    }
  ],
  "payment_method": "sepay", // cash, sepay, momo
  "note": "Đặt cho nhóm 4 người"
}
```

**Output Success (201)**:
```json
{
  "booking_id": 1,
  "user_id": 5,
  "facility_id": 1,
  "total_items": 2,
  "total_amount": 200000,
  "status": "pending",
  "payment_status": "unpaid",
  "payment_url": "https://sepay.vn/payment/abc123", // nếu chọn sepay
  "created_at": "2025-11-27T10:00:00"
}
```

**Output Error (409)**:
```json
{
  "detail": "Time slot already booked",
  "conflicting_slot": {
    "court_id": 1,
    "start_time": "2025-11-28T09:00:00",
    "end_time": "2025-11-28T10:00:00"
  }
}
```

**Output Error (400)**:
```json
{
  "detail": "Cannot book in the past"
}
```

**Quyền truy cập**: Customer, Manager

---

### 4.3 Lấy bookings theo facility và ngày (Manager)
**URI**: `GET /manager/{facility_id}/bookings`  
**Mô tả**: Manager xem tất cả bookings của facility theo ngày

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Input** (Path Parameters):
```
facility_id: integer
```

**Input** (Query Parameters):
```
date: string (YYYY-MM-DD, default: today)
```

**Output Success (200)**:
```json
{
  "facility_id": 1,
  "facility_name": "Victory Sports Complex",
  "date": "2025-11-27",
  "total_bookings": 15,
  "total_revenue": 1500000,
  "bookings": [
    {
      "id": 1,
      "user_name": "Nguyen Van A",
      "court_name": "Court B1",
      "start_time": "09:00",
      "end_time": "10:00",
      "status": "confirmed",
      "payment_status": "paid",
      "price": 100000
    },
    {
      "id": 2,
      "user_name": "Tran Thi B",
      "court_name": "Court B2",
      "start_time": "10:00",
      "end_time": "11:00",
      "status": "pending",
      "payment_status": "unpaid",
      "price": 120000
    }
  ]
}
```

**Quyền truy cập**: Manager only

---

### 4.4 Lấy time slots của court (Manager)
**URI**: `GET /manager/{court_id}/time_slots`  
**Mô tả**: Manager xem timeline của 1 sân (dùng cho màn hình manager_courts.js)

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Input** (Query Parameters):
```
date: string (YYYY-MM-DD, default: today)
```

**Output Success (200)**:
```json
{
  "court_id": 1,
  "court_name": "Court B1",
  "date": "2025-11-27",
  "time_slots": [
    {
      "hour": "06:00",
      "status": "available",
      "booking_id": null
    },
    {
      "hour": "07:00",
      "status": "available",
      "booking_id": null
    },
    {
      "hour": "08:00",
      "status": "available",
      "booking_id": null
    },
    {
      "hour": "09:00",
      "status": "confirmed",
      "booking_id": 1,
      "user_name": "Nguyen Van A",
      "payment_status": "paid"
    },
    {
      "hour": "10:00",
      "status": "pending",
      "booking_id": 2,
      "user_name": "Tran Thi B",
      "payment_status": "unpaid"
    },
    {
      "hour": "11:00",
      "status": "available",
      "booking_id": null
    }
  ]
}
```

**Quyền truy cập**: Manager only

---

### 4.5 Lấy chi tiết booking
**URI**: `GET /booking/{booking_id}`  
**Mô tả**: Xem thông tin chi tiết 1 booking

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Output Success (200)**:
```json
{
  "id": 1,
  "user_id": 5,
  "user_name": "Nguyen Van A",
  "user_email": "customer@test.com",
  "user_phone": "0123456789",
  "facility_id": 1,
  "facility_name": "Victory Sports Complex",
  "court_id": 1,
  "court_name": "Court B1",
  "start_time": "2025-11-27T09:00:00",
  "end_time": "2025-11-27T10:00:00",
  "price": 100000,
  "status": "confirmed",
  "payment_status": "paid",
  "payment_method": "sepay",
  "payment_reference": "PAY123456",
  "note": "Đặt cho nhóm 4 người",
  "created_at": "2025-11-26T15:30:00",
  "updated_at": "2025-11-27T08:00:00"
}
```

**Output Error (403)**:
```json
{
  "detail": "You don't have permission to view this booking"
}
```

**Quyền truy cập**: Customer (booking của mình), Manager (mọi booking)

---

### 4.6 Cập nhật trạng thái booking
**URI**: `PUT /booking/{booking_id}`  
**Mô tả**: Manager cập nhật trạng thái booking (pending → confirmed, cancelled)

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Input** (Body):
```json
{
  "status": "confirmed" // pending, confirmed, cancelled
}
```

**Output Success (200)**:
```json
{
  "id": 1,
  "status": "confirmed",
  "updated_at": "2025-11-27T10:00:00",
  "message": "Booking status updated successfully"
}
```

**Output Error (403)**:
```json
{
  "detail": "Manager role required"
}
```

**Quyền truy cập**: Manager only

**Lưu ý**: 
- Manager có thể update từ bất kỳ status nào (kể cả cancelled → confirmed)
- Customer không thể update status (chỉ có thể cancel)

---

### 4.7 Hủy booking
**URI**: `POST /booking/{booking_id}/cancel`  
**Mô tả**: Customer hoặc Manager hủy booking

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Input** (Body):
```json
{
  "reason": "Có việc đột xuất không thể đến"
}
```

**Output Success (200)**:
```json
{
  "id": 1,
  "status": "cancelled",
  "cancelled_at": "2025-11-27T10:00:00",
  "cancellation_reason": "Có việc đột xuất không thể đến",
  "refund_status": "pending", // nếu đã thanh toán
  "message": "Booking cancelled successfully"
}
```

**Output Error (400)**:
```json
{
  "detail": "Cannot cancel booking less than 2 hours before start time"
}
```

**Quyền truy cập**: Customer (booking của mình), Manager (mọi booking)

---

### 4.8 Xóa booking
**URI**: `DELETE /booking/{booking_id}`  
**Mô tả**: Manager xóa booking khỏi hệ thống

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Output Success (200)**:
```json
{
  "message": "Booking deleted successfully"
}
```

**Quyền truy cập**: Manager only

---

### 4.9 Cập nhật payment status
**URI**: `POST /booking/{booking_id}/payment-status`  
**Mô tả**: Billing service gọi endpoint này khi payment thành công

**Input** (Headers):
```
Authorization: Bearer {service_token}
```

**Input** (Body):
```json
{
  "status": "paid", // paid, failed, refunded
  "reference_id": "PAY123456",
  "gateway_payload": {
    "transaction_id": "TXN789",
    "payment_method": "sepay",
    "amount": 100000
  }
}
```

**Output Success (200)**:
```json
{
  "booking_id": 1,
  "payment_status": "paid",
  "updated_at": "2025-11-27T10:00:00"
}
```

**Quyền truy cập**: Internal service only

---

### 4.10 Health Check
**URI**: `GET /health`  
**Mô tả**: Kiểm tra trạng thái service

**Output Success (200)**:
```json
{
  "status": "healthy",
  "service": "booking"
}
```

**Quyền truy cập**: Public

---

### 4.11 Test Database
**URI**: `GET /db-test`  
**Mô tả**: Kiểm tra kết nối database

**Output Success (200)**:
```json
{
  "status": "connected",
  "database": "DB_BOOKING"
}
```

**Quyền truy cập**: Public

---

## 5. BILLING SERVICE - Quản lý Thanh toán
**Base URL**: `http://localhost:8002`  
**Chức năng chính**: Xử lý thanh toán, tạo invoice, tích hợp SePay payment gateway

### 5.1 Tạo invoice
**URI**: `POST /billing`  
**Mô tả**: Tạo hóa đơn thanh toán cho booking

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Input** (Body):
```json
{
  "booking_id": 1,
  "user_id": 5,
  "amount": 100000,
  "payment_method": "sepay", // cash, sepay, momo
  "description": "Booking Court B1 - Victory Sports: 27/11/2025 09:00-10:00"
}
```

**Output Success (201)**:
```json
{
  "invoice_id": 1,
  "booking_id": 1,
  "user_id": 5,
  "amount": 100000,
  "payment_method": "sepay",
  "status": "pending", // pending, paid, failed, refunded
  "created_at": "2025-11-27T10:00:00",
  "payment_url": "https://sepay.vn/payment/abc123" // nếu dùng sepay
}
```

**Quyền truy cập**: Customer, Manager

---

### 5.2 Lấy lịch sử thanh toán
**URI**: `GET /billing/history`  
**Mô tả**: Customer xem lịch sử thanh toán của mình, Manager xem tất cả

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Input** (Query Parameters - Optional):
```
status: string (pending, paid, failed, refunded)
from_date: string (YYYY-MM-DD)
to_date: string (YYYY-MM-DD)
```

**Output Success (200)**:
```json
[
  {
    "invoice_id": 1,
    "booking_id": 1,
    "user_name": "Nguyen Van A",
    "amount": 100000,
    "payment_method": "sepay",
    "status": "paid",
    "paid_at": "2025-11-27T09:30:00",
    "transaction_id": "TXN123456",
    "description": "Booking Court B1"
  },
  {
    "invoice_id": 2,
    "booking_id": 2,
    "user_name": "Nguyen Van A",
    "amount": 120000,
    "payment_method": "cash",
    "status": "pending",
    "created_at": "2025-11-27T10:00:00",
    "description": "Booking Court B2"
  }
]
```

**Quyền truy cập**: Customer (của mình), Manager (tất cả)

---

### 5.3 Thanh toán invoice
**URI**: `POST /billing/{invoice_id}/pay`  
**Mô tả**: Xử lý thanh toán invoice (cash hoặc redirect đến gateway)

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Input** (Body):
```json
{
  "payment_method": "sepay" // cash, sepay, momo
}
```

**Output Success (200)**:
```json
{
  "invoice_id": 1,
  "status": "paid", // hoặc "processing" nếu dùng gateway
  "payment_url": "https://sepay.vn/payment/abc123", // nếu dùng gateway
  "paid_at": "2025-11-27T10:00:00"
}
```

**Output Error (400)**:
```json
{
  "detail": "Invoice already paid"
}
```

**Quyền truy cập**: Customer (invoice của mình), Manager

---

### 5.4 Lấy chi tiết invoice
**URI**: `GET /billing/{invoice_id}`  
**Mô tả**: Xem thông tin chi tiết invoice

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Output Success (200)**:
```json
{
  "invoice_id": 1,
  "booking_id": 1,
  "user_id": 5,
  "user_name": "Nguyen Van A",
  "amount": 100000,
  "payment_method": "sepay",
  "status": "paid",
  "description": "Booking Court B1 - Victory Sports: 27/11/2025 09:00-10:00",
  "transaction_id": "TXN123456",
  "paid_at": "2025-11-27T09:30:00",
  "created_at": "2025-11-27T09:00:00"
}
```

**Quyền truy cập**: Customer (invoice của mình), Manager

---

### 5.5 Webhook SePay
**URI**: `POST /billing/{invoice_id}/webhook`  
**Mô tả**: SePay gateway gọi endpoint này khi có thay đổi payment status

**Input** (Body):
```json
{
  "invoice_id": 1,
  "transaction_id": "TXN123456",
  "status": "success", // success, failed
  "amount": 100000,
  "signature": "abc123xyz456"
}
```

**Output Success (200)**:
```json
{
  "message": "Webhook processed successfully"
}
```

**Quyền truy cập**: SePay gateway only (verify signature)

---

### 5.6 Tạo payment link SePay
**URI**: `POST /billing/{invoice_id}/sepay/create-payment`  
**Mô tả**: Tạo payment link cho SePay gateway

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Input** (Body):
```json
{
  "return_url": "http://localhost/payment/return",
  "cancel_url": "http://localhost/payment/cancel"
}
```

**Output Success (200)**:
```json
{
  "payment_url": "https://sepay.vn/payment/abc123",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUh...",
  "expires_at": "2025-11-27T11:00:00"
}
```

**Quyền truy cập**: Customer (invoice của mình)

---

### 5.7 SePay Return URL
**URI**: `GET /billing/sepay/return`  
**Mô tả**: SePay redirect về endpoint này sau khi user hoàn tất payment

**Input** (Query Parameters):
```
status: string (success, failed, cancel)
invoice_id: integer
transaction_id: string
```

**Output Success (200)**:
```html
<!-- Redirect to frontend success/fail page -->
```

**Quyền truy cập**: Public (from SePay)

---

### 5.8 SePay Return POST
**URI**: `POST /billing/sepay/return`  
**Mô tả**: SePay POST payment result

**Input** (Body):
```json
{
  "status": "success",
  "invoice_id": 1,
  "transaction_id": "TXN123456",
  "amount": 100000
}
```

**Output Success (200)**:
```json
{
  "message": "Payment processed successfully"
}
```

**Quyền truy cập**: SePay gateway only

---

### 5.9 SePay IPN (Instant Payment Notification)
**URI**: `POST /billing/sepay/ipn`  
**Mô tả**: SePay gửi IPN khi payment hoàn tất

**Input** (Body):
```json
{
  "invoice_id": 1,
  "transaction_id": "TXN123456",
  "status": "paid",
  "amount": 100000,
  "signature": "abc123xyz456"
}
```

**Output Success (200)**:
```json
{
  "message": "IPN processed successfully"
}
```

**Quyền truy cập**: SePay gateway only (verify signature)

---

### 5.10 Health Check
**URI**: `GET /`  
**Mô tả**: Kiểm tra trạng thái service

**Output Success (200)**:
```json
{
  "status": "healthy",
  "service": "billing"
}
```

**Quyền truy cập**: Public

---

## 6. NOTIFICATION SERVICE - Thông báo
**Base URL**: `http://localhost:8007`  
**Chức năng chính**: Gửi email notification (verify account, booking confirmation)

### 6.1 Health Check
**URI**: `GET /health`  
**Mô tả**: Kiểm tra trạng thái service

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Output Success (200)**:
```json
{
  "status": "healthy",
  "service": "notification"
}
```

**Quyền truy cập**: Customer, Manager

---

### 6.2 Gửi email verify registration
**URI**: `POST /notification/send-email-verify-register`  
**Mô tả**: Gửi email xác thực tài khoản sau khi đăng ký

**Input** (Headers):
```
Authorization: Bearer {service_token}
```

**Input** (Body):
```json
{
  "email": "customer@test.com",
  "fullname": "Nguyen Van A",
  "verification_code": "ABC123"
}
```

**Output Success (200)**:
```json
{
  "message": "Verification email sent successfully",
  "email": "customer@test.com",
  "sent_at": "2025-11-27T10:00:00"
}
```

**Output Error (500)**:
```json
{
  "detail": "Failed to send email",
  "error": "SMTP connection failed"
}
```

**Quyền truy cập**: Internal service only

---

### 6.3 Gửi email xác nhận booking
**URI**: `POST /notification/send-booking-confirmed`  
**Mô tả**: Gửi email xác nhận booking sau khi thanh toán thành công

**Input** (Headers):
```
Authorization: Bearer {service_token}
```

**Input** (Body):
```json
{
  "booking_id": 1,
  "user_email": "customer@test.com",
  "scheduled_time": "Court B1 - Victory Sports: 27/11/2025 09:00 - 10:00",
  "court_name": "Court B1"
}
```

**Output Success (200)**:
```json
{
  "message": "Booking confirmation email sent successfully",
  "booking_id": 1,
  "email": "customer@test.com",
  "sent_at": "2025-11-27T10:00:00"
}
```

**Output Error (422)**:
```json
{
  "detail": "Invalid email format"
}
```

**Quyền truy cập**: Internal service only

**Lưu ý**: 
- Service chấp nhận cả `user_email` và `email` field
- Gmail API token cần được configure đúng trong `credentials_desktop_apps.json`

---

## 7. SESSION SERVICE - Quản lý Phiên
**Base URL**: `http://localhost:8005`  
**Chức năng chính**: Quản lý session/token của user (track login sessions)

### 7.1 Health Check
**URI**: `GET /health`  
**Mô tả**: Kiểm tra trạng thái service

**Output Success (200)**:
```json
{
  "status": "healthy",
  "service": "session"
}
```

**Quyền truy cập**: Public

---

### 7.2 Test Database
**URI**: `GET /db-test`  
**Mô tả**: Kiểm tra kết nối database

**Output Success (200)**:
```json
{
  "status": "connected",
  "database": "DB_SESSION"
}
```

**Quyền truy cập**: Public

---

### 7.3 Tạo session
**URI**: `POST /session`  
**Mô tả**: Tạo session mới khi user login

**Input** (Headers):
```
Authorization: Bearer {service_token}
```

**Input** (Body):
```json
{
  "user_id": 5,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-11-28T10:00:00",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

**Output Success (201)**:
```json
{
  "session_id": 1,
  "user_id": 5,
  "created_at": "2025-11-27T10:00:00",
  "expires_at": "2025-11-28T10:00:00"
}
```

**Quyền truy cập**: Internal service only

---

### 7.4 Lấy sessions của user
**URI**: `GET /session/user/{user_id}`  
**Mô tả**: Xem tất cả active sessions của user

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Output Success (200)**:
```json
[
  {
    "session_id": 1,
    "user_id": 5,
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0)",
    "created_at": "2025-11-27T10:00:00",
    "expires_at": "2025-11-28T10:00:00",
    "is_active": true
  },
  {
    "session_id": 2,
    "user_id": 5,
    "ip_address": "192.168.1.101",
    "user_agent": "Mozilla/5.0 (iPhone)",
    "created_at": "2025-11-26T15:00:00",
    "expires_at": "2025-11-27T15:00:00",
    "is_active": true
  }
]
```

**Quyền truy cập**: Customer (sessions của mình), Manager (mọi session)

---

### 7.5 Xóa session (Logout)
**URI**: `DELETE /session/{session_id}`  
**Mô tả**: Xóa session khi user logout

**Input** (Headers):
```
Authorization: Bearer {token}
```

**Output Success (200)**:
```json
{
  "message": "Session deleted successfully",
  "session_id": 1
}
```

**Output Error (404)**:
```json
{
  "detail": "Session not found"
}
```

**Quyền truy cập**: Customer (session của mình), Manager

---

## 8. REPORT SERVICE - Báo cáo & Thống kê
**Base URL**: `http://localhost:8008`  
**Chức năng chính**: Tạo báo cáo, biểu đồ thống kê cho manager

### 8.1 Health Check
**URI**: `GET /health`  
**Mô tả**: Kiểm tra trạng thái service

**Output Success (200)**:
```json
{
  "status": "healthy",
  "service": "report"
}
```

**Quyền truy cập**: Public

---

### 8.2 Biểu đồ playtime của court
**URI**: `GET /report/manager/report-playtime-plot/court={court_id}`  
**Mô tả**: Manager xem biểu đồ thống kê giờ sử dụng của sân

**Input** (Headers):
```
Authorization: Bearer {manager_token}
```

**Input** (Path Parameters):
```
court_id: integer
```

**Input** (Query Parameters - Optional):
```
from_date: string (YYYY-MM-DD, default: 30 days ago)
to_date: string (YYYY-MM-DD, default: today)
```

**Output Success (200)**:
```
Content-Type: image/png
[Binary image data - biểu đồ playtime]
```

**Mô tả biểu đồ**:
- Trục X: Ngày (từ from_date đến to_date)
- Trục Y: Số giờ sử dụng
- Hiển thị: Số giờ confirmed + completed mỗi ngày

**Output Error (403)**:
```json
{
  "detail": "Manager role required"
}
```

**Output Error (404)**:
```json
{
  "detail": "Court not found"
}
```

**Quyền truy cập**: Manager only

**Lưu ý**:
- Chỉ tính bookings có status = confirmed hoặc completed
- Không tính pending, cancelled, expired
- Biểu đồ được generate bằng matplotlib

---

## TỔNG KẾT

### Tổng số API: 53 endpoints

**Phân loại theo service**:
1. **Auth Service**: 5 APIs
2. **Facility Service**: 7 APIs  
3. **Court Service**: 9 APIs
4. **Booking Service**: 11 APIs
5. **Billing Service**: 10 APIs
6. **Notification Service**: 3 APIs
7. **Session Service**: 5 APIs
8. **Report Service**: 2 APIs

### Phân loại theo quyền truy cập:
- **Public** (không cần token): 10 APIs
- **Customer**: 18 APIs
- **Manager Only**: 15 APIs
- **Both Customer & Manager**: 7 APIs
- **Internal Service Only**: 3 APIs

### Phân loại theo HTTP Method:
- **GET**: 26 APIs (49%)
- **POST**: 18 APIs (34%)
- **PUT**: 5 APIs (9%)
- **DELETE**: 4 APIs (8%)

### Authentication Flow:
1. User gọi `POST /login` → nhận JWT token
2. Gửi token trong header: `Authorization: Bearer {token}`
3. Mỗi service verify token và check role (customer/manager)

### Payment Flow:
1. Customer tạo booking → `POST /booking`
2. Hệ thống tạo invoice → `POST /billing`
3. Customer chọn payment method (sepay/cash)
4. Nếu sepay: redirect đến payment gateway
5. SePay callback → `POST /billing/sepay/ipn`
6. Update booking payment status → `POST /booking/{id}/payment-status`
7. Gửi email confirmation → `POST /notification/send-booking-confirmed`

### Manager Workflow:
1. Login với role=manager
2. Xem facilities → `GET /manager/facilities`
3. Xem courts → `GET /manager/{facility_id}/courts`
4. Xem bookings → `GET /manager/{facility_id}/bookings?date=2025-11-27`
5. Xem timeline → `GET /manager/{court_id}/time_slots?date=2025-11-27`
6. Update booking status → `PUT /booking/{id}` (status: pending/confirmed/cancelled)
7. Xem báo cáo → `GET /report/manager/report-playtime-plot/court={id}`

### Customer Workflow:
1. Login → `POST /login`
2. Xem facilities → `GET /facility`
3. Xem courts → `GET /court?facility_id=1`
4. Check availability → `GET /court/{id}/availability?date=2025-11-27`
5. Tạo booking → `POST /booking`
6. Thanh toán → `POST /billing/{invoice_id}/sepay/create-payment`
7. Xem bookings → `GET /booking`
8. Hủy booking (nếu cần) → `POST /booking/{id}/cancel`

### Status Management:
**Booking Status**:
- `pending`: Mới tạo, chờ xác nhận
- `confirmed`: Manager đã xác nhận (hiển thị màu đỏ)
- `cancelled`: Đã hủy (ẩn ở customer view)
- `completed`: Đã hoàn thành
- `expired`: Hết hạn

**Payment Status**:
- `unpaid`: Chưa thanh toán
- `paid`: Đã thanh toán
- `failed`: Thanh toán thất bại
- `refunded`: Đã hoàn tiền

**Color Coding** (Frontend):
- Pending: Màu vàng (#fef3c7)
- Confirmed: Màu đỏ (#fca5a5)
- Cancelled: Trắng/ẩn
- Available: Xanh lá

---

**Prepared by**: AI Assistant  
**Date**: 27/11/2025  
**Version**: 1.0  
**Purpose**: Yêu cầu 3 - Danh sách API hệ thống BSport
