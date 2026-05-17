"""
API para enviar mensagens via Discord
Permite enviar mensagens para qualquer pessoa via HTTP
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from aiohttp import web
import discord
from discord.ext import commands

# Variável global para o bot
discord_bot = None

class DiscordMessageAPI:
    """API para enviar mensagens via Discord"""

    def __init__(self, bot):
        self.bot = bot
        self.authorized_users = set()

        # Adicionar seu ID de usuário do Discord aqui
        # Você pode encontrar seu ID de usuário no Discord: Configurações -> Avançado -> Modo Desenvolvedor
        self.authorized_users.add(1505474529257066506)  # Substitua pelo seu ID real

    async def send_direct_message(self, user_id: int, message: str) -> Dict[str, Any]:
        """Envia mensagem direta para um usuário"""
        try:
            user = await self.bot.fetch_user(user_id)
            if user:
                await user.send(message)
                return {
                    "success": True,
                    "message": f"Mensagem enviada para {user.name} ({user.id})",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "discriminator": user.discriminator
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Usuario com ID {user_id} nao encontrado"
                }
        except discord.errors.Forbidden:
            return {
                "success": False,
                "error": "Nao tenho permissao para enviar mensagem para este usuario"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao enviar mensagem: {str(e)}"
            }

    async def send_to_channel(self, channel_id: int, message: str) -> Dict[str, Any]:
        """Envia mensagem para um canal específico"""
        try:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(message)
                return {
                    "success": True,
                    "message": f"Mensagem enviada para canal {channel.name}",
                    "channel": {
                        "id": channel.id,
                        "name": channel.name,
                        "guild": channel.guild.name if channel.guild else None
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Canal com ID {channel_id} nao encontrado"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao enviar mensagem: {str(e)}"
            }

    async def broadcast_to_guilds(self, message: str) -> Dict[str, Any]:
        """Envia mensagem para todos os servidores"""
        try:
            total_sent = 0
            failed_guilds = []

            for guild in self.bot.guilds:
                # Encontrar canal de texto padrão
                channel = guild.system_channel or (guild.text_channels[0] if guild.text_channels else None)
                if channel:
                    try:
                        await channel.send(f"📢 **Anuncio do BERNAS-DA-SAL**: {message}")
                        total_sent += 1
                    except Exception as e:
                        failed_guilds.append(f"{guild.name}: {str(e)}")

            return {
                "success": True,
                "message": f"Anuncio enviado para {total_sent} servidores",
                "stats": {
                    "total_guilds": len(self.bot.guilds),
                    "successful": total_sent,
                    "failed": len(failed_guilds),
                    "failed_list": failed_guilds[:5]  # Mostrar apenas 5 primeiros erros
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao fazer broadcast: {str(e)}"
            }

    async def find_user(self, username: str) -> Dict[str, Any]:
        """Encontra usuário pelo nome"""
        try:
            found_users = []

            for guild in self.bot.guilds:
                for member in guild.members:
                    if username.lower() in member.name.lower() or (member.nick and username.lower() in member.nick.lower()):
                        found_users.append({
                            "id": member.id,
                            "name": member.name,
                            "nick": member.nick,
                            "guild": guild.name,
                            "guild_id": guild.id
                        })

            return {
                "success": True,
                "count": len(found_users),
                "users": found_users[:20]  # Limitar a 20 resultados
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao buscar usuario: {str(e)}"
            }

    async def get_bot_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do bot"""
        try:
            return {
                "success": True,
                "stats": {
                    "bot_name": self.bot.user.name,
                    "bot_id": self.bot.user.id,
                    "guilds_count": len(self.bot.guilds),
                    "total_members": sum(len(guild.members) for guild in self.bot.guilds),
                    "uptime": str(datetime.now() - self.bot.start_time) if hasattr(self.bot, 'start_time') else "N/A",
                    "commands_available": len(self.bot.commands)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter estatisticas: {str(e)}"
            }

# Handlers HTTP
async def handle_send_dm(request):
    """Handler para enviar mensagem direta"""
    try:
        data = await request.json()
        user_id = data.get('user_id')
        message = data.get('message')
        auth_token = data.get('auth_token')

        if not user_id or not message:
            return web.json_response({
                "success": False,
                "error": "user_id e message sao obrigatorios"
            }, status=400)

        # Verificar autenticação (simples por enquanto)
        if auth_token != os.getenv("API_AUTH_TOKEN", "bernassecret"):
            return web.json_response({
                "success": False,
                "error": "Token de autenticacao invalido"
            }, status=401)

        if not discord_bot:
            return web.json_response({
                "success": False,
                "error": "Bot Discord nao inicializado"
            }, status=503)

        api = DiscordMessageAPI(discord_bot)
        result = await api.send_direct_message(int(user_id), message)

        return web.json_response(result)

    except json.JSONDecodeError:
        return web.json_response({
            "success": False,
            "error": "JSON invalido"
        }, status=400)
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }, status=500)

async def handle_find_user(request):
    """Handler para encontrar usuário"""
    try:
        username = request.query.get('username')
        auth_token = request.query.get('auth_token')

        if not username:
            return web.json_response({
                "success": False,
                "error": "username e obrigatorio"
            }, status=400)

        # Verificar autenticação
        if auth_token != os.getenv("API_AUTH_TOKEN", "bernassecret"):
            return web.json_response({
                "success": False,
                "error": "Token de autenticacao invalido"
            }, status=401)

        if not discord_bot:
            return web.json_response({
                "success": False,
                "error": "Bot Discord nao inicializado"
            }, status=503)

        api = DiscordMessageAPI(discord_bot)
        result = await api.find_user(username)

        return web.json_response(result)

    except Exception as e:
        return web.json_response({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }, status=500)

async def handle_bot_stats(request):
    """Handler para estatísticas do bot"""
    try:
        auth_token = request.query.get('auth_token')

        # Verificar autenticação
        if auth_token != os.getenv("API_AUTH_TOKEN", "bernassecret"):
            return web.json_response({
                "success": False,
                "error": "Token de autenticacao invalido"
            }, status=401)

        if not discord_bot:
            return web.json_response({
                "success": False,
                "error": "Bot Discord nao inicializado"
            }, status=503)

        api = DiscordMessageAPI(discord_bot)
        result = await api.get_bot_stats()

        return web.json_response(result)

    except Exception as e:
        return web.json_response({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }, status=500)

async def handle_broadcast(request):
    """Handler para broadcast"""
    try:
        data = await request.json()
        message = data.get('message')
        auth_token = data.get('auth_token')

        if not message:
            return web.json_response({
                "success": False,
                "error": "message e obrigatorio"
            }, status=400)

        # Verificar autenticação
        if auth_token != os.getenv("API_AUTH_TOKEN", "bernassecret"):
            return web.json_response({
                "success": False,
                "error": "Token de autenticacao invalido"
            }, status=401)

        if not discord_bot:
            return web.json_response({
                "success": False,
                "error": "Bot Discord nao inicializado"
            }, status=503)

        api = DiscordMessageAPI(discord_bot)
        result = await api.broadcast_to_guilds(message)

        return web.json_response(result)

    except json.JSONDecodeError:
        return web.json_response({
            "success": False,
            "error": "JSON invalido"
        }, status=400)
    except Exception as e:
        return web.json_response({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }, status=500)

def setup_routes(app, bot):
    """Configura rotas da API"""
    global discord_bot
    discord_bot = bot

    app.router.add_post('/api/v1/discord/send_dm', handle_send_dm)
    app.router.add_get('/api/v1/discord/find_user', handle_find_user)
    app.router.add_get('/api/v1/discord/stats', handle_bot_stats)
    app.router.add_post('/api/v1/discord/broadcast', handle_broadcast)

# Para importação
from datetime import datetime