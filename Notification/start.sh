#!/bin/bash

# Start consumer in background
python Notification/message.py &

# Start API (foreground)
uvicorn Notification.controller.main:app --host 0.0.0.0 --port 8007
