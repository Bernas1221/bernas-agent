"""
Painel de Controle BERNAS-AGENT
Sistema para controlar o bot como solicitado
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import aiohttp
from aiohttp import web

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ControlPanel:
    """Painel de controle do bot"""

    def __init__(self):
        self.commands_history = []
        self.bot_status = "running"
        self.active_tasks = []
        self.start_time = datetime.now()
        self.commands = {
            "status": {
                "description": "Ver status do bot",
                "handler": self.handle_status_command
            },
            "start": {
                "description": "Iniciar o bot",
                "handler": self.handle_start_command
            },
            "stop": {
                "description": "Parar o bot",
                "handler": self.handle_stop_command
            },
            "restart": {
                "description": "Reiniciar o bot",
                "handler": self.handle_restart_command
            },
            "stats": {
                "description": "Ver estatísticas",
                "handler": self.handle_stats_command
            },
            "tokens": {
                "description": "Gerenciar tokens",
                "handler": self.handle_tokens_command
            },
            "economy": {
                "description": "Controlar economia",
                "handler": self.handle_economy_command
            },
            "research": {
                "description": "Iniciar pesquisa",
                "handler": self.handle_research_command
            },
            "post": {
                "description": "Criar postagem",
                "handler": self.handle_post_command
            },
            "revenue": {
                "description": "Gerar receita",
                "handler": self.handle_revenue_command
            },
            "ai_chat": {
                "description": "Conversar com IAs",
                "handler": self.handle_ai_chat_command
            },
            "help": {
                "description": "Ajuda",
                "handler": self.handle_help_command
            }
        }

    async def execute_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """Executa um comando"""
        if args is None:
            args = []

        command_lower = command.lower()

        if command_lower not in self.commands:
            return {
                "success": False,
                "message": f"Comando '{command}' não encontrado. Use 'help' para ver comandos disponíveis."
            }

        try:
            handler = self.commands[command_lower]["handler"]
            result = await handler(args)

            # Registrar no histórico
            self.commands_history.append({
                "command": command,
                "args": args,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })

            # Manter apenas últimos 100 comandos
            if len(self.commands_history) > 100:
                self.commands_history = self.commands_history[-100:]

            return result

        except Exception as e:
            logger.error(f"Erro ao executar comando '{command}': {e}")
            return {
                "success": False,
                "message": f"Erro ao executar comando: {str(e)}"
            }

    async def handle_status_command(self, args: List[str]) -> Dict[str, Any]:
        """Ver status do bot"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8080/api/v1/status') as resp:
                    if resp.status == 200:
                        status_data = await resp.json()
                        return {
                            "success": True,
                            "message": "Status do bot",
                            "data": status_data
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Erro ao obter status: {resp.status}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro de conexão: {str(e)}"
            }

    async def handle_start_command(self, args: List[str]) -> Dict[str, Any]:
        """Iniciar o bot"""
        # Em produção, isso iniciaria o serviço
        # Por enquanto, apenas muda o status
        self.bot_status = "running"

        return {
            "success": True,
            "message": "Bot iniciado",
            "status": self.bot_status
        }

    async def handle_stop_command(self, args: List[str]) -> Dict[str, Any]:
        """Parar o bot"""
        self.bot_status = "stopped"

        return {
            "success": True,
            "message": "Bot parado",
            "status": self.bot_status
        }

    async def handle_restart_command(self, args: List[str]) -> Dict[str, Any]:
        """Reiniciar o bot"""
        self.bot_status = "restarting"

        # Simular reinício
        await asyncio.sleep(2)
        self.bot_status = "running"

        return {
            "success": True,
            "message": "Bot reiniciado",
            "status": self.bot_status
        }

    async def handle_stats_command(self, args: List[str]) -> Dict[str, Any]:
        """Ver estatísticas"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8080/api/v1/stats') as resp:
                    if resp.status == 200:
                        stats_data = await resp.json()
                        return {
                            "success": True,
                            "message": "Estatísticas do bot",
                            "data": stats_data
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Erro ao obter estatísticas: {resp.status}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro de conexão: {str(e)}"
            }

    async def handle_tokens_command(self, args: List[str]) -> Dict[str, Any]:
        """Gerenciar tokens"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8080/api/v1/tokens/stats') as resp:
                    if resp.status == 200:
                        tokens_data = await resp.json()

                        # Se houver argumentos, processar ação
                        if args:
                            action = args[0].lower()
                            if action == "recharge":
                                return await self._recharge_tokens(args[1:] if len(args) > 1 else [])
                            elif action == "check":
                                return {
                                    "success": True,
                                    "message": "Status dos tokens",
                                    "data": tokens_data
                                }

                        return {
                            "success": True,
                            "message": "Status dos tokens",
                            "data": tokens_data,
                            "available_actions": ["check", "recharge <provider>"]
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Erro ao obter tokens: {resp.status}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro de conexão: {str(e)}"
            }

    async def _recharge_tokens(self, args: List[str]) -> Dict[str, Any]:
        """Recarregar tokens de um provedor"""
        if not args:
            return {
                "success": False,
                "message": "Especifique o provedor. Ex: recharge gemini"
            }

        provider = args[0].lower()
        providers = ["gemini", "openclaude", "kiro", "openrouter", "nvidia", "9router"]

        if provider not in providers:
            return {
                "success": False,
                "message": f"Provedor inválido. Use: {', '.join(providers)}"
            }

        # Simular recarga
        await asyncio.sleep(1)

        return {
            "success": True,
            "message": f"Tokens recarregados para {provider}",
            "provider": provider,
            "recharged": True,
            "timestamp": datetime.now().isoformat()
        }

    async def handle_economy_command(self, args: List[str]) -> Dict[str, Any]:
        """Controlar economia"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:4020/api/v1/services') as resp:
                    if resp.status == 200:
                        economy_data = await resp.json()

                        return {
                            "success": True,
                            "message": "Economia do bot",
                            "data": economy_data,
                            "available_actions": ["list_services", "check_balance <agent>", "make_transaction"]
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Erro ao obter economia: {resp.status}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro de conexão: {str(e)}"
            }

    async def handle_research_command(self, args: List[str]) -> Dict[str, Any]:
        """Iniciar pesquisa"""
        if not args:
            topic = "tendências de mercado cripto"
        else:
            topic = " ".join(args)

        # Simular pesquisa
        await asyncio.sleep(3)

        research_results = {
            "topic": topic,
            "status": "completed",
            "findings": [
                f"Pesquisa sobre '{topic}' concluída",
                "Análise de dados coletados",
                "Insights gerados",
                "Relatório preparado"
            ],
            "tokens_used": 1500,
            "duration_seconds": 3,
            "timestamp": datetime.now().isoformat()
        }

        return {
            "success": True,
            "message": f"Pesquisa sobre '{topic}' concluída",
            "data": research_results
        }

    async def handle_post_command(self, args: List[str]) -> Dict[str, Any]:
        """Criar postagem"""
        if not args:
            content = "Postagem automática do BERNAS-AGENT sobre economia IA"
        else:
            content = " ".join(args)

        # Simular criação de postagem
        await asyncio.sleep(2)

        post_data = {
            "content": content,
            "platform": "simulated",
            "status": "published",
            "engagement": {
                "likes": 42,
                "shares": 15,
                "comments": 8
            },
            "timestamp": datetime.now().isoformat()
        }

        return {
            "success": True,
            "message": "Postagem criada com sucesso",
            "data": post_data
        }

    async def handle_revenue_command(self, args: List[str]) -> Dict[str, Any]:
        """Gerar receita"""
        # Simular geração de receita
        await asyncio.sleep(2)

        revenue_data = {
            "amount_usdc": 0.25,
            "source": "serviços_automatizados",
            "services": ["análise_mercado", "geração_conteúdo"],
            "timestamp": datetime.now().isoformat()
        }

        return {
            "success": True,
            "message": "Receita gerada com sucesso",
            "data": revenue_data
        }

    async def handle_ai_chat_command(self, args: List[str]) -> Dict[str, Any]:
        """Conversar com IAs"""
        if not args:
            return {
                "success": False,
                "message": "Especifique a mensagem. Ex: ai_chat Olá, como vai?"
            }

        message = " ".join(args)

        # Simular conversa com IA
        await asyncio.sleep(1)

        chat_data = {
            "message": message,
            "response": f"Resposta simulada da IA para: '{message}'",
            "provider": "gemini",
            "tokens_used": 120,
            "timestamp": datetime.now().isoformat()
        }

        return {
            "success": True,
            "message": "Conversa com IA concluída",
            "data": chat_data
        }

    async def handle_help_command(self, args: List[str]) -> Dict[str, Any]:
        """Ajuda"""
        commands_list = []
        for cmd_name, cmd_info in self.commands.items():
            commands_list.append({
                "command": cmd_name,
                "description": cmd_info["description"]
            })

        return {
            "success": True,
            "message": "Comandos disponíveis",
            "commands": commands_list,
            "usage": "Use: /comando [argumentos]",
            "examples": [
                "/status - Ver status do bot",
                "/research blockchain - Pesquisar sobre blockchain",
                "/post Nova atualização - Criar postagem",
                "/tokens check - Verificar tokens",
                "/ai_chat Olá - Conversar com IA"
            ]
        }

    def get_control_panel_data(self) -> Dict[str, Any]:
        """Retorna dados do painel de controle"""
        return {
            "status": self.bot_status,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "commands_count": len(self.commands_history),
            "available_commands": list(self.commands.keys()),
            "recent_commands": self.commands_history[-10:] if self.commands_history else [],
            "timestamp": datetime.now().isoformat()
        }


# Instância global do painel de controle
control_panel = ControlPanel()


async def handle_control_api(request: web.Request) -> web.Response:
    """API para controle do bot"""
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({
            "success": False,
            "message": "JSON inválido"
        }, status=400)

    command = data.get('command')
    args = data.get('args', [])

    if not command:
        return web.json_response({
            "success": False,
            "message": "Campo 'command' obrigatório"
        }, status=400)

    result = await control_panel.execute_command(command, args)
    return web.json_response(result)


async def handle_control_panel(request: web.Request) -> web.Response:
    """Página web do painel de controle"""
    try:
        html_content = generate_control_panel_html()
        return web.Response(text=html_content, content_type='text/html')
    except Exception as e:
        logger.error(f"Erro ao gerar painel de controle: {e}")
        # Retornar uma página de erro simples
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Erro - Painel de Controle</title></head>
        <body>
            <h1>Erro no Painel de Controle</h1>
            <p>Erro: {str(e)}</p>
            <p>API de controle funciona: <a href="/api/v1/control">/api/v1/control</a></p>
        </body>
        </html>
        """
        return web.Response(text=error_html, content_type='text/html')


def generate_control_panel_html() -> str:
    """Gera HTML do painel de controle"""
    data = control_panel.get_control_panel_data()

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Controle BERNAS-AGENT</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
                color: #e2e8f0;
                min-height: 100vh;
                padding: 20px;
                margin: 0;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }}
            .header h1 {{
                color: #63b3ed;
                font-size: 2.5rem;
                margin-bottom: 10px;
            }}
            .header .subtitle {{
                color: #a0aec0;
                font-size: 1.1rem;
            }}
            .status-badge {{
                display: inline-block;
                background: #48bb78;
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                font-weight: bold;
                font-size: 1.2rem;
                margin-top: 10px;
            }}
            .status-badge.stopped {{ background: #f56565; }}
            .status-badge.restarting {{ background: #ed8936; }}
            .control-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .card {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .card h2 {{
                color: #63b3ed;
                margin-bottom: 15px;
                font-size: 1.3rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding-bottom: 10px;
            }}
            .command-list {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 10px;
            }}
            .command-btn {{
                background: #4299e1;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 0.9rem;
                text-align: left;
                transition: background 0.3s ease;
            }}
            .command-btn:hover {{
                background: #3182ce;
            }}
            .command-btn.danger {{ background: #f56565; }}
            .command-btn.danger:hover {{ background: #e53e3e; }}
            .command-btn.success {{ background: #48bb78; }}
            .command-btn.success:hover {{ background: #38a169; }}
            .input-group {{
                margin-bottom: 15px;
            }}
            .input-group label {{
                display: block;
                color: #a0aec0;
                margin-bottom: 5px;
                font-size: 0.9rem;
            }}
            .input-group input {{
                width: 100%;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                background: rgba(0, 0, 0, 0.3);
                color: white;
                font-size: 1rem;
            }}
            .execute-btn {{
                background: #48bb78;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1rem;
                width: 100%;
                margin-top: 10px;
            }}
            .execute-btn:hover {{
                background: #38a169;
            }}
            .output-container {{
                background: rgba(0, 0, 0, 0.3);
                border-radius: 5px;
                padding: 15px;
                margin-top: 20px;
                max-height: 300px;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
            }}
            .output-line {{
                margin-bottom: 5px;
                padding: 5px;
                border-radius: 3px;
                background: rgba(255, 255, 255, 0.05);
            }}
            .output-line.success {{ color: #48bb78; }}
            .output-line.error {{ color: #f56565; }}
            .output-line.info {{ color: #63b3ed; }}
            .history-container {{
                max-height: 200px;
                overflow-y: auto;
                margin-top: 10px;
            }}
            .history-item {{
                padding: 8px;
                margin-bottom: 5px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 3px;
                font-size: 0.8rem;
            }}
            .footer {{
                text-align: center;
                color: #a0aec0;
                margin-top: 30px;
                font-size: 0.9rem;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                padding-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎮 Controle BERNAS-AGENT</h1>
                <p class="subtitle">Controle completo do bot de economia autônoma</p>
                <p class="subtitle">Uptime: {(data['uptime_seconds'] / 3600):.1f} horas | Comandos: {data['commands_count']}</p>
                <div class="status-badge {data['status']}">{data['status'].upper()}</div>
            </div>

            <div class="control-grid">
                <div class="card">
                    <h2>⚡ Comandos Rápidos</h2>
                    <div class="command-list">
                        <button class="command-btn" onclick="executeCommand('status')">Status</button>
                        <button class="command-btn" onclick="executeCommand('stats')">Estatísticas</button>
                        <button class="command-btn" onclick="executeCommand('tokens')">Tokens</button>
                        <button class="command-btn" onclick="executeCommand('economy')">Economia</button>
                        <button class="command-btn success" onclick="executeCommand('start')">Iniciar</button>
                        <button class="command-btn danger" onclick="executeCommand('stop')">Parar</button>
                        <button class="command-btn" onclick="executeCommand('restart')">Reiniciar</button>
                        <button class="command-btn success" onclick="executeCommand('research')">Pesquisar</button>
                        <button class="command-btn success" onclick="executeCommand('post')">Postar</button>
                        <button class="command-btn success" onclick="executeCommand('revenue')">Gerar Receita</button>
                        <button class="command-btn" onclick="executeCommand('ai_chat')">Chat IA</button>
                        <button class="command-btn" onclick="executeCommand('help')">Ajuda</button>
                    </div>
                </div>

                <div class="card">
                    <h2>🔧 Comando Personalizado</h2>
                    <div class="input-group">
                        <label for="commandInput">Comando:</label>
                        <input type="text" id="commandInput" placeholder="Ex: research blockchain trends" value="status">
                    </div>
                    <div class="input-group">
                        <label for="argsInput">Argumentos (separados por espaço):</label>
                        <input type="text" id="argsInput" placeholder="Ex: blockchain defi nft">
                    </div>
                    <button class="execute-btn" onclick="executeCustomCommand()">▶️ Executar Comando</button>
                </div>

                <div class="card">
                    <h2>📋 Comandos Recentes</h2>
                    <div class="history-container" id="historyContainer">
    """

    # Adicionar histórico
    if data['recent_commands']:
        for cmd in reversed(data['recent_commands']):
            html += f"""
                        <div class="history-item">
                            <strong>{cmd['command']}</strong> {cmd['args']}<br>
                            <small>{cmd['timestamp']}</small>
                        </div>
            """
    else:
        html += """
                        <div class="history-item">
                            Nenhum comando executado ainda
                        </div>
        """

    html += """
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>📊 Saída do Comando</h2>
                <div class="output-container" id="outputContainer">
                    <div class="output-line info">Aguardando comando...</div>
                </div>
            </div>

            <div class="footer">
                <p>BERNAS-AGENT v1.0.0 • Painel de Controle • Atualizado em: {timestamp}</p>
                <p>Use os comandos para controlar pesquisa, postagens, receita e conversas com IA</p>
            </div>
        </div>

        <script>
            let commandHistory = [];

            function executeCommand(command) {{
                const commandInput = document.getElementById('commandInput');
                const argsInput = document.getElementById('argsInput');

                commandInput.value = command;
                argsInput.value = '';

                executeCustomCommand();
            }}

            function executeCustomCommand() {{
                const command = document.getElementById('commandInput').value.trim();
                const argsText = document.getElementById('argsInput').value.trim();

                if (!command) {{
                    addOutput('error', 'Digite um comando');
                    return;
                }}

                const args = argsText ? argsText.split(' ') : [];

                addOutput('info', `Executando: ${command} ${args.join(' ')}`);

                fetch('/api/v1/control', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        command: command,
                        args: args
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        addOutput('success', `✅ ${data.message}`);
                        if (data.data) {{
                            addOutput('info', JSON.stringify(data.data, null, 2));
                        }}
                    }} else {{
                        addOutput('error', `❌ ${data.message}`);
                    }}

                    // Atualizar histórico
                    updateHistory();
                }})
                .catch(error => {{
                    addOutput('error', `Erro: ${{error.message}}`);
                }});
            }}

            function addOutput(type, message) {{
                const outputContainer = document.getElementById('outputContainer');
                const outputLine = document.createElement('div');
                outputLine.className = `output-line ${{type}}`;
                outputLine.textContent = `[${{new Date().toLocaleTimeString()}}] ${{message}}`;
                outputContainer.appendChild(outputLine);
                outputContainer.scrollTop = outputContainer.scrollHeight;
            }}

            function updateHistory() {{
                // Em uma implementação real, buscaria do servidor
                // Por enquanto, apenas rola para baixo
                const historyContainer = document.getElementById('historyContainer');
                historyContainer.scrollTop = historyContainer.scrollHeight;
            }}

            // Comandos de teclado
            document.addEventListener('keydown', (e) => {{
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {{
                    executeCustomCommand();
                }}
            }});

            // Focar no input de comando
            document.getElementById('commandInput').focus();
        </script>
    </body>
    </html>
    """.format(timestamp=data['timestamp'])

    return html