# from kafka import KafkaProducer, KafkaConsumer
# import json
# import time

# TOPIC = "test-topic"

# # ---------- Producer ----------
# producer = KafkaProducer(
#     bootstrap_servers="kafka:9092",
#     value_serializer=lambda v: json.dumps(v).encode("utf-8")
# )

# # Gửi message
# message = {"msg": "Hello from Python"}
# producer.send(TOPIC, message)
# producer.flush()
# print(f"Sent message: {message}")

# # Đợi 1 giây để Kafka cập nhật metadata
# time.sleep(1)

# # ---------- Consumer ----------
# consumer = KafkaConsumer(
#     TOPIC,
#     bootstrap_servers="kafka:9092",
#     auto_offset_reset="earliest",
#     enable_auto_commit=True,
#     group_id="test-group",
#     consumer_timeout_ms=5000,  # nếu không có message sẽ exit
#     value_deserializer=lambda x: json.loads(x.decode("utf-8"))
# )

# print("Waiting for messages...")
# for msg in consumer:
#     print("Received message:", msg.value)
# consumer.close()
# print("Consumer done")


from kafka import KafkaProducer, KafkaConsumer
import json

# === Producer ===
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_event(topic: str, data: dict):
    """Gửi event lên Kafka"""
    producer.send(topic, data)
    producer.flush()
    print(f"Sent message to {topic}: {data}")

# === Consumer ===
def consume_events(topic: str, group_id: str, callback):
    """Đọc event từ Kafka và gọi callback xử lý"""
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers="kafka:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    for message in consumer:
        callback(message.value)
