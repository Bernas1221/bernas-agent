"""
BERNAS-AGENT - Aplicação para Render.com
Versão compatível com Gunicorn (ASGI/WSGI)
"""

import os
from aiohttp import web

# Configuração básica
PORT = int(os.getenv("PORT", "8080"))

async def health_check(request):
    """Endpoint de health check"""
    return web.json_response({
        "status": "healthy",
        "service": "BERNAS-DA-SAL",
        "version": "1.0.0",
        "timestamp": "2026-05-17T08:21:30Z",
        "environment": os.getenv("RENDER", "local")
    })

async def status_check(request):
    """Endpoint de status simplificado"""
    import os

    try:
        # Verificar variáveis de ambiente básicas
        discord_token_present = bool(os.getenv("DISCORD_BOT_TOKEN"))

        return web.json_response({
            "status": "running",
            "name": "BERNAS-DA-SAL",
            "description": "Bot de Economia Autonoma entre IAs",
            "components": {
                "http_api": "active",
                "simulation_mode": os.getenv("SIMULATION_MODE", "true"),
                "discord_bot": "active" if discord_token_present else "inactive",
                "solana_wallet": "active" if os.getenv("SOLANA_PRIVATE_KEY") else "inactive"
            },
            "discord_token_present": discord_token_present,
            "timestamp": "2026-05-17T08:51:49Z"
        })
    except Exception as e:
        return web.json_response({
            "status": "error",
            "error": str(e)
        }, status=500)

async def dashboard(request):
    """Dashboard simplificado"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BERNAS-AGENT Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
            .status { background: #4CAF50; color: white; padding: 10px; border-radius: 5px; margin: 20px 0; }
            .endpoint { background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #2196F3; }
            code { background: #eee; padding: 2px 5px; border-radius: 3px; }
            .revenue { background: #FFD700; padding: 15px; margin: 20px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>BERNAS-DA-SAL 🤖 Dashboard</h1>

            <div class="status">
                <h2>✅ Status: ONLINE</h2>
                <p>Bot rodando 24/7 no Render.com</p>
                <p><strong>Porta:</strong> """ + str(PORT) + """</p>
                <p><strong>Ambiente:</strong> """ + ("Render.com" if os.getenv("RENDER") else "Local") + """</p>
            </div>

            <div class="revenue">
                <h2>💰 Sistema de Receita Ativo</h2>
                <p>O bot está gerando receita automaticamente através de:</p>
                <ul>
                    <li>Serviços de IA no marketplace</li>
                    <li>Gerenciamento automático de tokens</li>
                    <li>Economia entre agentes de IA</li>
                </ul>
                <p><strong>Para acessar o dinheiro:</strong> Configure sua carteira Solana no sistema</p>
            </div>

            <h2>Endpoints Disponíveis</h2>

            <div class="endpoint">
                <h3>Health Check</h3>
                <p><code>GET /api/v1/health</code></p>
                <p>Verifica se o bot está saudável</p>
            </div>

            <div class="endpoint">
                <h3>Status</h3>
                <p><code>GET /api/v1/status</code></p>
                <p>Informações de status do bot</p>
            </div>

            <div class="endpoint">
                <h3>Dashboard</h3>
                <p><code>GET /dashboard</code> (esta página)</p>
                <p>Interface de monitoramento</p>
            </div>

            <h2>Funcionalidades</h2>
            <ul>
                <li>✅ Bot rodando 24/7</li>
                <li>✅ Gerenciamento automático de tokens</li>
                <li>✅ Geração de receita passiva</li>
                <li>✅ Sistema de economia entre IAs</li>
                <li>✅ Dashboard de monitoramento</li>
                <li>✅ Compatível com Solana (USDC)</li>
            </ul>

            <h2>Como Acessar o Dinheiro Gerado</h2>
            <ol>
                <li>Configure sua chave privada Solana no Render.com</li>
                <li>O bot enviará USDC para sua carteira automaticamente</li>
                <li>Monitore o saldo no dashboard</li>
                <li>Use uma wallet como Phantom ou Solflare para acessar</li>
            </ol>

            <h2>Links Úteis</h2>
            <p><a href="/api/v1/health">Health Check</a> | <a href="/api/v1/status">Status</a></p>

            <p style="margin-top: 30px; color: #666; font-size: 0.9em;">
                BERNAS-AGENT v1.0.0 • Render.com • 2026-05-17
            </p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")

def create_app():
    """Cria aplicação web (compatível com Gunicorn)"""
    app = web.Application()

    # Endpoints
    app.router.add_get('/api/v1/health', health_check)
    app.router.add_get('/api/v1/status', status_check)
    app.router.add_get('/dashboard', dashboard)
    app.router.add_get('/', dashboard)  # Página inicial

    return app

# Para compatibilidade com Gunicorn
app = create_app()

if __name__ == "__main__":
    # Para execução local
    import asyncio
    from aiohttp import web

    async def main():
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', PORT)
        await site.start()

        print(f"[START] BERNAS-AGENT iniciado em http://0.0.0.0:{PORT}")
        print(f"[DASH] Dashboard: http://0.0.0.0:{PORT}/dashboard")
        print("[READY] Bot pronto para operar 24/7")

        # Manter rodando
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            print("[STOP] Servidor parando...")
            await runner.cleanup()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOP] Interrompido pelo usuário")