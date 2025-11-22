#!/bin/bash

# Start consumer in background
python Auth/message.py &

# Start API (foreground)
uvicorn Auth.controller.main:app --host 0.0.0.0 --port 8001 --reload
