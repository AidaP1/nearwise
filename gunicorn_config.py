from app import app, init_database

def post_fork(server, worker):
    # Initialize database after worker fork
    init_database()

# Gunicorn config variables
bind = "0.0.0.0:10000"
workers = 4
worker_class = "sync"
timeout = 120 