# Hướng dẫn luồng  Booking

- Trực tiếp tới service (port host): Auth `:8001`, Facility `:8005`, Court `:8004`, Booking `:8003`
- Luôn gửi `Authorization: Bearer <token>` cho các request booking.

Các bước
1) Đăng nhập (Auth)  
   `POST /auth/login` với body `{"email":"<email>","password":"<pass>"}` → nhận `token`.
2) Xem danh sách cơ sở (Facility)  

   `GET /facility` → chọn `facility_id`.
3) Xem danh sách sân (Court)  
   `GET /court` (hoặc `/court/{id}/availability?date=YYYY-MM-DD`) → chọn `court_id` và khung giờ.

4) Tạo booking (giữ slot + tạo hóa đơn)  
   `POST /booking` kèm header `Authorization: Bearer <token>` và body:
   ```json
   {
     "facility_id": 1,
     "items": [
       {
         "court_id": 1,
         "start_time": "2025-12-01T07:00:00",
         "end_time": "2025-12-01T08:00:00",
         "price": 120000
       }
     ],
     "payment_method": "cash",
     "note": "optional"
   }
   ```
   Booking sẽ kiểm tra facility/court, kiểm tra trùng slot, đặt trạng thái `pending`, gọi Billing tạo invoice/payment intent.
5) Xem danh sách booking của tôi  
   `GET /booking` với bearer token.

6) Hủy booking (nếu được phép)  
   `POST /booking/{booking_id}/cancel` với body `{"reason":"optional"}`.


