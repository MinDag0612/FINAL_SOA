from typing import List
from Notification.models.notification_models import (
    BookingConfirmedPayload,
    NotificationLog,
    NotificationSendRequest,
    ReminderPayload,
)
from Notification.core.mailler_api import send_email_v1
import requests
import json


class NotificationService:

    def __init__(self):
        pass
        
    @staticmethod
    def send_email_verify_register(user: dict):
        # Gọi hàm gửi email từ mailler_api
        try:
            send_email_v1(
                recipient=user["email"],
                subject="Xác nhận đăng ký tài khoản" + str(user["fullname"]),
                content="Cảm ơn bạn đã đăng ký tài khoản. Vui lòng xác nhận email của bạn.",
            )
            return {
                "status": "sent",
                "recipients": user,
                "message": "Email xác nhận đã được gửi.",
            }
        except Exception as e:
            raise Exception("Lỗi khi gửi email xác nhận: " + str(e) + " -- from notification service")
    
    @staticmethod
    def booking_confirmed(data: dict) -> dict:
        try:
            user_email = data.get("user_email") or data.get("email")
            if not user_email:
                raise ValueError("Missing user_email or email field")
            
            booking_id = data.get("booking_id", "N/A")
            court_name = data.get("court_name", "N/A")
            scheduled_time = data.get("scheduled_time", "N/A")
            
            content = f"""
Xin chào,

Booking của bạn đã được xác nhận thành công!

Thông tin booking:
- Mã booking: #{booking_id}
- Sân: {court_name}
- Thời gian: {scheduled_time}

Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi!

---
BSport - Hệ thống đặt sân Badminton
"""

            send_email_v1(
                recipient=user_email,
                subject="[BSport] Xác nhận đặt sân thành công",
                content=content,
            )

            return {
                "status": "sent",
                "recipients": user_email,
                "message": "Email xác nhận đã được gửi.",
            }
        except Exception as e:
            raise Exception("Lỗi khi gửi email xác nhận booking: " + str(e) + " -- from notification service")

