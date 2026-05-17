"""
Discord Bot para BERNAS-AGENT
Conversa em tempo real e geração de receita
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import discord
from discord.ext import commands
from decimal import Decimal

# Adicionar diretório pai ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Importar módulos do projeto
try:
    from economy.router_client import process_ai_request, AIProvider
    from economy.economy_manager import economy_manager
    from token_manager.token_manager import token_manager
    DISCORD_ENABLED = True
except ImportError as e:
    print(f"[WARN] Módulos não disponíveis para Discord: {e}")
    DISCORD_ENABLED = False

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
COMMAND_PREFIX = "!"
BOT_NAME = "BERNAS-DA-SAL"
REVENUE_PER_MESSAGE = Decimal("0.01")  # 0.01 USDC por mensagem

class DiscordRevenueTracker:
    """Rastreador de receita do Discord"""

    def __init__(self):
        self.revenue_stats = {
            "total_messages": 0,
            "total_revenue_usdc": Decimal("0"),
            "active_conversations": 0,
            "users_served": set(),
            "start_time": datetime.now()
        }

    def add_revenue(self, user_id: str, amount: Decimal = REVENUE_PER_MESSAGE):
        """Adiciona receita de uma interação"""
        self.revenue_stats["total_messages"] += 1
        self.revenue_stats["total_revenue_usdc"] += amount
        self.revenue_stats["users_served"].add(user_id)

        # Adicionar ao token manager
        if token_manager:
            token_manager.add_revenue(float(amount))

        logger.info(f"Receita Discord: +{amount} USDC de {user_id}")
        return amount

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas"""
        stats = self.revenue_stats.copy()
        stats["total_revenue_usdc"] = str(stats["total_revenue_usdc"])
        stats["users_served_count"] = len(stats["users_served"])
        stats["uptime_hours"] = (datetime.now() - stats["start_time"]).total_seconds() / 3600
        return stats

class BernasDiscordBot(commands.Bot):
    """Bot Discord do BERNAS-DA-SAL"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)

        self.revenue_tracker = DiscordRevenueTracker()
        self.active_conversations: Dict[str, Dict] = {}  # user_id -> conversation data

        # Comandos
        self.add_commands()

    def add_commands(self):
        """Adiciona comandos ao bot"""

        @self.command(name="chat", help="Inicia conversa com a IA")
        async def chat(ctx, *, message: str):
            """Comando de chat com IA"""
            user_id = str(ctx.author.id)

            # Gerar receita
            revenue = self.revenue_tracker.add_revenue(user_id)

            # Processar com IA
            try:
                response = await process_ai_request(
                    prompt=message,
                    provider=AIProvider.GEMINI,  # Usar Gemini por padrão
                    max_tokens=500,
                    temperature=0.7
                )

                if response and response.content:
                    # Enviar resposta
                    await ctx.send(f"**BERNAS-DA-SAL**: {response.content}\n\n"
                                  f"💰 *Receita gerada: {revenue} USDC*")
                else:
                    await ctx.send("Desculpe, não consegui processar sua mensagem.")

            except Exception as e:
                logger.error(f"Erro no chat: {e}")
                await ctx.send("Erro ao processar sua mensagem. Tente novamente.")

        @self.command(name="economy", help="Mostra estatísticas da economia")
        async def economy(ctx):
            """Mostra estatísticas da economia"""
            try:
                stats = economy_manager.get_marketplace_stats()
                revenue_stats = self.revenue_tracker.get_stats()

                embed = discord.Embed(
                    title="💰 Economia BERNAS-AGENT",
                    color=discord.Color.green()
                )

                embed.add_field(
                    name="Marketplace",
                    value=f"Serviços: {stats.get('total_services', 0)}\n"
                          f"Transações: {stats.get('total_transactions', 0)}\n"
                          f"Volume: {stats.get('total_volume_usdc', 0)} USDC",
                    inline=True
                )

                embed.add_field(
                    name="Discord",
                    value=f"Mensagens: {revenue_stats['total_messages']}\n"
                          f"Receita: {revenue_stats['total_revenue_usdc']} USDC\n"
                          f"Usuários: {revenue_stats['users_served_count']}",
                    inline=True
                )

                if token_manager:
                    token_stats = token_manager.get_stats()
                    embed.add_field(
                        name="Tokens",
                        value=f"Saldo: {token_stats.get('current_balance', 0):.2f} USDC\n"
                              f"Receita Total: {token_stats.get('total_revenue', 0):.2f} USDC",
                        inline=True
                    )

                await ctx.send(embed=embed)

            except Exception as e:
                logger.error(f"Erro no comando economy: {e}")
                await ctx.send("Erro ao obter estatísticas da economia.")

        @self.command(name="services", help="Lista serviços disponíveis")
        async def services(ctx):
            """Lista serviços disponíveis"""
            try:
                services = economy_manager.list_services()

                embed = discord.Embed(
                    title="🛒 Serviços Disponíveis",
                    description="Compre serviços com USDC",
                    color=discord.Color.blue()
                )

                for service in services[:10]:  # Mostrar apenas 10 primeiros
                    embed.add_field(
                        name=service.name,
                        value=f"💰 {service.price} USDC\n"
                              f"👤 {service.provider}\n"
                              f"📝 {service.description[:50]}...",
                        inline=False
                    )

                if len(services) > 10:
                    embed.set_footer(text=f"Mostrando 10 de {len(services)} serviços")

                await ctx.send(embed=embed)

            except Exception as e:
                logger.error(f"Erro no comando services: {e}")
                await ctx.send("Erro ao listar serviços.")

        @self.command(name="buy", help="Compra um serviço")
        async def buy(ctx, service_name: str):
            """Compra um serviço"""
            try:
                user_id = str(ctx.author.id)

                # Encontrar serviço
                service = None
                all_services = economy_manager.list_services()
                for s in all_services:
                    if s.name.lower() == service_name.lower():
                        service = s
                        break

                if not service:
                    await ctx.send(f"Serviço '{service_name}' não encontrado.")
                    return

                # Verificar saldo (simulação)
                # Em produção, verificar saldo real na blockchain

                # Processar compra
                transaction = economy_manager.create_transaction(
                    from_wallet=f"discord_{user_id}",
                    to_wallet=service.provider,
                    amount=service.price,
                    service_id=service.id,
                    description=f"Compra via Discord: {service.name}"
                )

                # Gerar receita (comissão do bot)
                commission = Decimal(str(service.price)) * Decimal("0.1")  # 10% comissão
                self.revenue_tracker.add_revenue(user_id, commission)

                embed = discord.Embed(
                    title="✅ Compra Realizada",
                    color=discord.Color.green()
                )

                embed.add_field(name="Serviço", value=service.name, inline=True)
                embed.add_field(name="Preço", value=f"{service.price} USDC", inline=True)
                embed.add_field(name="Comissão", value=f"{commission} USDC", inline=True)
                embed.add_field(name="Fornecedor", value=service.provider, inline=True)
                embed.add_field(name="Transação", value=transaction.id[:8], inline=True)

                await ctx.send(embed=embed)

            except Exception as e:
                logger.error(f"Erro no comando buy: {e}")
                await ctx.send(f"Erro ao comprar serviço: {e}")

        @self.command(name="help", help="Mostra ajuda")
        async def help_command(ctx):
            """Comando de ajuda"""
            embed = discord.Embed(
                title="🤖 BERNAS-AGENT - Comandos do Discord",
                description="Bot de Economia Autônoma entre IAs",
                color=discord.Color.purple()
            )

            embed.add_field(
                name="💬 Conversa",
                value="`!chat <mensagem>` - Conversa com a IA\n"
                      "Gera receita automática por mensagem",
                inline=False
            )

            embed.add_field(
                name="💰 Economia",
                value="`!economy` - Estatísticas da economia\n"
                      "`!services` - Lista serviços disponíveis\n"
                      "`!buy <serviço>` - Compra um serviço",
                inline=False
            )

            embed.add_field(
                name="📊 Informações",
                value="`!status` - Status do bot\n"
                      "`!revenue` - Sua receita gerada\n"
                      "`!help` - Esta mensagem",
                inline=False
            )

            embed.set_footer(text="BERNAS-AGENT • Gerando receita 24/7")

            await ctx.send(embed=embed)

        @self.command(name="status", help="Status do bot")
        async def status(ctx):
            """Status do bot"""
            revenue_stats = self.revenue_tracker.get_stats()

            embed = discord.Embed(
                title="✅ BERNAS-AGENT Online",
                description="Bot rodando 24/7 no Render.com",
                color=discord.Color.green()
            )

            embed.add_field(
                name="📊 Estatísticas Discord",
                value=f"Mensagens: {revenue_stats['total_messages']}\n"
                      f"Receita: {revenue_stats['total_revenue_usdc']} USDC\n"
                      f"Usuários: {revenue_stats['users_served_count']}\n"
                      f"Uptime: {revenue_stats['uptime_hours']:.1f}h",
                inline=True
            )

            embed.add_field(
                name="🌐 Online em",
                value="Render.com 24/7\n"
                      "Dashboard: https://bernas-agent.onrender.com\n"
                      "GitHub: https://github.com/Bernas1221/bernas-agent",
                inline=True
            )

            await ctx.send(embed=embed)

        @self.command(name="revenue", help="Sua receita gerada")
        async def revenue(ctx):
            """Mostra receita do usuário"""
            user_id = str(ctx.author.id)
            user_name = ctx.author.name

            # Calcular receita estimada do usuário
            # (em produção, rastrear por usuário)
            estimated_revenue = Decimal("0.05") * self.revenue_tracker.revenue_stats["total_messages"]

            embed = discord.Embed(
                title=f"💰 Sua Receita - {user_name}",
                color=discord.Color.gold()
            )

            embed.add_field(
                name="Estimativa",
                value=f"Receita gerada: {estimated_revenue:.4f} USDC\n"
                      f"Mensagens enviadas: {self.revenue_tracker.revenue_stats['total_messages']}",
                inline=True
            )

            embed.add_field(
                name="Como aumentar",
                value="1. Use `!chat` mais vezes\n"
                      "2. Compre serviços com `!buy`\n"
                      "3. Convide amigos\n"
                      "4. Participe do marketplace",
                inline=True
            )

            embed.set_footer(text="Receita enviada automaticamente a cada 10 USDC")

            await ctx.send(embed=embed)

    async def on_ready(self):
        """Evento quando o bot está pronto"""
        logger.info(f"✅ Discord Bot conectado como {self.user}")
        logger.info(f"📊 Servidores: {len(self.guilds)}")

        # Definir status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="💰 Gerando receita 24/7"
        )
        await self.change_presence(activity=activity)

    async def on_message(self, message):
        """Processa todas as mensagens"""
        # Ignorar mensagens do próprio bot
        if message.author == self.user:
            return

        # Processar comandos
        await self.process_commands(message)

        # Se a mensagem menciona o bot, responder automaticamente
        if self.user in message.mentions and not message.content.startswith(COMMAND_PREFIX):
            user_id = str(message.author.id)

            # Gerar receita
            self.revenue_tracker.add_revenue(user_id)

            # Responder com IA
            try:
                prompt = message.content.replace(f"<@{self.user.id}>", "").strip()
                if prompt:
                    response = await process_ai_request(
                        prompt=prompt,
                        max_tokens=300,
                        temperature=0.7
                    )

                    if response and response.content:
                        await message.channel.send(
                            f"**{message.author.name}**, {response.content}\n"
                            f"💰 *Receita gerada: {REVENUE_PER_MESSAGE} USDC*"
                        )
            except Exception as e:
                logger.error(f"Erro ao responder menção: {e}")

async def start_discord_bot():
    """Inicia o bot Discord"""
    if not DISCORD_TOKEN:
        logger.warning("Token do Discord não configurado. Bot Discord desativado.")
        return None

    if not DISCORD_ENABLED:
        logger.warning("Módulos necessários não disponíveis. Bot Discord desativado.")
        return None

    try:
        bot = BernasDiscordBot()
        await bot.start(DISCORD_TOKEN)
        return bot
    except Exception as e:
        logger.error(f"Erro ao iniciar bot Discord: {e}")
        return None

def main():
    """Função principal para teste"""
    if not DISCORD_TOKEN:
        print("ERRO: DISCORD_BOT_TOKEN não configurado")
        print("Configure no .env ou variáveis de ambiente:")
        print("DISCORD_BOT_TOKEN=seu_token_aqui")
        return

    print("🤖 Iniciando BERNAS-AGENT Discord Bot...")
    asyncio.run(start_discord_bot())

if __name__ == "__main__":
    main()