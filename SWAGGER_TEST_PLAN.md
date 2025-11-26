# SWAGGER API TEST PLAN - BSport System

## Tổng quan
- **Hệ thống**: BSport - Hệ thống đặt sân Badminton
- **Architecture**: Microservices
- **API Gateway**: Nginx (http://localhost)
- **Ngày tạo**: 27/11/2025

---

## 1. AUTH SERVICE (Port 8001)
**Base URL**: `http://localhost:8001`

### 1.1 POST /login
**Mục đích**: Đăng nhập và lấy JWT token

**Test Cases**:
```json
// TC1: Login thành công - Customer
{
  "username": "customer@test.com",
  "password": "test123"
}
Expected: 200, token returned

// TC2: Login thành công - Manager  
{
  "username": "manager@test.com",
  "password": "manager123"
}
Expected: 200, token với role="manager"

// TC3: Sai password
{
  "username": "customer@test.com",
  "password": "wrong"
}
Expected: 401 Unauthorized

// TC4: Email không tồn tại
{
  "username": "notexist@test.com",
  "password": "test123"
}
Expected: 401 Unauthorized
```

### 1.2 POST /register
**Mục đích**: Đăng ký tài khoản mới

**Test Cases**:
```json
// TC1: Đăng ký customer thành công
{
  "fullname": "Test User",
  "email": "newuser@test.com",
  "password": "password123",
  "role": "customer"
}
Expected: 201 Created

// TC2: Email đã tồn tại
{
  "fullname": "Test User 2",
  "email": "customer@test.com",
  "password": "password123",
  "role": "customer"
}
Expected: 400 Bad Request

// TC3: Password quá ngắn
{
  "fullname": "Test User",
  "email": "test3@test.com",
  "password": "123",
  "role": "customer"
}
Expected: 422 Validation Error

// TC4: Email không hợp lệ
{
  "fullname": "Test User",
  "email": "invalid-email",
  "password": "password123",
  "role": "customer"
}
Expected: 422 Validation Error
```

### 1.3 POST /token
**Mục đích**: Lấy token (OAuth2 format)

**Test Cases**:
```
// TC1: Get token thành công
Form data:
- username: customer@test.com
- password: test123

Expected: 200, access_token returned
```

---

## 2. FACILITY SERVICE (Port 8004)

**Base URL**: `http://localhost:8004`
**Authentication**: Bearer Token required

### 2.1 GET /facility
**Mục đích**: Lấy danh sách facilities

**Test Cases**:
```
// TC1: Không có token
Headers: None
Expected: 401 Unauthorized

// TC2: Customer với token hợp lệ
Headers: Authorization: Bearer {token}
Expected: 200, list of facilities

// TC3: Manager với token hợp lệ
Headers: Authorization: Bearer {manager_token}
Expected: 200, list of facilities
```

### 2.2 POST /facility
**Mục đích**: Tạo facility mới (Manager only)

**Test Cases**:
```json
// TC1: Manager tạo facility thành công
Headers: Authorization: Bearer {manager_token}
{
  "name": "Test Sports Complex",
  "address": "123 Test Street",
  "location": "Ha Noi",
  "phone": "0123456789",
  "operating_hours": "06:00 - 23:00"
}
Expected: 201 Created

// TC2: Customer không có quyền
Headers: Authorization: Bearer {customer_token}
{...same body...}
Expected: 403 Forbidden
```

### 2.3 GET /manager/facilities
**Mục đích**: Manager lấy danh sách facilities của mình

**Test Cases**:
```
// TC1: Manager lấy facilities
Headers: Authorization: Bearer {manager_token}
Expected: 200, list of facilities

// TC2: Customer không có quyền
Headers: Authorization: Bearer {customer_token}
Expected: 403 Forbidden
```

### 2.4 GET /facility/{facility_id}
**Mục đích**: Lấy chi tiết 1 facility

**Test Cases**:
```
// TC1: Facility tồn tại
GET /facility/1
Expected: 200, facility details

// TC2: Facility không tồn tại
GET /facility/99999
Expected: 404 Not Found
```

### 2.5 PUT /facility/{facility_id}
**Mục đích**: Cập nhật facility (Manager only)

**Test Cases**:
```json
// TC1: Manager cập nhật thành công
PUT /facility/1
Headers: Authorization: Bearer {manager_token}
{
  "name": "Updated Name",
  "address": "New Address"
}
Expected: 200 OK

// TC2: Customer không có quyền
Expected: 403 Forbidden
```

### 2.6 DELETE /facility/{facility_id}
**Mục đích**: Xóa facility (Manager only)

**Test Cases**:
```
// TC1: Manager xóa facility
DELETE /facility/1
Headers: Authorization: Bearer {manager_token}
Expected: 200 OK

// TC2: Xóa facility không tồn tại
DELETE /facility/99999
Expected: 404 Not Found
```

---

## 3. COURT SERVICE (Port 8006)

**Base URL**: `http://localhost:8006`
**Authentication**: Bearer Token required

### 3.1 GET /court
**Mục đích**: Lấy danh sách tất cả courts

**Test Cases**:
```
// TC1: Lấy danh sách courts
Headers: Authorization: Bearer {token}
Expected: 200, list of courts

// TC2: Không có token
Expected: 401 Unauthorized
```

### 3.2 POST /court
**Mục đích**: Tạo court mới (Manager only)

**Test Cases**:
```json
// TC1: Manager tạo court thành công
Headers: Authorization: Bearer {manager_token}
{
  "facility_id": 1,
  "name": "Court B1",
  "surface_type": "Rubber",
  "hourly_rate": 100000,
  "status": "available"
}
Expected: 201 Created

// TC2: Thiếu required fields
{
  "facility_id": 1,
  "name": "Court B2"
}
Expected: 422 Validation Error

// TC3: facility_id không tồn tại
{
  "facility_id": 99999,
  "name": "Court B3",
  "surface_type": "Vinyl",
  "hourly_rate": 100000
}
Expected: 404 Not Found
```

### 3.3 GET /manager/{facility_id}/courts
**Mục đích**: Manager lấy courts theo facility

**Test Cases**:
```
// TC1: Lấy courts của facility
GET /manager/1/courts
Headers: Authorization: Bearer {manager_token}
Expected: 200, list of courts

// TC2: Facility không có court nào
GET /manager/999/courts
Expected: 200, empty list []
```

### 3.4 GET /court/{court_id}
**Mục đích**: Lấy chi tiết 1 court

**Test Cases**:
```
// TC1: Court tồn tại
GET /court/1
Expected: 200, court details

// TC2: Court không tồn tại
GET /court/99999
Expected: 404 Not Found
```

### 3.5 PUT /court/{court_id}
**Mục đích**: Cập nhật court (Manager only)

**Test Cases**:
```json
// TC1: Update court thành công
PUT /court/1
Headers: Authorization: Bearer {manager_token}
{
  "name": "Court B1 Updated",
  "hourly_rate": 120000,
  "status": "maintenance"
}
Expected: 200 OK

// TC2: Update court không tồn tại
PUT /court/99999
Expected: 404 Not Found
```

### 3.6 DELETE /court/{court_id}
**Mục đích**: Xóa court (Manager only)

**Test Cases**:
```
// TC1: Xóa court thành công
DELETE /court/1
Expected: 200 OK

// TC2: Customer không có quyền
Headers: Authorization: Bearer {customer_token}
Expected: 403 Forbidden
```

### 3.7 GET /court/{court_id}/availability
**Mục đích**: Kiểm tra tình trạng sân

**Test Cases**:
```
// TC1: Kiểm tra availability
GET /court/1/availability?date=2025-11-27
Expected: 200, availability status

// TC2: Không truyền date
GET /court/1/availability
Expected: 200, today's availability
```

---

## 4. BOOKING SERVICE (Port 8003)

**Base URL**: `http://localhost:8003`
**Authentication**: Bearer Token required

### 4.1 GET /booking
**Mục đích**: Lấy danh sách bookings của user

**Test Cases**:
```
// TC1: Customer lấy bookings của mình
Headers: Authorization: Bearer {customer_token}
Expected: 200, list of bookings

// TC2: Manager lấy tất cả bookings
Headers: Authorization: Bearer {manager_token}
Expected: 200, all bookings

// TC3: Không có token
Expected: 401 Unauthorized
```

### 4.2 POST /booking
**Mục đích**: Tạo booking mới

**Test Cases**:
```json
// TC1: Tạo booking thành công
Headers: Authorization: Bearer {customer_token}
{
  "facility_id": 1,
  "items": [
    {
      "court_id": 1,
      "start_time": "2025-11-28T09:00:00",
      "end_time": "2025-11-28T10:00:00",
      "price": 100000
    }
  ],
  "payment_method": "cash",
  "note": "Test booking"
}
Expected: 201 Created, booking_id returned

// TC2: Booking slot đã được đặt
{
  "facility_id": 1,
  "items": [
    {
      "court_id": 1,
      "start_time": "2025-11-28T09:00:00",
      "end_time": "2025-11-28T10:00:00",
      "price": 100000
    }
  ]
}
Expected: 409 Conflict

// TC3: Thời gian không hợp lệ (end < start)
{
  "facility_id": 1,
  "items": [
    {
      "court_id": 1,
      "start_time": "2025-11-28T10:00:00",
      "end_time": "2025-11-28T09:00:00",
      "price": 100000
    }
  ]
}
Expected: 422 Validation Error

// TC4: Court không tồn tại
{
  "facility_id": 1,
  "items": [
    {
      "court_id": 99999,
      "start_time": "2025-11-28T09:00:00",
      "end_time": "2025-11-28T10:00:00",
      "price": 100000
    }
  ]
}
Expected: 404 Not Found
```

### 4.3 GET /manager/{facility_id}/bookings
**Mục đích**: Manager lấy bookings theo facility và date

**Test Cases**:
```
// TC1: Lấy bookings hôm nay
GET /manager/1/bookings?date=2025-11-27
Headers: Authorization: Bearer {manager_token}
Expected: 200, list of bookings

// TC2: Customer không có quyền
Headers: Authorization: Bearer {customer_token}
Expected: 403 Forbidden

// TC3: Không truyền date
GET /manager/1/bookings
Expected: 200, today's bookings
```

### 4.4 GET /booking/{booking_id}
**Mục đích**: Lấy chi tiết booking

**Test Cases**:
```
// TC1: User lấy booking của mình
GET /booking/1
Headers: Authorization: Bearer {customer_token}
Expected: 200, booking details

// TC2: User lấy booking của người khác
GET /booking/999
Expected: 403 Forbidden (nếu không phải manager)

// TC3: Manager lấy bất kỳ booking nào
GET /booking/1
Headers: Authorization: Bearer {manager_token}
Expected: 200, booking details
```

### 4.5 PUT /booking/{booking_id}
**Mục đích**: Cập nhật booking status

**Test Cases**:
```json
// TC1: Manager update status thành confirmed
PUT /booking/1
Headers: Authorization: Bearer {manager_token}
{
  "status": "confirmed"
}
Expected: 200 OK

// TC2: Manager update từ cancelled về confirmed
PUT /booking/2
{
  "status": "confirmed"
}
Expected: 200 OK (manager có thể update từ mọi status)

// TC3: Customer update booking của người khác
Headers: Authorization: Bearer {customer_token}
Expected: 403 Forbidden

// TC4: Update status không hợp lệ
{
  "status": "invalid_status"
}
Expected: 422 Validation Error
```

### 4.6 POST /booking/{booking_id}/cancel
**Mục đích**: Hủy booking

**Test Cases**:
```json
// TC1: User hủy booking của mình
POST /booking/1/cancel
Headers: Authorization: Bearer {customer_token}
{
  "reason": "Có việc đột xuất"
}
Expected: 200 OK

// TC2: Manager hủy booking
POST /booking/2/cancel
Headers: Authorization: Bearer {manager_token}
{
  "reason": "Maintenance"
}
Expected: 200 OK

// TC3: Hủy booking đã cancelled
POST /booking/1/cancel
Expected: 400 Bad Request "Already cancelled"
```

### 4.7 DELETE /booking/{booking_id}
**Mục đích**: Xóa booking (Manager only)

**Test Cases**:
```
// TC1: Manager xóa booking
DELETE /booking/1
Headers: Authorization: Bearer {manager_token}
Expected: 200 OK

// TC2: Customer không có quyền
Headers: Authorization: Bearer {customer_token}
Expected: 403 Forbidden
```

### 4.8 POST /booking/{booking_id}/payment-status
**Mục đích**: Cập nhật payment status

**Test Cases**:
```json
// TC1: Cập nhật payment thành công
POST /booking/1/payment-status
{
  "status": "paid",
  "reference_id": "PAY123456",
  "gateway_payload": {"transaction_id": "TXN123"}
}
Expected: 200 OK

// TC2: Status không hợp lệ
{
  "status": "invalid"
}
Expected: 422 Validation Error
```

### 4.9 GET /manager/{court_id}/time_slots
**Mục đích**: Lấy time slots của court

**Test Cases**:
```
// TC1: Lấy time slots
GET /manager/1/time_slots?date=2025-11-27
Expected: 200, available time slots

// TC2: Không truyền date
GET /manager/1/time_slots
Expected: 200, today's time slots
```

---

## 5. BILLING SERVICE (Port 8002)

**Base URL**: `http://localhost:8002`
**Authentication**: Bearer Token required

### 5.1 POST /billing
**Mục đích**: Tạo invoice

**Test Cases**:
```json
// TC1: Tạo invoice thành công
{
  "booking_id": 1,
  "user_id": 1,
  "amount": 100000,
  "payment_method": "sepay",
  "description": "Booking Court B1"
}
Expected: 201 Created, invoice_id returned

// TC2: Booking không tồn tại
{
  "booking_id": 99999,
  "user_id": 1,
  "amount": 100000
}
Expected: 404 Not Found
```

### 5.2 GET /billing/history
**Mục đích**: Lấy billing history của user

**Test Cases**:
```
// TC1: Lấy history
Headers: Authorization: Bearer {customer_token}
Expected: 200, list of invoices

// TC2: Manager lấy tất cả history
Headers: Authorization: Bearer {manager_token}
Expected: 200, all invoices
```

### 5.3 POST /billing/{invoice_id}/pay
**Mục đích**: Thanh toán invoice

**Test Cases**:
```json
// TC1: Pay invoice thành công
POST /billing/1/pay
{
  "payment_method": "sepay"
}
Expected: 200 OK

// TC2: Invoice đã paid
POST /billing/1/pay
Expected: 400 Bad Request "Already paid"
```

### 5.4 GET /billing/{invoice_id}
**Mục đích**: Lấy chi tiết invoice

**Test Cases**:
```
// TC1: Lấy invoice
GET /billing/1
Expected: 200, invoice details

// TC2: Invoice không tồn tại
GET /billing/99999
Expected: 404 Not Found
```

### 5.5 POST /billing/{invoice_id}/sepay/create-payment
**Mục đích**: Tạo payment link SePay

**Test Cases**:
```json
// TC1: Tạo payment link
POST /billing/1/sepay/create-payment
{
  "return_url": "http://localhost/payment/return",
  "cancel_url": "http://localhost/payment/cancel"
}
Expected: 200, payment_url returned

// TC2: Invoice đã paid
Expected: 400 Bad Request
```

### 5.6 GET /billing/sepay/return
**Mục đích**: SePay return callback

**Test Cases**:
```
// TC1: Payment success
GET /billing/sepay/return?status=success&invoice_id=1
Expected: 200, redirect to success page

// TC2: Payment failed
GET /billing/sepay/return?status=failed&invoice_id=1
Expected: 200, redirect to failed page
```

### 5.7 POST /billing/sepay/ipn
**Mục đích**: SePay IPN webhook

**Test Cases**:
```json
// TC1: Valid IPN
{
  "invoice_id": 1,
  "status": "paid",
  "transaction_id": "TXN123456"
}
Expected: 200 OK

// TC2: Invalid signature
Expected: 401 Unauthorized
```

---

## 6. NOTIFICATION SERVICE (Port 8007)

**Base URL**: `http://localhost:8007`
**Authentication**: Bearer Token required

### 6.1 GET /health
**Mục đích**: Health check

**Test Cases**:
```
// TC1: Health check
GET /health
Headers: Authorization: Bearer {token}
Expected: 200 OK
```

### 6.2 POST /notification/send-email-verify-register
**Mục đích**: Gửi email verify registration

**Test Cases**:
```json
// TC1: Gửi email verify
{
  "email": "test@example.com",
  "fullname": "Test User"
}
Expected: 200 OK

// TC2: Email không hợp lệ
{
  "email": "invalid-email",
  "fullname": "Test User"
}
Expected: 422 Validation Error
```

### 6.3 POST /notification/send-booking-confirmed
**Mục đích**: Gửi email xác nhận booking

**Test Cases**:
```json
// TC1: Gửi email confirmation
{
  "booking_id": 1,
  "user_email": "customer@test.com",
  "scheduled_time": "Court B1 - Victory Sports: 27/11/2025 09:00 - 10:00",
  "court_name": "Court B1"
}
Expected: 200 OK

// TC2: Thiếu required fields
{
  "booking_id": 1
}
Expected: 422 Validation Error
```

---

## 7. SESSION SERVICE (Port 8005)

**Base URL**: `http://localhost:8005`
**Authentication**: Bearer Token required

### 7.1 GET /health
**Mục đích**: Health check

**Test Cases**:
```
// TC1: Health check
GET /health
Expected: 200 OK
```

### 7.2 POST /session
**Mục đích**: Tạo session mới

**Test Cases**:
```json
// TC1: Tạo session
{
  "user_id": 1,
  "token": "jwt_token_here",
  "expires_at": "2025-11-28T10:00:00"
}
Expected: 201 Created

// TC2: Thiếu required fields
{
  "user_id": 1
}
Expected: 422 Validation Error
```

### 7.3 GET /session/user/{user_id}
**Mục đích**: Lấy sessions của user

**Test Cases**:
```
// TC1: Lấy sessions
GET /session/user/1
Expected: 200, list of sessions

// TC2: User không có session
GET /session/user/99999
Expected: 200, empty list []
```

### 7.4 DELETE /session/{session_id}
**Mục đích**: Xóa session (logout)

**Test Cases**:
```
// TC1: Xóa session
DELETE /session/1
Expected: 200 OK

// TC2: Session không tồn tại
DELETE /session/99999
Expected: 404 Not Found
```

---

## 8. REPORT SERVICE (Port 8008)

**Base URL**: `http://localhost:8008`
**Authentication**: Bearer Token required

### 8.1 GET /health
**Mục đích**: Health check

**Test Cases**:
```
// TC1: Health check
GET /health
Expected: 200 OK
```

### 8.2 GET /report/manager/report-playtime-plot/court={court_id}
**Mục đích**: Lấy biểu đồ playtime của court

**Test Cases**:
```
// TC1: Lấy chart (Manager only)
GET /report/manager/report-playtime-plot/court=1
Headers: Authorization: Bearer {manager_token}
Expected: 200, image/png

// TC2: Customer không có quyền
Headers: Authorization: Bearer {customer_token}
Expected: 403 Forbidden

// TC3: Court không tồn tại
GET /report/manager/report-playtime-plot/court=99999
Expected: 404 Not Found
```

---

## TEST EXECUTION PLAN

### Phase 1: Setup & Authentication (Priority: HIGH)
1. Test Auth Service endpoints
2. Lấy tokens cho customer và manager
3. Verify token với các service khác

### Phase 2: Master Data (Priority: HIGH)
1. Test Facility endpoints
2. Test Court endpoints
3. Verify data relationships

### Phase 3: Core Business Logic (Priority: CRITICAL)
1. Test Booking flow (create → confirm → cancel)
2. Test Billing flow (invoice → payment)
3. Test payment integration (SePay)

### Phase 4: Supporting Services (Priority: MEDIUM)
1. Test Notification endpoints
2. Test Session management
3. Test Report generation

### Phase 5: Integration Testing (Priority: HIGH)
1. End-to-end booking flow
2. Payment callback handling
3. Email notification after booking

### Phase 6: Negative Testing (Priority: MEDIUM)
1. Invalid tokens
2. Missing required fields
3. Permission violations
4. Race conditions

### Phase 7: Performance Testing (Priority: LOW)
1. Load testing cho booking endpoints
2. Concurrent booking conflicts
3. Database connection pooling

---

## TOOLS & SETUP

### Swagger UI Access
- Auth: http://localhost:8001/docs
- Booking: http://localhost:8003/docs
- Facility: http://localhost:8004/docs
- Court: http://localhost:8006/docs
- Billing: http://localhost:8002/docs
- Notification: http://localhost:8007/docs
- Session: http://localhost:8005/docs
- Report: http://localhost:8008/docs

### Test Data
```json
// Customer Account
{
  "email": "customer@test.com",
  "password": "test123",
  "role": "customer"
}

// Manager Account
{
  "email": "manager@test.com",
  "password": "manager123",
  "role": "manager"
}

// Test Facility
{
  "facility_id": 1,
  "name": "Victory Sports Complex"
}

// Test Court
{
  "court_id": 1,
  "name": "Court B1",
  "facility_id": 1
}
```

---

## SUCCESS CRITERIA

### Functional
- [ ] Tất cả endpoints trả về đúng status code
- [ ] Response data đúng format
- [ ] Authentication/Authorization hoạt động đúng
- [ ] Booking flow hoàn chỉnh
- [ ] Payment integration hoạt động

### Non-Functional
- [ ] Response time < 2s cho read operations
- [ ] Response time < 5s cho write operations
- [ ] Concurrent booking không bị duplicate
- [ ] Email notification được gửi đúng

### Security
- [ ] JWT token validation hoạt động
- [ ] Role-based access control đúng
- [ ] Không expose sensitive data
- [ ] SQL injection prevention
- [ ] CSRF protection (nếu có)

---

## NOTES

1. **Test Order**: Luôn test Auth trước, sau đó mới test các service khác
2. **Token Management**: Lưu token sau khi login để dùng cho các test sau
3. **Data Cleanup**: Xóa test data sau mỗi test suite
4. **Environment**: Test trên localhost, port như đã định nghĩa
5. **Error Handling**: Verify error messages rõ ràng và hữu ích

---

**Prepared by**: AI Assistant
**Date**: 27/11/2025
**Version**: 1.0
