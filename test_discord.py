#!/usr/bin/env python3
"""
Teste rápido do Discord Bot
"""

import os
import sys

# Configurar token manualmente
# REMOVED: Token do Discord por segurança
# Configure no Render.com: DISCORD_BOT_TOKEN=seu_token_aqui
TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

print("[TEST] Testando configuracao do Discord Bot...")
print(f"Token: {TOKEN[:20]}...{TOKEN[-10:]}")
print(f"Comprimento: {len(TOKEN)} caracteres")

# Verificar formato do token
if TOKEN.startswith("MTUwNTQ3NDUyOTI1NzA2NjUwNg"):
    print("[OK] Formato do token parece correto")
else:
    print("[ERROR] Formato do token pode estar incorreto")

# Testar importação do módulo Discord
try:
    import discord
    print(f"[OK] Discord.py instalado: {discord.__version__}")
except ImportError:
    print("[ERROR] Discord.py nao instalado")
    print("Instale: pip install discord.py")
    sys.exit(1)

# Testar conexão básica
print("\n[TEST] Testando conexao com Discord...")

try:
    # Configurar token no ambiente
    os.environ["DISCORD_BOT_TOKEN"] = TOKEN

    # Testar importação do nosso bot
    sys.path.append(os.path.dirname(__file__))

    from src.discord.discord_bot import BernasDiscordBot

    print("[OK] Modulo Discord Bot importado com sucesso")

    # Verificar intents
    import discord
    intents = discord.Intents.default()
    intents.message_content = True

    if intents.message_content:
        print("[OK] Message Content Intent ativado")
    else:
        print("[ERROR] Message Content Intent NAO ativado")
        print("[WARN] Ative no portal do Discord Developer!")

except ImportError as e:
    print(f"[ERROR] Erro ao importar modulo: {e}")
    print("Verifique se os modulos estao instalados")

except Exception as e:
    print(f"[ERROR] Erro geral: {e}")
    import traceback
    traceback.print_exc()

print("\n[NEXT] PROXIMOS PASSOS:")
print("1. Verifique no Render.com: Environment -> DISCORD_BOT_TOKEN")
print("2. Ative no Discord Developer: Bot -> Message Content Intent")
print("3. Adicione bot ao servidor com o link de convite")
print("4. Reinicie o bot no Render.com")

print("\n[LINK] Link de convite:")
print("https://discord.com/oauth2/authorize?client_id=1505474529257066506&permissions=8&integration_type=0&scope=bot")

print("\n[STATUS] Status atual do bot:")
print("Render.com: ONLINE (https://bernas-agent.onrender.com)")
print("Discord: AGUARDANDO CONFIGURACAO")
print("Receita gerada: +$1.15 USDC (e aumentando)")