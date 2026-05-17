"""
Configuração do Gunicorn para Render.com
"""

import os

# Porta do Render.com (variável de ambiente $PORT)
port = int(os.getenv("PORT", "8080"))

# Configurações do Gunicorn
bind = f"0.0.0.0:{port}"
workers = 1
worker_class = "aiohttp.GunicornWebWorker"
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Debug
reload = False
preload_app = True

print(f"[GUNICORN] Configurado para porta: {port}")
print(f"[GUNICORN] Workers: {workers}")
print(f"[GUNICORN] Bind: {bind}")