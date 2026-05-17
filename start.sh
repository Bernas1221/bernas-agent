#!/bin/bash
# Script de inicialização para Render.com
# Este script é executado a partir do diretório /opt/render/project/src/

echo "=========================================="
echo "🚀 Iniciando BERNAS-AGENT no Render.com"
echo "=========================================="

# Mostrar diretório atual e conteúdo
echo "📁 Diretório atual: $(pwd)"
echo "📁 Conteúdo:"
ls -la

# Verificar se app.py existe
if [ -f "app.py" ]; then
    echo "✅ app.py encontrado"
else
    echo "❌ app.py NÃO encontrado"
    echo "📁 Procurando em subdiretórios..."
    find . -name "app.py" -type f
    exit 1
fi

# Verificar Python
echo "🐍 Python version:"
python --version

# Instalar dependências (já feito pelo build command)
echo "📦 Verificando dependências..."
pip list | grep -E "(aiohttp|httpx|pydantic)"

# Iniciar aplicação
echo "🤖 Iniciando BERNAS-AGENT..."
exec python app.py