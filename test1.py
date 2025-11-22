from kafka import KafkaProducer
import json

# Kết nối tới Kafka broker
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",  # host/port của Kafka broker
    value_serializer=lambda v: json.dumps(v).encode("utf-8")  # serialize JSON
)

# Gửi message tới topic 'test-topic'
producer.send("test-topic", {"msg": "Hello from Python"})

# Đảm bảo gửi ngay lập tức
producer.flush()

print("Message sent!")
