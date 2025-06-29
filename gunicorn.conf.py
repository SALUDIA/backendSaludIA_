import os

# CRÍTICO: Bind al puerto dinámico de Render
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Configuración optimizada
workers = 1
worker_class = "sync"
timeout = 300
keepalive = 5
max_requests = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Debug
print(f"🚀 Gunicorn configurado para puerto: {os.environ.get('PORT', '10000')}")
print(f"📡 Bind address: {bind}")