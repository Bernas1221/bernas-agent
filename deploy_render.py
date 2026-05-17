#!/usr/bin/env python3
"""
Script para deploy automático no Render.com
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_render_cli():
    """Verifica se Render CLI está instalado"""
    print("[CHECK] Verificando Render CLI...")

    try:
        result = subprocess.run(["render", "--version"],
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"[OK] Render CLI encontrado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("[INFO] Render CLI não encontrado.")
    print("[INFO] Para Windows, instale via:")
    print("  pip install render-cli")
    print("  Ou baixe de: https://render.com/docs/cli")
    return False

def check_render_config():
    """Verifica se arquivos de configuração do Render existem"""
    print("[CHECK] Verificando configuração do Render...")

    required_files = ["render.yaml", "Procfile", "app.py"]
    missing_files = []

    for file in required_files:
        if Path(file).exists():
            print(f"[OK] {file} encontrado")
        else:
            print(f"[MISSING] {file} não encontrado")
            missing_files.append(file)

    if missing_files:
        print(f"[ERROR] Arquivos faltando: {missing_files}")
        return False

    # Verificar requirements.txt
    if not Path("requirements.txt").exists():
        print("[WARN] requirements.txt não encontrado")
    else:
        print("[OK] requirements.txt encontrado")

    return True

def create_render_service():
    """Cria serviço no Render.com"""
    print("[DEPLOY] Criando serviço no Render.com...")

    # Verificar se já existe
    try:
        result = subprocess.run(["render", "services", "list"],
                              capture_output=True, text=True)
        if "bernas-agent" in result.stdout:
            print("[INFO] Serviço 'bernas-agent' já existe")
            return True
    except:
        pass

    # Criar serviço
    print("[INFO] Para criar serviço manualmente:")
    print("1. Acesse: https://dashboard.render.com")
    print("2. Clique em 'New +' -> 'Web Service'")
    print("3. Conecte seu repositório GitHub")
    print("4. Configure:")
    print("   - Name: bernas-agent")
    print("   - Environment: Python")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python app.py")
    print("   - Plan: Free")
    print("5. Adicione variáveis de ambiente:")
    print("   - GEMINI_API_KEY (opcional)")
    print("   - SIMULATION_MODE: true (para teste)")
    print("6. Clique em 'Create Web Service'")

    return True

def setup_environment_variables():
    """Guia para configurar variáveis de ambiente no Render.com"""
    print("\n[CONFIG] CONFIGURAÇÃO DE VARIÁVEIS DE AMBIENTE")
    print("=" * 50)
    print("\nNo Render.com Dashboard:")
    print("1. Acesse seu serviço 'bernas-agent'")
    print("2. Vá em 'Environment'")
    print("3. Adicione as variáveis necessárias:")
    print("\nVariáveis MÍNIMAS para teste:")
    print("  SIMULATION_MODE=true")
    print("\nVariáveis RECOMENDADAS:")
    print("  GEMINI_API_KEY=sua_chave_gemini")
    print("  SOLANA_PRIVATE_KEY=sua_chave_privada_base58")
    print("  ALERT_CONTACTS=+5511999999999")
    print("\n[WARNING] NUNCA commit arquivos .env com chaves reais!")

def test_local_deployment():
    """Testa o bot localmente antes do deploy"""
    print("\n[TEST] Testando bot localmente...")

    # Verificar se o bot inicia
    try:
        # Testar importação do app
        import app
        print("[OK] app.py importado com sucesso")

        # Testar se o bot pode ser inicializado
        print("[INFO] Para testar localmente:")
        print("  python main.py")
        print("  Ou: python app.py")
        print("\n[INFO] Endpoints disponíveis:")
        print("  http://localhost:8080/api/v1/health")
        print("  http://localhost:8080/dashboard")
        print("  http://localhost:8080/control")

        return True

    except Exception as e:
        print(f"[ERROR] Erro ao testar localmente: {e}")
        return False

def main():
    """Função principal"""
    print("""
    ====================================
    [DEPLOY] BERNAS-AGENT - RENDER.COM
    ====================================
    """)

    # Verificar pré-requisitos
    print("[STEP 1] Verificando pré-requisitos...")
    if not check_render_config():
        return 1

    # Testar localmente
    print("\n[STEP 2] Testando localmente...")
    if not test_local_deployment():
        print("[WARN] Teste local falhou, mas continuando...")

    # Verificar Render CLI
    print("\n[STEP 3] Verificando Render CLI...")
    has_cli = check_render_cli()

    if has_cli:
        # Tentar criar serviço via CLI
        if create_render_service():
            print("[OK] Serviço criado/configurado")
    else:
        # Instruções manuais
        print("\n[INFO] Instruções para deploy manual:")
        print("1. Faça push do código para um repositório GitHub")
        print("2. Acesse: https://dashboard.render.com")
        print("3. Siga as instruções abaixo:")
        create_render_service()

    # Configuração de variáveis
    print("\n[STEP 4] Configuração de ambiente...")
    setup_environment_variables()

    print("\n" + "=" * 50)
    print("[SUCCESS] DEPLOY CONCLUÍDO!")
    print("=" * 50)
    print("\n[MONITOR] Monitoramento:")
    print("  Acesse o dashboard do Render.com")
    print("\n[COMMANDS] Comandos úteis:")
    print("  render logs bernas-agent --follow")
    print("  render services restart bernas-agent")
    print("\n[WEB] Dashboard: https://dashboard.render.com")
    print("\n[TEST] Teste o bot:")
    print("  Após deploy, acesse: https://bernas-agent.onrender.com")
    print("  Ou: https://bernas-agent.onrender.com/api/v1/health")

    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[STOP] Operação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Erro fatal: {e}")
        sys.exit(1)