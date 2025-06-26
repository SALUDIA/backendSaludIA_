import os

# Configuración simplificada para Render
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"
workers = 1  # Reducido para evitar problemas de memoria
worker_class = "sync"
timeout = 300  # Aumentado para modelos ML
keepalive = 2
max_requests = 1000
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"