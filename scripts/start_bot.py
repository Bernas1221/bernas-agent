#!/usr/bin/env python3
"""
Script de inicialização do BERNAS-AGENT
Para uso com Square Cloud ou outros serviços de hospedagem
"""

import os
import sys
import subprocess
import time
import signal
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    logger.info("🔍 Verificando ambiente...")

    # Verificar Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 11):
        logger.error(f"Python 3.11+ requerido. Versão atual: {python_version.major}.{python_version.minor}")
        return False

    logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Verificar diretórios
    required_dirs = ['src', 'src/economy', 'src/solana', 'src/whatsapp', 'logs', 'data']
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            logger.warning(f"Diretório não encontrado: {dir_path}")
            try:
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"📁 Diretório criado: {dir_path}")
            except Exception as e:
                logger.error(f"Erro ao criar diretório {dir_path}: {e}")
                return False

    # Verificar arquivo .env
    env_file = '.env'
    if not os.path.exists(env_file):
        logger.warning(f"Arquivo {env_file} não encontrado")
        # Copiar template se existir
        template_file = 'config/.env.example'
        if os.path.exists(template_file):
            try:
                import shutil
                shutil.copy(template_file, env_file)
                logger.info(f"📄 Template copiado para {env_file}")
                logger.info("⚠️  Configure as variáveis de ambiente antes de iniciar o bot")
                return False
            except Exception as e:
                logger.error(f"Erro ao copiar template: {e}")
        else:
            logger.error(f"Template {template_file} não encontrado")
            return False
    else:
        logger.info(f"✅ Arquivo {env_file} encontrado")

    # Verificar variáveis de ambiente mínimas
    required_vars = ['SOLANA_PRIVATE_KEY', 'ALERT_CONTACTS']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.warning(f"Variáveis de ambiente não configuradas: {', '.join(missing_vars)}")
        logger.info("⚠️  Configure estas variáveis no arquivo .env")
        # Não falhar, apenas avisar

    return True


def install_dependencies():
    """Instala dependências do projeto"""
    logger.info("📦 Instalando dependências...")

    requirements_file = 'requirements.txt'
    if not os.path.exists(requirements_file):
        logger.error(f"Arquivo {requirements_file} não encontrado")
        return False

    try:
        # Usar pip do ambiente virtual se existir
        pip_cmd = [sys.executable, '-m', 'pip', 'install', '-r', requirements_file]

        logger.info(f"Executando: {' '.join(pip_cmd)}")
        result = subprocess.run(
            pip_cmd,
            capture_output=True,
            text=True,
            check=True
        )

        logger.info("✅ Dependências instaladas com sucesso")
        if result.stdout:
            logger.debug(f"Saída: {result.stdout[:500]}...")

        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao instalar dependências: {e}")
        if e.stderr:
            logger.error(f"Erro detalhado: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        return False


def start_bot():
    """Inicia o bot principal"""
    logger.info("🚀 Iniciando BERNAS-AGENT...")

    bot_script = 'main.py'
    if not os.path.exists(bot_script):
        logger.error(f"Arquivo principal {bot_script} não encontrado")
        return False

    try:
        # Iniciar o bot em um subprocesso
        cmd = [sys.executable, bot_script]

        logger.info(f"Executando: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Monitorar saída
        def monitor_output():
            for line in iter(process.stdout.readline, ''):
                logger.info(f"🤖 {line.strip()}")

        import threading
        monitor_thread = threading.Thread(target=monitor_output, daemon=True)
        monitor_thread.start()

        # Aguardar processo
        logger.info("✅ Bot iniciado. Monitorando saída...")
        logger.info("📱 Aguardando alerta 'Bot Online' no WhatsApp...")

        # Manter script rodando enquanto o bot estiver ativo
        try:
            process.wait()
        except KeyboardInterrupt:
            logger.info("🛑 Interrupção recebida. Encerrando bot...")
            process.send_signal(signal.SIGINT)
            process.wait(timeout=30)

        return_code = process.returncode
        logger.info(f"Bot encerrado com código: {return_code}")

        return return_code == 0

    except Exception as e:
        logger.error(f"❌ Erro ao iniciar bot: {e}")
        return False


def setup_square_cloud():
    """Configurações específicas para Square Cloud"""
    logger.info("☁️  Configurando para Square Cloud...")

    # Verificar se estamos no Square Cloud
    square_env = os.getenv('SQUARE_CLOUD_APP_ID')
    if square_env:
        logger.info(f"✅ Executando no Square Cloud (App ID: {square_env})")

        # Configurar porta para Square Cloud
        port = os.getenv('PORT', '8080')
        os.environ['HTTP_PORT'] = port
        logger.info(f"🌐 Porta HTTP configurada: {port}")

        # Configurar logs para Square Cloud
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        logger.info(f"📁 Diretório de logs: {log_dir}")

        return True
    else:
        logger.info("ℹ️  Ambiente local detectado")
        return True


def main():
    """Função principal do script de inicialização"""
    print("""
    ============================================
    🤖 BERNAS-AGENT - SCRIPT DE INICIALIZAÇÃO 🤖
    ============================================
    """)

    # Configurar para Square Cloud se aplicável
    setup_square_cloud()

    # Verificar ambiente
    if not check_environment():
        logger.error("❌ Falha na verificação do ambiente")
        return 1

    # Instalar dependências
    if not install_dependencies():
        logger.error("❌ Falha na instalação de dependências")
        return 1

    # Iniciar bot
    if not start_bot():
        logger.error("❌ Falha ao iniciar bot")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("🛑 Script interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)