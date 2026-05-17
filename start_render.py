#!/usr/bin/env python3
"""
Script de inicialização para Render.com
Funciona com aiohttp diretamente, sem Gunicorn
"""

import os
import sys
import asyncio
from aiohttp import web

# Adicionar diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configuração
PORT = int(os.getenv("PORT", "8080"))
HOST = "0.0.0.0"

print("=" * 50)
print("BERNAS-AGENT - Render.com Startup")
print("=" * 50)
print(f"Diretório: {current_dir}")
print(f"Host: {HOST}:{PORT}")
print(f"Python: {sys.version}")
print("=" * 50)

# Verificar se app.py existe
app_path = os.path.join(current_dir, "app.py")
if not os.path.exists(app_path):
    print(f"❌ ERRO: app.py não encontrado em {app_path}")
    print(f"📁 Conteúdo do diretório:")
    for item in os.listdir(current_dir):
        print(f"  - {item}")
    sys.exit(1)

print(f"[OK] app.py encontrado: {app_path}")

# Importar app
try:
    import app
    print("[OK] Modulo app importado com sucesso")
except ImportError as e:
    print(f"[ERROR] ERRO ao importar app: {e}")
    print(f"[PATH] Python path: {sys.path}")
    sys.exit(1)

# Verificar se app.app existe
if not hasattr(app, 'app'):
    print(f"[ERROR] ERRO: app.app nao encontrado no modulo")
    print(f"[ATTR] Atributos disponiveis: {dir(app)}")
    sys.exit(1)

print("[OK] app.app disponivel")

async def start_server():
    """Inicia o servidor aiohttp"""
    print("\n[START] Iniciando servidor BERNAS-AGENT...")

    # Usar o app do módulo app
    runner = web.AppRunner(app.app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()

    print(f"[OK] Servidor iniciado em http://{HOST}:{PORT}")
    print(f"[DASH] Dashboard: http://{HOST}:{PORT}/dashboard")
    print(f"[HEALTH] Health: http://{HOST}:{PORT}/api/v1/health")
    print("[READY] BERNAS-AGENT pronto para operar 24/7!")

    # Manter servidor rodando
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print("\n[STOP] Servidor parando...")
        await runner.cleanup()

def main():
    """Função principal"""
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\n[STOP] Interrompido pelo usuário")
    except Exception as e:
        print(f"\n[FATAL] ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()