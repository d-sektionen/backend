# gunicorn.conf.py
bind = "0.0.0.0:8000"

workers = 4
worker_class = "uvicorn.workers.UvicornWorker"

max_requests = 5000
max_requests_jitter = 500
timeout = 20
graceful_timeout = 60
keepalive = 5

accesslog = "/var/log/backend_access.log"
errorlog = "/var/log/backend_error.log"
loglevel = "info"

limit_request_line = 65535
limit_request_field_size = 65535


def worker_exit(server, worker):
    """Called just before a worker is killed."""
    pass


def on_starting(server):
    """Called just before the master process is initialized."""
    pass
