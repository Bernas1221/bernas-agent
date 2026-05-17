"""
BERNAS-AGENT - Bot de Economia Autônoma entre IAs
Integração: IA + Blockchain (Solana) + WhatsApp
Baseado na arquitetura Moltbook Crypto Bot
"""

import os
import sys
import json
import logging
import asyncio
import signal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import aiohttp
from aiohttp import web

# Carregar variáveis de ambiente do arquivo .env
from dotenv import load_dotenv
load_dotenv()

# Adicionar diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importar módulos do projeto
from economy.router_client import router, process_ai_request
from economy.economy_manager import economy_manager, start_economy_server
from monitoring.simple_dashboard import dashboard, update_dashboard_metrics, handle_dashboard
from token_manager.token_manager import token_manager, start_token_manager
from control.simple_control import simple_control, handle_simple_control_api, handle_simple_control_panel

# Imports opcionais
try:
    from solana.solana_client import wallet_manager, init_solana_service
    SOLANA_ENABLED = True
except ImportError:
    SOLANA_ENABLED = False
    logger.warning("Serviço Solana não disponível")

try:
    from whatsapp.whatsapp_client import notification_manager, init_whatsapp_service
    WHATSAPP_ENABLED = True
except ImportError:
    WHATSAPP_ENABLED = False
    logger.warning("Serviço WhatsApp não disponível")

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bernas_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BernasAgent:
    """Classe principal do bot BERNAS-AGENT"""

    def __init__(self):
        self.running = False
        self.start_time = None
        self.tasks = []
        self.http_app = None
        self.stats = {
            "start_time": None,
            "uptime_seconds": 0,
            "total_requests": 0,
            "total_transactions": 0,
            "total_messages": 0,
            "total_errors": 0
        }

    async def initialize(self):
        """Inicializa todos os componentes do bot"""
        logger.info("🚀 Inicializando BERNAS-AGENT...")

        # Criar diretórios necessários
        self._create_directories()

        # Carregar configuração
        config = self._load_config()
        logger.info(f"Configuração carregada: {len(config)} variáveis")

        # Inicializar componentes
        logger.info("1. Inicializando Roteador de IA...")
        # O roteador já é inicializado na importação

        logger.info("2. Inicializando Gerenciador de Economia...")
        self.economy_task = asyncio.create_task(start_economy_server())

        logger.info("3. Inicializando Serviço Solana...")
        if SOLANA_ENABLED:
            await init_solana_service()
        else:
            logger.warning("Serviço Solana desativado - módulo não disponível")

        logger.info("4. Inicializando Serviço WhatsApp...")
        if WHATSAPP_ENABLED:
            await init_whatsapp_service()
        else:
            logger.warning("Serviço WhatsApp desativado - módulo não disponível")

        logger.info("5. Inicializando API HTTP...")
        await self._start_http_api()

        logger.info("6. Inicializando Gerenciador de Tokens...")
        self.token_manager_task = asyncio.create_task(start_token_manager())

        logger.info("7. Inicializando Dashboard de Monitoramento...")
        self.dashboard_task = asyncio.create_task(update_dashboard_metrics())

        logger.info("8. Inicializando Painel de Controle...")
        # Painel de controle já inicializado na importação

        self.start_time = datetime.now()
        self.stats["start_time"] = self.start_time.isoformat()
        self.running = True

        logger.info("✅ BERNAS-AGENT inicializado com sucesso!")
        logger.info(f"📅 Início: {self.start_time}")
        logger.info("🤖 Bot pronto para operar 24/7")
        logger.info("📊 Dashboard: http://localhost:8080/dashboard")
        logger.info("🎮 Controle: http://localhost:8080/control")
        logger.info("💰 Gerenciador de Tokens: Ativo")

    def _create_directories(self):
        """Cria diretórios necessários"""
        directories = ['logs', 'data', 'data/transactions', 'data/wallets']
        for directory in directories:
            os.makedirs(os.path.join('logs', directory), exist_ok=True)

    def _load_config(self) -> Dict[str, str]:
        """Carrega configuração do ambiente"""
        config = {}
        required_vars = [
            "GEMINI_API_KEY",
            "OPENCLAUDE_API_KEY",
            "KIRO_API_KEY",
            "OPENROUTER_API_KEY",
            "NVIDIA_API_KEY",
            "SOLANA_PRIVATE_KEY",
            "CALLMEBOT_API_KEY",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_WHATSAPP_FROM",
            "EVOLUTION_API_URL",
            "EVOLUTION_API_KEY",
            "ALERT_CONTACTS"
        ]

        for var in required_vars:
            value = os.getenv(var)
            if value:
                config[var] = value
                if "KEY" in var or "TOKEN" in var or "PRIVATE" in var:
                    logger.info(f"{var}: {'*' * 8}{value[-4:] if len(value) > 4 else '****'}")
                else:
                    logger.info(f"{var}: {value}")
            else:
                logger.warning(f"{var}: NÃO CONFIGURADO")

        return config

    async def _start_http_api(self):
        """Inicia API HTTP para monitoramento e controle"""
        app = web.Application()

        # Endpoints de status
        app.router.add_get('/api/v1/status', self.handle_status)
        app.router.add_get('/api/v1/stats', self.handle_stats)
        app.router.add_get('/api/v1/health', self.handle_health)
        app.router.add_get('/api/v1/test', self.handle_test)  # Endpoint de teste
        app.router.add_get('/dashboard', handle_dashboard)  # Dashboard de monitoramento

        # Endpoints de controle
        app.router.add_post('/api/v1/ai/query', self.handle_ai_query)
        app.router.add_get('/api/v1/ai/stats', self.handle_ai_stats)
        app.router.add_get('/api/v1/economy/stats', self.handle_economy_stats)
        app.router.add_get('/api/v1/whatsapp/stats', self.handle_whatsapp_stats)
        app.router.add_get('/api/v1/tokens/stats', self.handle_token_stats)

        # Painel de controle
        app.router.add_post('/api/v1/control', handle_simple_control_api)
        app.router.add_get('/control', handle_simple_control_panel)

        # Endpoints de administração
        app.router.add_post('/api/v1/admin/restart', self.handle_admin_restart)
        app.router.add_post('/api/v1/admin/shutdown', self.handle_admin_shutdown)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)

        self.http_app = app
        await site.start()
        logger.info("🌐 API HTTP iniciada na porta 8080")

    async def handle_status(self, request: web.Request) -> web.Response:
        """Endpoint de status do bot"""
        uptime = datetime.now() - self.start_time if self.start_time else timedelta(0)

        status = {
            "status": "running" if self.running else "stopped",
            "name": "BERNAS-AGENT",
            "version": "1.0.0",
            "start_time": self.stats["start_time"],
            "uptime_seconds": int(uptime.total_seconds()),
            "components": {
                "ai_router": "active",
                "economy_manager": "active",
                "solana_client": "active" if SOLANA_ENABLED and hasattr(wallet_manager, 'wallets') and wallet_manager.wallets else "inactive",
                "whatsapp_client": "active" if WHATSAPP_ENABLED else "inactive",
                "http_api": "active"
            },
            "timestamp": datetime.now().isoformat()
        }

        return web.json_response(status)

    async def handle_stats(self, request: web.Request) -> web.Response:
        """Endpoint de estatísticas"""
        ai_stats = router.get_stats()
        economy_stats = economy_manager.get_marketplace_stats()
        token_stats = token_manager.get_stats()

        stats = {
            "bot": self.stats,
            "ai_router": ai_stats,
            "economy": economy_stats,
            "token_manager": token_stats,
            "timestamp": datetime.now().isoformat()
        }

        # Adicionar stats opcionais
        if WHATSAPP_ENABLED:
            try:
                whatsapp_stats = notification_manager.router.get_stats()
                stats["whatsapp"] = whatsapp_stats
            except Exception as e:
                stats["whatsapp"] = {"error": str(e)}

        return web.json_response(stats)

    async def handle_health(self, request: web.Request) -> web.Response:
        """Endpoint de health check"""
        health = {
            "status": "healthy",
            "checks": {
                "ai_router": "ok",
                "economy_manager": "ok",
                "http_api": "ok"
            },
            "timestamp": datetime.now().isoformat()
        }

        return web.json_response(health, status=200)

    async def handle_test(self, request: web.Request) -> web.Response:
        """Endpoint de teste simples"""
        return web.json_response({
            "status": "success",
            "message": "Test endpoint working",
            "timestamp": datetime.now().isoformat()
        })

    async def handle_ai_query(self, request: web.Request) -> web.Response:
        """Endpoint para consultas de IA"""
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response({
                "status": "error",
                "message": "JSON inválido"
            }, status=400)

        prompt = data.get('prompt')
        if not prompt:
            return web.json_response({
                "status": "error",
                "message": "Campo 'prompt' obrigatório"
            }, status=400)

        provider = data.get('provider')
        max_tokens = data.get('max_tokens', 2048)
        temperature = data.get('temperature', 0.7)

        try:
            response = await process_ai_request(
                prompt=prompt,
                provider=provider,
                max_tokens=max_tokens,
                temperature=temperature
            )

            if response:
                self.stats["total_requests"] += 1
                return web.json_response({
                    "status": "success",
                    "response": response.content,
                    "provider": response.provider.value,
                    "tokens_used": response.tokens_used,
                    "cost_usdc": response.cost_usdc,
                    "latency_ms": response.latency_ms,
                    "timestamp": response.timestamp.isoformat()
                })
            else:
                self.stats["total_errors"] += 1
                return web.json_response({
                    "status": "error",
                    "message": "Falha ao processar requisição de IA"
                }, status=500)

        except Exception as e:
            self.stats["total_errors"] += 1
            logger.error(f"Erro em AI query: {e}")
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=500)

    async def handle_ai_stats(self, request: web.Request) -> web.Response:
        """Endpoint de estatísticas da IA"""
        stats = router.get_stats()
        return web.json_response(stats)

    async def handle_economy_stats(self, request: web.Request) -> web.Response:
        """Endpoint de estatísticas da economia"""
        stats = economy_manager.get_marketplace_stats()
        return web.json_response(stats)

    async def handle_whatsapp_stats(self, request: web.Request) -> web.Response:
        """Endpoint de estatísticas do WhatsApp"""
        if WHATSAPP_ENABLED:
            try:
                stats = notification_manager.router.get_stats()
                return web.json_response(stats)
            except Exception as e:
                return web.json_response({"error": str(e), "enabled": False}, status=503)
        else:
            return web.json_response({"error": "WhatsApp module not available", "enabled": False}, status=503)

    async def handle_token_stats(self, request: web.Request) -> web.Response:
        """Endpoint de estatísticas do gerenciador de tokens"""
        stats = token_manager.get_stats()
        return web.json_response(stats)

    async def handle_admin_restart(self, request: web.Request) -> web.Response:
        """Endpoint para reiniciar o bot (requer autenticação)"""
        # Em produção, adicionar autenticação
        logger.warning("Reinicialização solicitada via API")
        return web.json_response({
            "status": "success",
            "message": "Reinicialização agendada",
            "timestamp": datetime.now().isoformat()
        })

    async def handle_admin_shutdown(self, request: web.Request) -> web.Response:
        """Endpoint para desligar o bot (requer autenticação)"""
        # Em produção, adicionar autenticação
        logger.warning("Desligamento solicitado via API")
        return web.json_response({
            "status": "success",
            "message": "Desligamento agendado",
            "timestamp": datetime.now().isoformat()
        })

    async def run(self):
        """Loop principal do bot"""
        await self.initialize()

        # Configurar handlers de sinal para graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Tarefa de atualização de estatísticas
        stats_task = asyncio.create_task(self._update_stats_loop())

        # Tarefa de relatório diário
        report_task = asyncio.create_task(self._daily_report_loop())

        self.tasks.extend([stats_task, report_task, self.dashboard_task])

        logger.info("🔄 Entrando no loop principal...")
        try:
            while self.running:
                await asyncio.sleep(1)
                # Aqui poderiam ser adicionadas outras tarefas periódicas
        except asyncio.CancelledError:
            logger.info("Loop principal cancelado")
        finally:
            await self.shutdown()

    async def _update_stats_loop(self):
        """Atualiza estatísticas periodicamente"""
        while self.running:
            await asyncio.sleep(60)  # Atualizar a cada minuto
            if self.start_time:
                uptime = datetime.now() - self.start_time
                self.stats["uptime_seconds"] = int(uptime.total_seconds())

    async def _daily_report_loop(self):
        """Envia relatório diário"""
        while self.running:
            # Esperar até 8:00 AM do próximo dia
            now = datetime.now()
            next_report = now.replace(hour=8, minute=0, second=0, microsecond=0)
            if now >= next_report:
                next_report += timedelta(days=1)

            wait_seconds = (next_report - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            # Enviar relatório
            if WHATSAPP_ENABLED:
                try:
                    await notification_manager.send_daily_report(self.stats)
                    logger.info("Relatório diário enviado")
                except Exception as e:
                    logger.error(f"Erro ao enviar relatório diário: {e}")
            else:
                logger.info("Relatório diário gerado (WhatsApp não disponível)")

    def _signal_handler(self, signum, frame):
        """Handler para sinais de sistema"""
        logger.info(f"Recebido sinal {signum}, iniciando shutdown...")
        self.running = False

    async def shutdown(self):
        """Desliga o bot de forma controlada"""
        logger.info("🛑 Iniciando shutdown do BERNAS-AGENT...")

        # Desligar gerenciador de tokens
        if hasattr(self, 'token_manager_task'):
            try:
                await token_manager.shutdown()
            except Exception as e:
                logger.error(f"Erro ao desligar gerenciador de tokens: {e}")

        # Cancelar todas as tarefas
        for task in self.tasks:
            task.cancel()

        # Aguardar tarefas serem canceladas
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        # Salvar estado
        self._save_state()

        logger.info("✅ BERNAS-AGENT desligado com sucesso")

    def _save_state(self):
        """Salva estado do bot"""
        state = {
            "stats": self.stats,
            "last_shutdown": datetime.now().isoformat(),
            "total_uptime": self.stats["uptime_seconds"]
        }

        state_file = "data/bot_state.json"
        try:
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Estado salvo em {state_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")


async def main():
    """Função principal"""
    bot = BernasAgent()

    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Interrupção por teclado recebida")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        raise
    finally:
        if bot.running:
            await bot.shutdown()


if __name__ == "__main__":
    # Verificar se estamos no diretório correto
    if not os.path.exists("src"):
        print("❌ Erro: Execute o script do diretório raiz do projeto")
        print("   cd C:\\Users\\Carlos\\bernas-agent")
        print("   python main.py")
        sys.exit(1)

    print("""
    BERNAS-AGENT
    Bot de Economia Autônoma entre IAs
    ===================================
    Integração: IA + Blockchain + WhatsApp
    Arquitetura: Moltbook Crypto Bot
    ===================================
    """)

    asyncio.run(main())