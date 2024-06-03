#!/bin/bash

# Load environment variables from .env file
chmod 777 /app/.env
source /app/.env

# Start your Python Application
python app.py
