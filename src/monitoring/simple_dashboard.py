"""
Dashboard Simples de Monitoramento BERNAS-AGENT
Versão simplificada que roda na mesma porta do bot
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


class SimpleDashboard:
    """Dashboard simples de monitoramento"""

    def __init__(self):
        self.metrics = {
            "uptime": 0,
            "total_requests": 0,
            "total_transactions": 0,
            "total_messages": 0,
            "total_errors": 0,
            "ai_providers": {},
            "economy_stats": {},
            "token_stats": {},
            "alerts": []
        }
        self.start_time = datetime.now()

    async def update_metrics(self):
        """Atualiza métricas do sistema"""
        try:
            # Coletar métricas da API do bot
            async with aiohttp.ClientSession() as session:
                # Status do bot
                async with session.get('http://localhost:8080/api/v1/stats') as resp:
                    if resp.status == 200:
                        bot_stats = await resp.json()
                        self.metrics.update({
                            "uptime": bot_stats.get("bot", {}).get("uptime_seconds", 0),
                            "total_requests": bot_stats.get("bot", {}).get("total_requests", 0),
                            "total_transactions": bot_stats.get("bot", {}).get("total_transactions", 0),
                            "total_messages": bot_stats.get("bot", {}).get("total_messages", 0),
                            "total_errors": bot_stats.get("bot", {}).get("total_errors", 0)
                        })
                        self.metrics["ai_providers"] = bot_stats.get("ai_router", {}).get("providers", {})
                        self.metrics["economy_stats"] = bot_stats.get("economy", {})
                        self.metrics["token_stats"] = bot_stats.get("token_manager", {})

                # Verificar alertas
                await self._check_alerts()

        except Exception as e:
            logger.error(f"Erro ao atualizar métricas: {e}")

    async def _check_alerts(self):
        """Verifica condições para alertas"""
        alerts = []

        # Verificar provedores de IA desabilitados
        for provider, stats in self.metrics.get("ai_providers", {}).items():
            if not stats.get("enabled", False):
                alerts.append({
                    "level": "warning",
                    "message": f"Provedor de IA {provider} desabilitado",
                    "timestamp": datetime.now().isoformat()
                })

        # Verificar erros recentes
        if self.metrics["total_errors"] > 10:
            alerts.append({
                "level": "error",
                "message": f"Alto número de erros: {self.metrics['total_errors']}",
                "timestamp": datetime.now().isoformat()
            })

        # Verificar tokens baixos
        token_stats = self.metrics.get("token_stats", {})
        providers = token_stats.get("providers", {})
        for provider_name, provider_data in providers.items():
            percentage = provider_data.get("percentage", 100)
            if percentage < 20:  # Menos de 20% de tokens
                alerts.append({
                    "level": "warning",
                    "message": f"Tokens baixos em {provider_name}: {percentage:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })

        self.metrics["alerts"] = alerts[-10:]  # Manter apenas últimos 10 alertas

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados para o dashboard"""
        return {
            "metrics": self.metrics,
            "system_info": {
                "start_time": self.start_time.isoformat(),
                "current_time": datetime.now().isoformat(),
                "uptime_hours": self.metrics["uptime"] / 3600,
            },
            "timestamp": datetime.now().isoformat()
        }

    def generate_html_dashboard(self) -> str:
        """Gera HTML do dashboard"""
        data = self.get_dashboard_data()

        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BERNAS-AGENT Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                    min-height: 100vh;
                    padding: 20px;
                    margin: 0;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #e2e8f0;
                    padding-bottom: 20px;
                }}
                .header h1 {{
                    color: #2d3748;
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                }}
                .header .subtitle {{
                    color: #718096;
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
                .dashboard-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .card {{
                    background: #f7fafc;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
                }}
                .card h2 {{
                    color: #2d3748;
                    margin-bottom: 15px;
                    font-size: 1.3rem;
                    border-bottom: 1px solid #e2e8f0;
                    padding-bottom: 10px;
                }}
                .metric {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                    padding: 8px;
                    background: white;
                    border-radius: 5px;
                }}
                .metric-label {{
                    color: #4a5568;
                    font-weight: 500;
                }}
                .metric-value {{
                    color: #2d3748;
                    font-weight: bold;
                }}
                .metric-value.good {{ color: #48bb78; }}
                .metric-value.warning {{ color: #ed8936; }}
                .metric-value.error {{ color: #f56565; }}
                .alerts-container {{
                    background: #fed7d7;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 20px;
                }}
                .alert {{
                    padding: 10px;
                    margin-bottom: 10px;
                    border-radius: 5px;
                    background: white;
                }}
                .alert.error {{ border-left: 4px solid #f56565; }}
                .alert.warning {{ border-left: 4px solid #ed8936; }}
                .alert.info {{ border-left: 4px solid #4299e1; }}
                .providers-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                    gap: 10px;
                }}
                .provider-card {{
                    background: white;
                    border-radius: 5px;
                    padding: 10px;
                    text-align: center;
                    border: 2px solid #cbd5e0;
                }}
                .provider-card.enabled {{ border-color: #48bb78; }}
                .provider-card.disabled {{ border-color: #fed7d7; opacity: 0.7; }}
                .refresh-btn {{
                    background: #4299e1;
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    border-radius: 25px;
                    font-size: 1rem;
                    cursor: pointer;
                    margin-top: 20px;
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                }}
                .refresh-btn:hover {{ background: #3182ce; }}
                .footer {{
                    text-align: center;
                    color: #718096;
                    margin-top: 30px;
                    font-size: 0.9rem;
                    border-top: 1px solid #e2e8f0;
                    padding-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 BERNAS-AGENT Dashboard</h1>
                    <p class="subtitle">Monitoramento em tempo real do bot de economia autônoma</p>
                    <p class="subtitle">Iniciado em: {data['system_info']['start_time']}</p>
                    <div class="status-badge">🟢 OPERACIONAL</div>
                </div>

                <div class="dashboard-grid">
                    <div class="card">
                        <h2>📊 Estatísticas Gerais</h2>
                        <div class="metric">
                            <span class="metric-label">Uptime</span>
                            <span class="metric-value">{data['system_info']['uptime_hours']:.1f} horas</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Requisições Totais</span>
                            <span class="metric-value good">{data['metrics']['total_requests']}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Transações</span>
                            <span class="metric-value good">{data['metrics']['total_transactions']}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Erros</span>
                            <span class="metric-value {'error' if data['metrics']['total_errors'] > 10 else 'warning' if data['metrics']['total_errors'] > 5 else ''}">
                                {data['metrics']['total_errors']}
                            </span>
                        </div>
                    </div>

                    <div class="card">
                        <h2>💰 Economia</h2>
                        <div class="metric">
                            <span class="metric-label">Carteiras Ativas</span>
                            <span class="metric-value">{data['metrics']['economy_stats'].get('active_wallets', 0)}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Volume Total</span>
                            <span class="metric-value good">{data['metrics']['economy_stats'].get('total_volume_usdc', '0')} USDC</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Transações Completadas</span>
                            <span class="metric-value">{data['metrics']['economy_stats'].get('completed_transactions', 0)}</span>
                        </div>
                    </div>

                    <div class="card">
                        <h2>🤖 Provedores de IA</h2>
                        <div class="providers-grid">
        """

        # Adicionar provedores
        for provider_name, provider_data in data['metrics']['ai_providers'].items():
            enabled = provider_data.get('enabled', False)
            html += f"""
                            <div class="provider-card {'enabled' if enabled else 'disabled'}">
                                <div style="font-weight: bold; margin-bottom: 5px;">{provider_name.upper()}</div>
                                <div style="font-size: 0.9rem; color: {'#48bb78' if enabled else '#f56565'};">
                                    {'✅ ATIVO' if enabled else '❌ INATIVO'}
                                </div>
                            </div>
            """

        html += """
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>🚨 Alertas ({alerts_count})</h2>
        """.format(alerts_count=len(data['metrics']['alerts']))

        # Adicionar alertas
        if data['metrics']['alerts']:
            for alert in data['metrics']['alerts']:
                html += f"""
                    <div class="alert {alert['level']}">
                        <strong>{alert['message']}</strong><br>
                        <small>{alert['timestamp']}</small>
                    </div>
                """
        else:
            html += """
                    <div class="alert info">
                        <strong>✅ Tudo funcionando perfeitamente!</strong><br>
                        <small>Nenhum alerta ativo</small>
                    </div>
            """

        html += """
                </div>

                <button class="refresh-btn" onclick="location.reload()">🔄 Atualizar Dashboard</button>

                <div class="footer">
                    <p>BERNAS-AGENT v1.0.0 • Dashboard atualizado em: {timestamp}</p>
                    <p>Monitoramento estilo CLAWSEC/Moltbook • Atualize a página para ver dados atualizados</p>
                </div>
            </div>

            <script>
                // Atualizar automaticamente a cada 30 segundos
                setTimeout(() => {{
                    location.reload();
                }}, 30000);
            </script>
        </body>
        </html>
        """.format(timestamp=data['timestamp'])

        return html


# Instância global do dashboard
dashboard = SimpleDashboard()


async def update_dashboard_metrics():
    """Atualiza métricas do dashboard periodicamente"""
    while True:
        try:
            await dashboard.update_metrics()
            await asyncio.sleep(30)  # Atualizar a cada 30 segundos
        except Exception as e:
            logger.error(f"Erro ao atualizar dashboard: {e}")
            await asyncio.sleep(10)


async def handle_dashboard(request: web.Request) -> web.Response:
    """Endpoint do dashboard"""
    await dashboard.update_metrics()
    html_content = dashboard.generate_html_dashboard()
    return web.Response(text=html_content, content_type='text/html')