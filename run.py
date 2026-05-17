#!/usr/bin/env python3
"""
Script de inicialização para Render.com
Este script é executado a partir do diretório /opt/render/project/src/
"""

import os
import sys

# Adicionar diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Verificar se app.py existe
app_path = os.path.join(current_dir, "app.py")
if not os.path.exists(app_path):
    print(f"[ERROR] Arquivo app.py não encontrado em: {app_path}")
    print(f"[INFO] Diretório atual: {current_dir}")
    print(f"[INFO] Conteúdo do diretório: {os.listdir(current_dir)}")
    sys.exit(1)

print(f"[INFO] Iniciando BERNAS-AGENT a partir de: {app_path}")
print(f"[INFO] Python path: {sys.path}")

# Importar e executar app.py
try:
    # Executar app.py como módulo
    import app
    app.main()
except Exception as e:
    print(f"[FATAL] Erro ao iniciar BERNAS-AGENT: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)