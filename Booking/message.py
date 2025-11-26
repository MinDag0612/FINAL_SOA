from kafka import KafkaProducer, KafkaConsumer
import json
import threading
import time
from kafka.errors import NoBrokersAvailable

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