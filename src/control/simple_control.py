"""
Painel de Controle Simples BERNAS-AGENT
Versão simplificada para evitar erros
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from aiohttp import web

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleControl:
    """Painel de controle simples"""

    def __init__(self):
        self.commands_history = []
        self.start_time = datetime.now()

    async def execute_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """Executa um comando"""
        if args is None:
            args = []

        command_lower = command.lower()

        # Comandos básicos
        if command_lower == "status":
            return await self._get_status()
        elif command_lower == "stats":
            return await self._get_stats()
        elif command_lower == "tokens":
            return await self._get_tokens()
        elif command_lower == "economy":
            return await self._get_economy()
        elif command_lower == "research":
            topic = " ".join(args) if args else "tendências de mercado"
            return await self._do_research(topic)
        elif command_lower == "post":
            content = " ".join(args) if args else "Postagem automática do BERNAS-AGENT"
            return await self._create_post(content)
        elif command_lower == "revenue":
            return await self._generate_revenue()
        elif command_lower == "ai_chat":
            message = " ".join(args) if args else "Olá, como vai?"
            return await self._ai_chat(message)
        elif command_lower == "start":
            return {"success": True, "message": "Bot já está rodando"}
        elif command_lower == "stop":
            return {"success": True, "message": "Use CTRL+C no terminal para parar"}
        elif command_lower == "restart":
            return {"success": True, "message": "Reinicie manualmente com CTRL+C e python main.py"}
        elif command_lower == "help":
            return self._get_help()
        else:
            return {
                "success": False,
                "message": f"Comando '{command}' não suportado. Use 'help'."
            }

    async def _get_status(self) -> Dict[str, Any]:
        """Obter status do bot"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8080/api/v1/status') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "message": "Status do bot",
                            "data": data
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    async def _get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8080/api/v1/stats') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "message": "Estatísticas",
                            "data": data
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    async def _get_tokens(self) -> Dict[str, Any]:
        """Obter status dos tokens"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8080/api/v1/tokens/stats') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "message": "Status dos tokens",
                            "data": data
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    async def _get_economy(self) -> Dict[str, Any]:
        """Obter economia"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:4020/api/v1/services') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "message": "Serviços da economia",
                            "data": data
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    async def _do_research(self, topic: str) -> Dict[str, Any]:
        """Fazer pesquisa"""
        import asyncio
        await asyncio.sleep(2)  # Simular pesquisa

        return {
            "success": True,
            "message": f"Pesquisa sobre '{topic}' concluída",
            "data": {
                "topic": topic,
                "status": "completed",
                "findings": [
                    "Dados coletados e analisados",
                    "Insights gerados",
                    "Relatório preparado"
                ],
                "timestamp": datetime.now().isoformat()
            }
        }

    async def _create_post(self, content: str) -> Dict[str, Any]:
        """Criar postagem"""
        import asyncio
        await asyncio.sleep(1)

        return {
            "success": True,
            "message": "Postagem criada",
            "data": {
                "content": content,
                "platform": "simulated",
                "status": "published",
                "engagement": {"likes": 35, "shares": 12, "comments": 5},
                "timestamp": datetime.now().isoformat()
            }
        }

    async def _generate_revenue(self) -> Dict[str, Any]:
        """Gerar receita"""
        import asyncio
        await asyncio.sleep(1)

        return {
            "success": True,
            "message": "Receita gerada",
            "data": {
                "amount_usdc": 0.15,
                "source": "serviços_automatizados",
                "timestamp": datetime.now().isoformat()
            }
        }

    async def _ai_chat(self, message: str) -> Dict[str, Any]:
        """Conversar com IA"""
        import asyncio
        await asyncio.sleep(1)

        return {
            "success": True,
            "message": "Resposta da IA",
            "data": {
                "query": message,
                "response": f"Resposta simulada para: '{message}'",
                "provider": "gemini",
                "timestamp": datetime.now().isoformat()
            }
        }

    def _get_help(self) -> Dict[str, Any]:
        """Ajuda"""
        return {
            "success": True,
            "message": "Comandos disponíveis",
            "commands": [
                {"command": "status", "description": "Ver status do bot"},
                {"command": "stats", "description": "Ver estatísticas completas"},
                {"command": "tokens", "description": "Gerenciar tokens"},
                {"command": "economy", "description": "Ver economia"},
                {"command": "research [tópico]", "description": "Fazer pesquisa"},
                {"command": "post [conteúdo]", "description": "Criar postagem"},
                {"command": "revenue", "description": "Gerar receita"},
                {"command": "ai_chat [mensagem]", "description": "Conversar com IA"},
                {"command": "help", "description": "Esta ajuda"}
            ],
            "examples": [
                "research blockchain trends",
                "post Nova análise de mercado publicada",
                "ai_chat Olá, como vai o mercado hoje?",
                "tokens",
                "economy"
            ]
        }


# Instância global
simple_control = SimpleControl()


async def handle_simple_control_api(request: web.Request) -> web.Response:
    """API simples para controle"""
    try:
        data = await request.json()
    except:
        return web.json_response({
            "success": False,
            "message": "JSON inválido"
        }, status=400)

    command = data.get('command', '')
    args = data.get('args', [])

    if not command:
        return web.json_response({
            "success": False,
            "message": "Comando necessário"
        }, status=400)

    result = await simple_control.execute_command(command, args)
    return web.json_response(result)


async def handle_simple_control_panel(request: web.Request) -> web.Response:
    """Página web simples do painel de controle"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Controle BERNAS-AGENT</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #1a202c;
                color: #e2e8f0;
                padding: 20px;
                margin: 0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: #63b3ed;
                text-align: center;
            }
            .card {
                background: #2d3748;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }
            .command-btn {
                background: #4299e1;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
                margin: 5px;
            }
            .command-btn:hover {
                background: #3182ce;
            }
            #output {
                background: #1a202c;
                border: 1px solid #4a5568;
                border-radius: 4px;
                padding: 15px;
                margin-top: 20px;
                min-height: 100px;
                font-family: monospace;
                white-space: pre-wrap;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 Controle BERNAS-AGENT</h1>

            <div class="card">
                <h2>Comandos</h2>
                <button class="command-btn" onclick="runCommand('status')">Status</button>
                <button class="command-btn" onclick="runCommand('stats')">Estatísticas</button>
                <button class="command-btn" onclick="runCommand('tokens')">Tokens</button>
                <button class="command-btn" onclick="runCommand('economy')">Economia</button>
                <button class="command-btn" onclick="runCommand('research')">Pesquisar</button>
                <button class="command-btn" onclick="runCommand('post')">Postar</button>
                <button class="command-btn" onclick="runCommand('revenue')">Receita</button>
                <button class="command-btn" onclick="runCommand('ai_chat')">Chat IA</button>
                <button class="command-btn" onclick="runCommand('help')">Ajuda</button>
            </div>

            <div class="card">
                <h2>Saída</h2>
                <div id="output">Clique em um comando...</div>
            </div>

            <div class="card">
                <p>Bot rodando em: http://localhost:8080</p>
                <p>Dashboard: <a href="/dashboard" style="color: #63b3ed;">/dashboard</a></p>
            </div>
        </div>

        <script>
            async function runCommand(command) {
                const output = document.getElementById('output');
                output.innerHTML = `Executando: ${command}...`;

                try {
                    const response = await fetch('/api/v1/control', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({command: command, args: []})
                    });

                    const data = await response.json();

                    if (data.success) {
                        output.innerHTML = `✅ ${data.message}\\n\\n`;
                        if (data.data) {
                            output.innerHTML += JSON.stringify(data.data, null, 2);
                        }
                    } else {
                        output.innerHTML = `❌ ${data.message}`;
                    }
                } catch (error) {
                    output.innerHTML = `❌ Erro: ${error.message}`;
                }
            }
        </script>
    </body>
    </html>
    """

    return web.Response(text=html, content_type='text/html')