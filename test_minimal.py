#!/usr/bin/env python3
"""
Teste mínimo para verificar se o bot funciona com dependências essenciais
"""

import sys
import os
import asyncio
from aiohttp import web

# Adicionar diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_basic():
    """Testa funcionalidades básicas do bot"""
    print("[TEST] Testando BERNAS-AGENT com dependências mínimas...")

    # Testar importações essenciais
    try:
        from economy.router_client import router, process_ai_request
        print("[OK] Módulo de roteador de IA importado")
    except ImportError as e:
        print(f"[ERROR] Erro ao importar roteador de IA: {e}")
        return False

    try:
        from economy.economy_manager import economy_manager, start_economy_server
        print("[OK] Módulo de gerenciador de economia importado")
    except ImportError as e:
        print(f"[ERROR] Erro ao importar gerenciador de economia: {e}")
        return False

    try:
        from monitoring.simple_dashboard import dashboard, update_dashboard_metrics, handle_dashboard
        print("[OK] Módulo de dashboard importado")
    except ImportError as e:
        print(f"[ERROR] Erro ao importar dashboard: {e}")
        return False

    try:
        from token_manager.token_manager import token_manager, start_token_manager
        print("[OK] Módulo de gerenciador de tokens importado")
    except ImportError as e:
        print(f"[ERROR] Erro ao importar gerenciador de tokens: {e}")
        return False

    try:
        from control.simple_control import simple_control, handle_simple_control_api, handle_simple_control_panel
        print("[OK] Módulo de controle importado")
    except ImportError as e:
        print(f"[ERROR] Erro ao importar controle: {e}")
        return False

    # Testar servidor HTTP básico
    print("\n[HTTP] Testando servidor HTTP básico...")
    try:
        app = web.Application()

        async def health_check(request):
            return web.json_response({"status": "healthy", "test": "ok"})

        app.router.add_get('/health', health_check)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8081)
        await site.start()

        print("[OK] Servidor HTTP iniciado na porta 8081")

        # Parar servidor
        await runner.cleanup()
        print("[OK] Servidor HTTP parado")

    except Exception as e:
        print(f"[ERROR] Erro no servidor HTTP: {e}")
        return False

    # Testar simulação de IA
    print("\n[AI] Testando simulação de IA...")
    try:
        # Testar com simulação (sem chaves de API)
        test_prompt = "Teste de funcionamento do bot BERNAS-AGENT"

        # Forçar modo de simulação
        os.environ['SIMULATION_MODE'] = 'true'

        response = await process_ai_request(
            prompt=test_prompt,
            provider=None,  # Usar provedor padrão
            max_tokens=100,
            temperature=0.7
        )

        if response and response.content:
            print(f"[OK] Resposta de IA recebida: {response.content[:50]}...")
        else:
            print("[WARN] Resposta de IA vazia (modo simulação)")

    except Exception as e:
        print(f"[ERROR] Erro na simulação de IA: {e}")
        return False

    print("\n[SUCCESS] Todos os testes básicos passaram!")
    print("O bot está pronto para deploy no Render.com")
    return True

async def main():
    """Função principal de teste"""
    print("=" * 60)
    print("BERNAS-AGENT - Teste de Dependências Mínimas")
    print("=" * 60)

    success = await test_basic()

    if success:
        print("\n[READY] PRONTO PARA DEPLOY!")
        print("O bot pode ser implantado no Render.com com:")
        print("1. requirements.txt simplificado")
        print("2. main.py com imports opcionais")
        print("3. Serviço web na porta 8080")
        return 0
    else:
        print("\n[FAILED] TESTES FALHARAM")
        print("Verifique as dependências e imports")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[STOP] Teste interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL] Erro fatal: {e}")
        sys.exit(1)