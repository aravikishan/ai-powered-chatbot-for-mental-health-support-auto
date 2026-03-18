#!/bin/bash
set -e
echo "Starting AI-Powered Chatbot for Mental Health Support..."
uvicorn app:app --host 0.0.0.0 --port 9093 --workers 1
