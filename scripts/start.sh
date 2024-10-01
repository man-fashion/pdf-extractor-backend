#!/bin/bash

# Start the Flask application
flask run --host=0.0.0.0 --port=5050 &
#python -m k run

# Start the Celery worker
celery -A tasks.celery worker --loglevel=info &

# Wait for both background processes to finish
wait
