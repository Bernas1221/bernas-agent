"""
Dashboard de Monitoramento BERNAS-AGENT
Sistema de monitoramento estilo CLAWSEC/Moltbook
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
import jinja2
import aiohttp_jinja2

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringDashboard:
    """Dashboard de monitoramento em tempo real"""

    def __init__(self):
        self.metrics = {
            "uptime": 0,
            "total_requests": 0,
            "total_transactions": 0,
            "total_messages": 0,
            "total_errors": 0,
            "ai_providers": {},
            "economy_stats": {},
            "whatsapp_stats": {},
            "system_resources": {},
            "alerts": []
        }
        self.history = {
            "requests": [],
            "transactions": [],
            "errors": [],
            "costs": []
        }
        self.alerts = []
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
                        self.metrics["whatsapp_stats"] = bot_stats.get("whatsapp", {})

                # Estatísticas da economia
                async with session.get('http://localhost:4020/api/v1/services') as resp:
                    if resp.status == 200:
                        services_data = await resp.json()
                        self.metrics["active_services"] = len(services_data.get("services", []))

                # Adicionar ao histórico
                now = datetime.now()
                self.history["requests"].append({
                    "timestamp": now.isoformat(),
                    "count": self.metrics["total_requests"]
                })
                self.history["transactions"].append({
                    "timestamp": now.isoformat(),
                    "count": self.metrics["total_transactions"]
                })
                self.history["errors"].append({
                    "timestamp": now.isoformat(),
                    "count": self.metrics["total_errors"]
                })

                # Manter apenas últimas 100 entradas
                for key in self.history:
                    if len(self.history[key]) > 100:
                        self.history[key] = self.history[key][-100:]

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

        # Verificar serviços da economia
        if self.metrics.get("active_services", 0) == 0:
            alerts.append({
                "level": "error",
                "message": "Nenhum serviço ativo no marketplace",
                "timestamp": datetime.now().isoformat()
            })

        # Verificar uptime
        if self.metrics["uptime"] < 60:  # Menos de 1 minuto
            alerts.append({
                "level": "info",
                "message": "Bot iniciado recentemente",
                "timestamp": datetime.now().isoformat()
            })

        self.alerts = alerts[-20:]  # Manter apenas últimos 20 alertas

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados para o dashboard"""
        return {
            "metrics": self.metrics,
            "history": self.history,
            "alerts": self.alerts,
            "system_info": {
                "start_time": self.start_time.isoformat(),
                "current_time": datetime.now().isoformat(),
                "uptime_hours": self.metrics["uptime"] / 3600,
                "request_rate": self._calculate_request_rate(),
                "error_rate": self._calculate_error_rate()
            },
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_request_rate(self) -> float:
        """Calcula taxa de requisições por minuto"""
        if len(self.history["requests"]) < 2:
            return 0.0

        recent = self.history["requests"][-10:]  # Últimas 10 entradas
        if len(recent) < 2:
            return 0.0

        first = recent[0]
        last = recent[-1]

        try:
            first_time = datetime.fromisoformat(first["timestamp"])
            last_time = datetime.fromisoformat(last["timestamp"])
            time_diff = (last_time - first_time).total_seconds() / 60  # em minutos

            if time_diff == 0:
                return 0.0

            request_diff = last["count"] - first["count"]
            return request_diff / time_diff
        except:
            return 0.0

    def _calculate_error_rate(self) -> float:
        """Calcula taxa de erros por minuto"""
        if len(self.history["errors"]) < 2:
            return 0.0

        recent = self.history["errors"][-10:]  # Últimas 10 entradas
        if len(recent) < 2:
            return 0.0

        first = recent[0]
        last = recent[-1]

        try:
            first_time = datetime.fromisoformat(first["timestamp"])
            last_time = datetime.fromisoformat(last["timestamp"])
            time_diff = (last_time - first_time).total_seconds() / 60  # em minutos

            if time_diff == 0:
                return 0.0

            error_diff = last["count"] - first["count"]
            return error_diff / time_diff
        except:
            return 0.0


# Instância global do dashboard
dashboard = MonitoringDashboard()


async def start_monitoring_server(host: str = "0.0.0.0", port: int = 8081):
    """Inicia servidor web do dashboard"""

    # Configurar templates Jinja2
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)

    # Criar template padrão se não existir
    template_file = os.path.join(template_dir, 'dashboard.html')
    if not os.path.exists(template_file):
        _create_default_template(template_file)

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(template_dir))

    # Rotas
    app.router.add_get('/', handle_dashboard)
    app.router.add_get('/api/metrics', handle_metrics_api)
    app.router.add_get('/api/alerts', handle_alerts_api)
    app.router.add_get('/api/history', handle_history_api)
    app.router.add_static('/static', os.path.join(template_dir, 'static'))

    # Tarefa de atualização de métricas
    async def update_metrics_task():
        while True:
            await dashboard.update_metrics()
            await asyncio.sleep(30)  # Atualizar a cada 30 segundos

    app['metrics_task'] = asyncio.create_task(update_metrics_task())

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)

    await site.start()
    logger.info(f"Dashboard de monitoramento iniciado em http://{host}:{port}")

    return app


@aiohttp_jinja2.template('dashboard.html')
async def handle_dashboard(request: web.Request) -> Dict[str, Any]:
    """Página principal do dashboard"""
    return dashboard.get_dashboard_data()


async def handle_metrics_api(request: web.Request) -> web.Response:
    """API para métricas em JSON"""
    return web.json_response(dashboard.get_dashboard_data())


async def handle_alerts_api(request: web.Request) -> web.Response:
    """API para alertas"""
    return web.json_response({
        "alerts": dashboard.alerts,
        "count": len(dashboard.alerts),
        "timestamp": datetime.now().isoformat()
    })


async def handle_history_api(request: web.Request) -> web.Response:
    """API para histórico"""
    return web.json_response({
        "history": dashboard.history,
        "timestamp": datetime.now().isoformat()
    })


def _create_default_template(template_path: str):
    """Cria template HTML padrão para o dashboard"""
    html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BERNAS-AGENT Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            color: #2d3748;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .header .subtitle {
            color: #718096;
            font-size: 1.1rem;
        }

        .status-badge {
            background: #48bb78;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.2rem;
        }

        .status-badge.error {
            background: #f56565;
        }

        .status-badge.warning {
            background: #ed8936;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .card h2 {
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 1.5rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding: 10px;
            background: #f7fafc;
            border-radius: 10px;
        }

        .metric-label {
            color: #4a5568;
            font-weight: 500;
        }

        .metric-value {
            color: #2d3748;
            font-weight: bold;
            font-size: 1.2rem;
        }

        .metric-value.good {
            color: #48bb78;
        }

        .metric-value.warning {
            color: #ed8936;
        }

        .metric-value.error {
            color: #f56565;
        }

        .alerts-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }

        .alert {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            display: flex;
            align-items: center;
        }

        .alert.info {
            background: #ebf8ff;
            border-left: 4px solid #4299e1;
        }

        .alert.warning {
            background: #fefcbf;
            border-left: 4px solid #ed8936;
        }

        .alert.error {
            background: #fed7d7;
            border-left: 4px solid #f56565;
        }

        .alert-icon {
            margin-right: 15px;
            font-size: 1.5rem;
        }

        .alert-content {
            flex: 1;
        }

        .alert-time {
            color: #718096;
            font-size: 0.9rem;
        }

        .providers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }

        .provider-card {
            background: #f7fafc;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }

        .provider-card.enabled {
            border: 2px solid #48bb78;
        }

        .provider-card.disabled {
            border: 2px solid #cbd5e0;
            opacity: 0.7;
        }

        .provider-name {
            font-weight: bold;
            margin-bottom: 5px;
        }

        .provider-status {
            font-size: 0.9rem;
            padding: 3px 10px;
            border-radius: 15px;
            display: inline-block;
        }

        .provider-status.enabled {
            background: #c6f6d5;
            color: #22543d;
        }

        .provider-status.disabled {
            background: #fed7d7;
            color: #742a2a;
        }

        .refresh-btn {
            background: #4299e1;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s ease;
            margin-top: 20px;
        }

        .refresh-btn:hover {
            background: #3182ce;
        }

        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 30px;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                text-align: center;
                gap: 20px;
            }

            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🤖 BERNAS-AGENT Dashboard</h1>
                <p class="subtitle">Monitoramento em tempo real do bot de economia autônoma</p>
                <p class="subtitle">Iniciado em: {{ system_info.start_time }}</p>
            </div>
            <div class="status-badge" id="statusBadge">
                🟢 OPERACIONAL
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <h2>📊 Estatísticas Gerais</h2>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value" id="uptime">{{ "%.1f"|format(system_info.uptime_hours) }} horas</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Requisições Totais</span>
                    <span class="metric-value good" id="totalRequests">{{ metrics.total_requests }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Transações</span>
                    <span class="metric-value good" id="totalTransactions">{{ metrics.total_transactions }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Taxa de Requisições</span>
                    <span class="metric-value" id="requestRate">{{ "%.1f"|format(system_info.request_rate) }}/min</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Erros</span>
                    <span class="metric-value {% if metrics.total_errors > 10 %}error{% elif metrics.total_errors > 5 %}warning{% endif %}"
                          id="totalErrors">{{ metrics.total_errors }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Taxa de Erros</span>
                    <span class="metric-value {% if system_info.error_rate > 0.5 %}error{% elif system_info.error_rate > 0.1 %}warning{% endif %}"
                          id="errorRate">{{ "%.2f"|format(system_info.error_rate) }}/min</span>
                </div>
            </div>

            <div class="card">
                <h2>💰 Economia</h2>
                <div class="metric">
                    <span class="metric-label">Serviços Ativos</span>
                    <span class="metric-value good" id="activeServices">{{ metrics.active_services|default(0) }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Carteiras Ativas</span>
                    <span class="metric-value" id="activeWallets">{{ metrics.economy_stats.active_wallets|default(0) }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Volume Total (USDC)</span>
                    <span class="metric-value good" id="totalVolume">{{ metrics.economy_stats.total_volume_usdc|default('0') }}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Transações Completadas</span>
                    <span class="metric-value" id="completedTransactions">{{ metrics.economy_stats.completed_transactions|default(0) }}</span>
                </div>
            </div>

            <div class="card">
                <h2>🤖 Provedores de IA</h2>
                <div class="providers-grid" id="providersGrid">
                    {% for provider_name, provider_data in metrics.ai_providers.items() %}
                    <div class="provider-card {% if provider_data.enabled %}enabled{% else %}disabled{% endif %}">
                        <div class="provider-name">{{ provider_name|upper }}</div>
                        <div class="provider-status {% if provider_data.enabled %}enabled{% else %}disabled{% endif %}">
                            {% if provider_data.enabled %}✅ ATIVO{% else %}❌ INATIVO{% endif %}
                        </div>
                        <div style="margin-top: 5px; font-size: 0.8rem;">
                            Tokens: {{ provider_data.tokens_used|default(0) }}<br>
                            Custo: ${{ "%.4f"|format(provider_data.cost_usdc|default(0)) }}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <div class="alerts-container">
            <h2>🚨 Alertas ({{ alerts|length }})</h2>
            <div id="alertsList">
                {% for alert in alerts %}
                <div class="alert {{ alert.level }}">
                    <div class="alert-icon">
                        {% if alert.level == 'error' %}⚠️{% elif alert.level == 'warning' %}🔶{% else %}ℹ️{% endif %}
                    </div>
                    <div class="alert-content">
                        <strong>{{ alert.message }}</strong>
                        <div class="alert-time">{{ alert.timestamp }}</div>
                    </div>
                </div>
                {% else %}
                <div class="alert info">
                    <div class="alert-icon">✅</div>
                    <div class="alert-content">
                        <strong>Tudo funcionando perfeitamente!</strong>
                        <div class="alert-time">Nenhum alerta ativo</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <button class="refresh-btn" onclick="refreshDashboard()">🔄 Atualizar Dashboard</button>

        <div class="footer">
            <p>BERNAS-AGENT v1.0.0 • Dashboard atualizado em: <span id="currentTime">{{ timestamp }}</span></p>
            <p>Monitoramento estilo CLAWSEC/Moltbook • Atualização automática a cada 30 segundos</p>
        </div>
    </div>

    <script>
        function refreshDashboard() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {
                    // Atualizar métricas
                    document.getElementById('uptime').textContent = data.system_info.uptime_hours.toFixed(1) + ' horas';
                    document.getElementById('totalRequests').textContent = data.metrics.total_requests;
                    document.getElementById('totalTransactions').textContent = data.metrics.total_transactions;
                    document.getElementById('requestRate').textContent = data.system_info.request_rate.toFixed(1) + '/min';
                    document.getElementById('totalErrors').textContent = data.metrics.total_errors;
                    document.getElementById('errorRate').textContent = data.system_info.error_rate.toFixed(2) + '/min';

                    document.getElementById('activeServices').textContent = data.metrics.active_services || 0;
                    document.getElementById('activeWallets').textContent = data.metrics.economy_stats.active_wallets || 0;
                    document.getElementById('totalVolume').textContent = data.metrics.economy_stats.total_volume_usdc || '0';
                    document.getElementById('completedTransactions').textContent = data.metrics.economy_stats.completed_transactions || 0;

                    // Atualizar status badge
                    const statusBadge = document.getElementById('statusBadge');
                    if (data.metrics.total_errors > 20 || data.system_info.error_rate > 1) {
                        statusBadge.textContent = '🔴 CRÍTICO';
                        statusBadge.className = 'status-badge error';
                    } else if (data.metrics.total_errors > 5 || data.system_info.error_rate > 0.5) {
                        statusBadge.textContent = '🟡 ALERTA';
                        statusBadge.className = 'status-badge warning';
                    } else {
                        statusBadge.textContent = '🟢 OPERACIONAL';
                        statusBadge.className = 'status-badge';
                    }

                    // Atualizar provedores
                    const providersGrid = document.getElementById('providersGrid');
                    providersGrid.innerHTML = '';

                    Object.entries(data.metrics.ai_providers || {}).forEach(([name, provider]) => {
                        const card = document.createElement('div');
                        card.className = `provider-card ${provider.enabled ? 'enabled' : 'disabled'}`;

                        card.innerHTML = `
                            <div class="provider-name">${name.toUpperCase()}</div>
                            <div class="provider-status ${provider.enabled ? 'enabled' : 'disabled'}">
                                ${provider.enabled ? '✅ ATIVO' : '❌ INATIVO'}
                            </div>
                            <div style="margin-top: 5px; font-size: 0.8rem;">
                                Tokens: ${provider.tokens_used || 0}<br>
                                Custo: $${(provider.cost_usdc || 0).toFixed(4)}
                            </div>
                        `;

                        providersGrid.appendChild(card);
                    });

                    // Atualizar alertas
                    const alertsList = document.getElementById('alertsList');
                    alertsList.innerHTML = '';

                    if (data.alerts.length === 0) {
                        alertsList.innerHTML = `
                            <div class="alert info">
                                <div class="alert-icon">✅</div>
                                <div class="alert-content">
                                    <strong>Tudo funcionando perfeitamente!</strong>
                                    <div class="alert-time">Nenhum alerta ativo</div>
                                </div>
                            </div>
                        `;
                    } else {
                        data.alerts.forEach(alert => {
                            const alertDiv = document.createElement('div');
                            alertDiv.className = `alert ${alert.level}`;

                            let icon = 'ℹ️';
                            if (alert.level === 'error') icon = '⚠️';
                            if (alert.level === 'warning') icon = '🔶';

                            alertDiv.innerHTML = `
                                <div class="alert-icon">${icon}</div>
                                <div class="alert-content">
                                    <strong>${alert.message}</strong>
                                    <div class="alert-time">${alert.timestamp}</div>
                                </div>
                            `;

                            alertsList.appendChild(alertDiv);
                        });
                    }

                    // Atualizar timestamp
                    document.getElementById('currentTime').textContent = data.timestamp;

                    // Feedback visual
                    const btn = event.target;
                    btn.textContent = '✅ Atualizado!';
                    setTimeout(() => {
                        btn.textContent = '🔄 Atualizar Dashboard';
                    }, 2000);
                })
                .catch(error => {
                    console.error('Erro ao atualizar dashboard:', error);
                    alert('Erro ao atualizar dashboard. Verifique o console.');
                });
        }

        // Atualizar automaticamente a cada 30 segundos
        setInterval(refreshDashboard, 30000);

        // Atualizar timestamp a cada segundo
        function updateCurrentTime() {
            const now = new Date();
            document.getElementById('currentTime').textContent = now.toISOString();
        }
        setInterval(updateCurrentTime, 1000);
    </script>
</body>
</html>
    """

    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"Template criado em {template_path}")