# Gunicorn config variables
bind = "0.0.0.0:10000"
workers = 1  # Single worker for simplicity
worker_class = "sync"
timeout = 120
preload_app = True  # This ensures the app is loaded before workers are forked 