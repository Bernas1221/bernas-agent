#!/usr/bin/env python3
"""
Script para deploy automático no Square Cloud
"""

import os
import sys
import json
import subprocess
import zipfile
from pathlib import Path

def create_deployment_package():
    """Cria pacote ZIP para deploy no Square Cloud"""
    print("[DEPLOY] Criando pacote de deploy...")

    # Arquivos a incluir
    include_patterns = [
        "main.py",
        "requirements.txt",
        "scripts/*.py",
        "src/**/*.py",
        "config/*",
        ".env.example",
        "README.md",
        "squarecloud.config"
    ]

    # Arquivos a excluir
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        ".venv",
        "logs",
        "data",
        ".git",
        ".env"  # Não incluir arquivo .env com chaves reais
    ]

    zip_filename = "bernas-agent-deploy.zip"

    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Adicionar arquivos principais
            for pattern in include_patterns:
                if "*" in pattern:
                    # Padrão com wildcard
                    for file_path in Path(".").glob(pattern):
                        if not any(exclude in str(file_path) for exclude in exclude_patterns):
                            arcname = str(file_path)
                            zipf.write(file_path, arcname)
                            print(f"  + {arcname}")
                else:
                    # Arquivo específico
                    if Path(pattern).exists():
                        zipf.write(pattern, pattern)
                        print(f"  + {pattern}")

        print(f"[OK] Pacote criado: {zip_filename}")
        print(f"[SIZE] Tamanho: {os.path.getsize(zip_filename) / 1024:.1f} KB")
        return zip_filename

    except Exception as e:
        print(f"[ERROR] Erro ao criar pacote: {e}")
        return None

def check_square_cli():
    """Verifica se Square CLI está instalado"""
    print("[CHECK] Verificando Square CLI...")

    # Caminhos para Windows
    windows_paths = [
        "squarecloud.cmd",
        "squarecloud",
        r"C:\Users\Carlos\AppData\Roaming\npm\squarecloud.cmd"
    ]

    for cmd in windows_paths:
        try:
            result = subprocess.run([cmd, "--version"],
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print(f"[OK] Square CLI encontrado: {result.stdout.strip()}")
                return cmd
        except FileNotFoundError:
            continue

    print("[INFO] Para Windows, use o caminho completo:")
    print(r"  C:\Users\Carlos\AppData\Roaming\npm\squarecloud.cmd")
    print("\n[INFO] Ou adicione ao PATH do Windows:")
    print(r"  C:\Users\Carlos\AppData\Roaming\npm")
    return r"C:\Users\Carlos\AppData\Roaming\npm\squarecloud.cmd"

def deploy_to_squarecloud(zip_filename, square_cmd):
    """Faz deploy no Square Cloud"""
    print(f"[DEPLOY] Iniciando deploy no Square Cloud usando comando: {square_cmd}...")

    # Verificar se app já existe
    try:
        result = subprocess.run([square_cmd, "app", "list"],
                              capture_output=True, text=True)

        if "bernas-agent" in result.stdout:
            print("[INFO] Aplicativo 'bernas-agent' já existe. Atualizando...")
            cmd = [square_cmd, "upload", zip_filename, "--app", "bernas-agent"]
        else:
            print("[NEW] Criando novo aplicativo 'bernas-agent'...")
            cmd = [square_cmd, "upload", zip_filename, "--name", "bernas-agent"]

        print(f"[CONFIG] Executando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("[OK] Deploy realizado com sucesso!")
            print(f"[OUTPUT] Saída: {result.stdout}")

            # Obter informações do app
            subprocess.run([square_cmd, "app", "status", "bernas-agent"])
            return True
        else:
            print(f"[ERROR] Erro no deploy: {result.stderr}")
            return False

    except Exception as e:
        print(f"[ERROR] Erro ao executar deploy: {e}")
        return False

def setup_environment_variables():
    """Guia para configurar variáveis de ambiente no Square Cloud"""
    print("\n[CONFIG] CONFIGURAÇÃO DE VARIÁVEIS DE AMBIENTE")
    print("=" * 50)
    print("\nNo Square Cloud Dashboard:")
    print("1. Acesse seu aplicativo 'bernas-agent'")
    print("2. Vá em 'Environment Variables'")
    print("3. Adicione as variáveis necessárias:")
    print("\nVariáveis MÍNIMAS para teste:")
    print("  SOLANA_PRIVATE_KEY=sua_chave_privada_base58")
    print("  ALERT_CONTACTS=+5511999999999")
    print("\nVariáveis RECOMENDADAS:")
    print("  GEMINI_API_KEY=sua_chave_gemini")
    print("  CALLMEBOT_API_KEY=sua_chave_callmebot")
    print("\n[WARNING] NUNCA commit arquivos .env com chaves reais!")

def main():
    """Função principal"""
    print("""
    ====================================
    [DEPLOY] BERNAS-AGENT - SQUARE CLOUD
    ====================================
    """)

    # Verificar pré-requisitos
    square_cmd = check_square_cli()
    if not square_cmd:
        print("\n[INFO] Para Windows, o comando é: squarecloud")
        print("[INFO] Se já instalou, use o caminho completo:")
        print("  C:\\Users\\Carlos\\AppData\\Roaming\\npm\\squarecloud.cmd")
        return 1

    # Criar pacote de deploy
    zip_file = create_deployment_package()
    if not zip_file:
        return 1

    # Fazer deploy
    if deploy_to_squarecloud(zip_file, square_cmd):
        setup_environment_variables()

        print("\n" + "=" * 50)
        print("[SUCCESS] DEPLOY CONCLUÍDO!")
        print("=" * 50)
        print("\n[MONITOR] Monitoramento:")
        print("  square logs bernas-agent --follow")
        print("\n[COMMANDS] Comandos úteis:")
        print("  square apps restart bernas-agent")
        print("  square apps stop bernas-agent")
        print("  square apps delete bernas-agent")
        print("\n[WEB] Dashboard: https://squarecloud.app/dashboard")

        # Limpar arquivo temporário
        try:
            os.remove(zip_file)
            print(f"\n[CLEAN] Arquivo temporário removido: {zip_file}")
        except:
            pass

        return 0
    else:
        return 1

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