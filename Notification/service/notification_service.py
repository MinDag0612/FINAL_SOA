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
            content = f"""
                    Your booking is confirmed!

                    Booking information:
                    {data}

                    Please complete your payment in 10 minutes to secure your reservation.
                    Thank you for choosing our service.
                    """

            send_email_v1(
                recipient=data["email"],
                subject="Booking Confirmed - Your Reservation is Successful!",
                content=content,
            )

            return {
                "status": "sent",
                "recipients": data["email"],
                "message": "Email xác nhận đã được gửi.",
                "payload_received": data.__dict__
            }
        except Exception as e:
            raise Exception("Lỗi khi gửi email xác nhận booking: " + str(e) + " -- from notification service")

