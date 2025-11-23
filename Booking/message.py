import json
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable


def create_producer(retries: int = 5, delay: int = 3):
    """Create Kafka producer with small retry window to avoid startup races."""
    for idx in range(retries):
        try:
            return KafkaProducer(
                bootstrap_servers="kafka:9092",
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        except NoBrokersAvailable:
            time.sleep(delay)
    raise Exception("Cannot connect to Kafka broker after retries")


def send_event(topic: str, data: dict):
    producer = create_producer()
    producer.send(topic, data)
    producer.flush()
