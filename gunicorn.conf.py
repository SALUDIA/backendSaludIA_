import os

# Bind to 0.0.0.0 para que Render pueda detectar el puerto
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Configuración optimizada para Render
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 5
max_requests = 100
max_requests_jitter = 10

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Preload app para mejor rendimiento
preload_app = True

# Para debugging
print(f"🚀 Gunicorn configurado para puerto: {os.environ.get('PORT', '10000')}")