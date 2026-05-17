#!/usr/bin/env python3
"""
Endpoint de teste do Discord para diagnóstico
"""

import os
import sys
from aiohttp import web

async def discord_test(request):
    """Endpoint de teste do Discord"""
    token = os.getenv("DISCORD_BOT_TOKEN", "")

    # Informações do token
    token_info = {
        "present": bool(token),
        "length": len(token),
        "starts_with": token[:20] if token else "",
        "ends_with": token[-10:] if token else "",
        "valid_format": token.startswith("MTUw") if token else False
    }

    # Verificar intents necessários
    intents_required = ["MESSAGE_CONTENT_INTENT"]

    # Status do bot
    bot_status = {
        "name": "BERNAS-DA-SAL",
        "application_id": "1505474529257066506",
        "invite_url": "https://discord.com/oauth2/authorize?client_id=1505474529257066506&permissions=8&integration_type=0&scope=bot",
        "developer_portal": "https://discord.com/developers/applications/1505474529257066506/bot"
    }

    # Diagnóstico
    diagnosis = []

    if not token_info["present"]:
        diagnosis.append("❌ DISCORD_BOT_TOKEN não configurado no ambiente")
    elif token_info["length"] < 50:
        diagnosis.append("❌ Token muito curto (possivelmente inválido)")
    elif not token_info["valid_format"]:
        diagnosis.append("⚠️  Token não começa com formato esperado")
    else:
        diagnosis.append("✅ Token parece válido")

    # Verificar outras variáveis
    env_vars = {
        "SOLANA_PRIVATE_KEY": os.getenv("SOLANA_PRIVATE_KEY", ""),
        "SIMULATION_MODE": os.getenv("SIMULATION_MODE", "true"),
        "PORT": os.getenv("PORT", "8080")
    }

    response = {
        "status": "diagnostic",
        "discord_token": token_info,
        "bot_info": bot_status,
        "diagnosis": diagnosis,
        "environment": {
            "discord_token_present": bool(token),
            "solana_key_present": bool(env_vars["SOLANA_PRIVATE_KEY"]),
            "simulation_mode": env_vars["SIMULATION_MODE"],
            "port": env_vars["PORT"]
        },
        "next_steps": [
            "1. Verifique se 'Message Content Intent' está ativado no portal do Discord",
            "2. Confirme que o token no Render.com é idêntico ao do portal",
            "3. Use o link de convite para adicionar o bot ao servidor",
            "4. Verifique os logs do Render.com para erros de inicialização"
        ]
    }

    return web.json_response(response)

def main():
    """Servidor de teste simples"""
    app = web.Application()
    app.router.add_get('/test/discord', discord_test)

    print("Servidor de teste do Discord iniciado")
    print("Acesse: http://localhost:8081/test/discord")
    print("Verifique o status do seu token do Discord")

    web.run_app(app, port=8081)

if __name__ == "__main__":
    main()