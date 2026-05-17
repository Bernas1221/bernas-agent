#!/usr/bin/env python3
"""
Script de inicialização completo do BERNAS-AGENT
Inicia todos os sistemas: Discord, MOLTBOOK, Revenue Generators, etc.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Imprime banner do sistema"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                🤖 BERNAS-AGENT v2.0                      ║
    ║          Sistema Completo de Economia Autônoma           ║
    ║                                                          ║
    ║  ✅ Render.com: https://bernas-agent.onrender.com        ║
    ║  ✅ GitHub: https://github.com/Bernas1221/bernas-agent   ║
    ║  ✅ Discord: Conversa em tempo real                      ║
    ║  ✅ MOLTBOOK: Dashboard profissional                     ║
    ║  ✅ +30 Formas de Gerar Dinheiro                         ║
    ║  ✅ 24/7 Gerando receita automática                      ║
    ╚══════════════════════════════════════════════════════════╝
    """)

async def start_discord_bot():
    """Inicia o bot Discord"""
    try:
        from src.discord.discord_bot import start_discord_bot as start_discord
        logger.info("🤖 Iniciando Discord Bot...")

        # Verificar se token está configurado
        if not os.getenv("DISCORD_BOT_TOKEN"):
            logger.warning("⚠️  DISCORD_BOT_TOKEN não configurado. Discord Bot desativado.")
            logger.info("💡 Configure: DISCORD_BOT_TOKEN=seu_token_no_render.com")
            return None

        bot = await start_discord()
        if bot:
            logger.info("✅ Discord Bot iniciado com sucesso")
            return bot
        else:
            logger.warning("⚠️  Discord Bot não pôde ser iniciado")
            return None

    except ImportError as e:
        logger.warning(f"⚠️  Módulo Discord não disponível: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar Discord Bot: {e}")
        return None

async def start_moltbook_dashboard():
    """Inicia dashboard MOLTBOOK"""
    try:
        from src.monitoring.moltbook_dashboard import start_moltbook_monitoring
        logger.info("📊 Iniciando MOLTBOOK Dashboard...")

        task = await start_moltbook_monitoring()
        if task:
            logger.info("✅ MOLTBOOK Dashboard iniciado")
            return task
        else:
            logger.warning("⚠️  MOLTBOOK Dashboard não pôde ser iniciado")
            return None

    except ImportError as e:
        logger.warning(f"⚠️  Módulo MOLTBOOK não disponível: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar MOLTBOOK: {e}")
        return None

async def start_revenue_generators():
    """Inicia geradores de receita"""
    try:
        from src.revenue.revenue_generators import revenue_generator
        logger.info("💰 Iniciando Geradores de Receita...")

        # Testar alguns geradores
        test_results = await revenue_generator.generate_bulk_revenue(3)
        total_revenue = sum(float(r.get("revenue", 0)) for r in test_results)

        logger.info(f"✅ {len(revenue_generator.generators)} geradores de receita carregados")
        logger.info(f"💰 Receita de teste: {total_revenue:.4f} USDC")

        # Iniciar geração automática em background
        async def generate_continuous_revenue():
            """Gera receita continuamente"""
            while True:
                try:
                    # Gerar receita a cada minuto
                    await asyncio.sleep(60)
                    results = await revenue_generator.generate_bulk_revenue(
                        random.randint(1, 5)  # 1-5 transações por minuto
                    )

                    total = sum(float(r.get("revenue", 0)) for r in results)
                    if total > 0:
                        logger.info(f"💰 Receita gerada: +{total:.4f} USDC (automática)")

                except Exception as e:
                    logger.error(f"Erro na geração automática de receita: {e}")
                    await asyncio.sleep(300)  # Esperar 5 minutos em caso de erro

        # Iniciar em background
        import random
        task = asyncio.create_task(generate_continuous_revenue())
        return task

    except ImportError as e:
        logger.warning(f"⚠️  Módulo Revenue Generators não disponível: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar Revenue Generators: {e}")
        return None

async def start_main_bot():
    """Inicia o bot principal (servidor HTTP)"""
    try:
        from app import app
        from aiohttp import web

        # Configurar porta
        PORT = int(os.getenv("PORT", "8080"))
        HOST = "0.0.0.0"

        # Adicionar endpoints do MOLTBOOK
        from src.monitoring.moltbook_dashboard import (
            handle_moltbook_dashboard,
            handle_moltbook_metrics
        )

        app.router.add_get('/moltbook', handle_moltbook_dashboard)
        app.router.add_get('/api/v1/moltbook/metrics', handle_moltbook_metrics)

        # Iniciar servidor
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, HOST, PORT)
        await site.start()

        logger.info(f"🌐 Servidor HTTP iniciado em http://{HOST}:{PORT}")
        logger.info(f"📊 Dashboard: http://{HOST}:{PORT}/dashboard")
        logger.info(f"📈 MOLTBOOK: http://{HOST}:{PORT}/moltbook")
        logger.info(f"❤️  Health: http://{HOST}:{PORT}/api/v1/health")

        return runner

    except ImportError as e:
        logger.error(f"❌ Erro ao importar módulos principais: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor HTTP: {e}")
        raise

async def monitor_systems():
    """Monitora todos os sistemas"""
    logger.info("🔍 Iniciando monitoramento de sistemas...")

    systems_status = {
        "http_server": False,
        "discord_bot": False,
        "moltbook": False,
        "revenue_generators": False,
        "start_time": datetime.now().isoformat()
    }

    async def check_status_periodically():
        """Verifica status periodicamente"""
        while True:
            try:
                # Coletar métricas de todos os sistemas
                status_report = {
                    "timestamp": datetime.now().isoformat(),
                    "systems": systems_status.copy()
                }

                # Adicionar métricas de receita se disponível
                try:
                    from src.revenue.revenue_generators import revenue_generator
                    revenue_stats = revenue_generator.get_stats()
                    status_report["revenue"] = revenue_stats
                except:
                    pass

                logger.info(f"📈 Status do sistema: {status_report}")

                # Verificar alertas
                await check_alerts()

            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")

            await asyncio.sleep(60)  # Verificar a cada minuto

    async def check_alerts():
        """Verifica alertas do sistema"""
        alerts = []

        # Verificar saldo (se token_manager disponível)
        try:
            from token_manager.token_manager import token_manager
            token_stats = token_manager.get_stats()
            balance = token_stats.get("current_balance", 0)

            if balance < 10:
                alerts.append({
                    "level": "warning",
                    "message": f"Saldo baixo: {balance:.2f} USDC",
                    "action": "Configurar auto-recarga"
                })
        except:
            pass

        if alerts:
            for alert in alerts:
                logger.warning(f"⚠️  ALERTA: {alert['message']}")

    # Iniciar monitoramento em background
    task = asyncio.create_task(check_status_periodically())
    return task, systems_status

async def main():
    """Função principal"""
    print_banner()

    logger.info("🚀 Inicializando BERNAS-AGENT v2.0...")
    logger.info(f"📅 Data: {datetime.now().isoformat()}")
    logger.info(f"🐍 Python: {sys.version}")
    logger.info(f"📁 Diretório: {os.getcwd()}")

    # Lista de tarefas
    tasks = []
    systems = {}

    try:
        # 1. Iniciar monitoramento
        monitor_task, systems_status = await monitor_systems()
        tasks.append(monitor_task)
        systems["monitor"] = systems_status

        # 2. Iniciar servidor HTTP principal
        logger.info("\n" + "="*50)
        logger.info("1. Iniciando Servidor HTTP...")
        http_runner = await start_main_bot()
        systems_status["http_server"] = True

        # 3. Iniciar Discord Bot (se token configurado)
        logger.info("\n" + "="*50)
        logger.info("2. Iniciando Discord Bot...")
        discord_bot = await start_discord_bot()
        if discord_bot:
            systems_status["discord_bot"] = True

        # 4. Iniciar MOLTBOOK Dashboard
        logger.info("\n" + "="*50)
        logger.info("3. Iniciando MOLTBOOK Dashboard...")
        moltbook_task = await start_moltbook_dashboard()
        if moltbook_task:
            tasks.append(moltbook_task)
            systems_status["moltbook"] = True

        # 5. Iniciar Geradores de Receita
        logger.info("\n" + "="*50)
        logger.info("4. Iniciando Geradores de Receita...")
        revenue_task = await start_revenue_generators()
        if revenue_task:
            tasks.append(revenue_task)
            systems_status["revenue_generators"] = True

        # 6. Resumo
        logger.info("\n" + "="*50)
        logger.info("✅ BERNAS-AGENT INICIALIZADO COM SUCESSO!")
        logger.info("="*50)

        active_systems = sum(1 for v in systems_status.values() if v is True)
        logger.info(f"📊 Sistemas ativos: {active_systems}/4")
        logger.info(f"🤖 Discord: {'✅' if systems_status['discord_bot'] else '❌'}")
        logger.info(f"📈 MOLTBOOK: {'✅' if systems_status['moltbook'] else '❌'}")
        logger.info(f"💰 Revenue: {'✅' if systems_status['revenue_generators'] else '❌'}")
        logger.info(f"🌐 HTTP: {'✅' if systems_status['http_server'] else '❌'}")

        logger.info("\n🔗 URLs disponíveis:")
        PORT = int(os.getenv("PORT", "8080"))
        logger.info(f"   Dashboard: http://localhost:{PORT}/dashboard")
        logger.info(f"   MOLTBOOK: http://localhost:{PORT}/moltbook")
        logger.info(f"   Health: http://localhost:{PORT}/api/v1/health")

        logger.info("\n💬 Comandos Discord:")
        logger.info("   !chat <mensagem> - Conversa com IA")
        logger.info("   !economy - Estatísticas da economia")
        logger.info("   !services - Lista serviços")
        logger.info("   !buy <serviço> - Compra serviço")
        logger.info("   !help - Ajuda completa")

        logger.info("\n💰 Gerando receita 24/7...")
        logger.info("="*50)

        # Manter sistema rodando
        try:
            while True:
                await asyncio.sleep(3600)  # Esperar 1 hora
        except asyncio.CancelledError:
            logger.info("🛑 Sistema interrompido")

    except KeyboardInterrupt:
        logger.info("\n🛑 Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"💥 Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Limpeza
        logger.info("🧹 Finalizando sistemas...")

        # Cancelar todas as tarefas
        for task in tasks:
            task.cancel()

        # Aguardar tarefas serem canceladas
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("✅ BERNAS-AGENT finalizado")

    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)