#!/bin/bash

# Activate the virtual environment
# source .venv/bin/activate

# Install dependencies if not already installed
pip3 install flask gunicorn eventlet

# Run the Flask app using Gunicorn and Eventlet
gunicorn -w 4 -k eventlet -b 0.0.0.0:8000 app:app
