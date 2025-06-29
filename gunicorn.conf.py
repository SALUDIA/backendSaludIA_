import os

# Bind to 0.0.0.0 para que Render pueda detectar el puerto
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"

# Workers configuration (ajustado para modelos ML)
workers = 1  # Reducido para modelos pesados
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Aumentado para carga de modelos
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "saludia-backend"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"

# Para Render - importante
preload_app = True
max_requests = 1000
max_requests_jitter = 100

# Memory management para modelos ML
worker_tmp_dir = "/dev/shm"