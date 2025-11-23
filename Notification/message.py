from fastapi import FastAPI
from Notification.service.notification_service import NotificationService
import json, threading
from kafka.errors import NoBrokersAvailable
from kafka import KafkaProducer, KafkaConsumer
import time


def create_producer(retries=5, delay=3):
    """Tạo KafkaProducer với retry nếu broker chưa ready"""
    for i in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers="kafka:9092",
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            return producer
        except NoBrokersAvailable:
            print(f"Kafka not ready, retry {i+1}/{retries}...")
            time.sleep(delay)
    raise Exception("Cannot connect to Kafka broker after retries")

def send_event(topic: str, data: dict):
    """Gửi event lên Kafka"""
    producer = create_producer()
    producer.send(topic, data)
    producer.flush()
    print(f"Sent message to {topic}: {data}")

def consume_messages():
    consumer = KafkaConsumer(
        bootstrap_servers="kafka:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="notification-service",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    # Subcribe nhiều topic
    consumer.subscribe([
        "user.signup",
    ])

    # Bảng ánh xạ topic → hàm xử lý
    topic_handlers = {
        "user.signup": NotificationService.send_email_verify_register,
    }

    for msg in consumer:
        handler = topic_handlers.get(msg.topic)
        if handler:
            print(f"[Kafka] Received from {msg.topic}: {msg.value}")
            try:
                handler(msg.value)
            except Exception as e:
                print(f"[ERROR] Handler failed: {e}")
        else:
            print(f"[Kafka] No handler configured for topic: {msg.topic}")



