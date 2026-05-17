"""
Dashboard MOLTBOOK para BERNAS-AGENT
Interface profissional de monitoramento
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from aiohttp import web

# Adicionar diretório pai ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Importar módulos do projeto
try:
    from economy.economy_manager import economy_manager
    from economy.router_client import router
    from token_manager.token_manager import token_manager
    from solana.solana_client import wallet_manager
    from revenue.revenue_generators import revenue_generator
    MOLTBOOK_ENABLED = True
except ImportError as e:
    print(f"[WARN] Módulos não disponíveis para MOLTBOOK: {e}")
    MOLTBOOK_ENABLED = False

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoltbookDashboard:
    """Dashboard estilo MOLTBOOK para monitoramento avançado"""

    def __init__(self):
        self.metrics_history: Dict[str, List] = {
            "revenue": [],
            "transactions": [],
            "ai_requests": [],
            "token_balance": [],
            "active_users": []
        }
        self.start_time = datetime.now()
        self.update_interval = 30  # segundos

    async def collect_metrics(self):
        """Coleta métricas de todos os sistemas"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "systems": {}
        }

        try:
            # 1. Sistema de Economia
            economy_stats = economy_manager.get_marketplace_stats()
            metrics["systems"]["economy"] = {
                "total_services": economy_stats.get("total_services", 0),
                "total_transactions": economy_stats.get("total_transactions", 0),
                "total_volume_usdc": economy_stats.get("total_volume_usdc", "0"),
                "active_wallets": economy_stats.get("active_wallets", 0)
            }

            # 2. Roteador de IA
            ai_stats = router.get_stats()
            metrics["systems"]["ai_router"] = {
                "total_requests": ai_stats.get("total_requests", 0),
                "success_rate": ai_stats.get("success_rate", 0),
                "total_cost_usdc": ai_stats.get("total_cost_usdc", 0),
                "active_providers": ai_stats.get("active_providers", 0)
            }

            # 3. Gerenciador de Tokens
            token_stats = token_manager.get_stats()
            metrics["systems"]["token_manager"] = {
                "current_balance": token_stats.get("current_balance", 0),
                "total_revenue": token_stats.get("total_revenue", 0),
                "transactions_count": token_stats.get("transactions_count", 0),
                "auto_recharge_count": token_stats.get("auto_recharge_count", 0)
            }

            # 4. Geradores de Receita
            revenue_stats = revenue_generator.get_stats()
            metrics["systems"]["revenue_generators"] = {
                "total_revenue_usdc": revenue_stats.get("total_revenue_usdc", "0"),
                "transactions_count": revenue_stats.get("transactions_count", 0),
                "generators_active": revenue_stats.get("generators_active", 0),
                "revenue_per_hour": str(revenue_stats.get("revenue_per_hour", "0"))
            }

            # 5. Solana (se disponível)
            if hasattr(wallet_manager, 'wallets'):
                solana_stats = {
                    "wallets_count": len(wallet_manager.wallets),
                    "total_balance": sum(w.balance for w in wallet_manager.wallets.values()),
                    "transactions_count": getattr(wallet_manager, 'transaction_count', 0)
                }
                metrics["systems"]["solana"] = solana_stats

            # 6. Performance
            metrics["performance"] = {
                "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
                "response_time_ms": self._calculate_response_time(),
                "system_health": self._calculate_system_health(),
                "last_update": datetime.now().isoformat()
            }

            # 7. Alertas
            metrics["alerts"] = self._check_alerts()

            # Armazenar no histórico
            self._store_in_history(metrics)

            return metrics

        except Exception as e:
            logger.error(f"Erro ao coletar métricas: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _calculate_response_time(self) -> float:
        """Calcula tempo médio de resposta"""
        # Simulação - em produção, medir tempos reais
        return 150.0  # ms

    def _calculate_system_health(self) -> str:
        """Calcula saúde do sistema"""
        # Simulação - em produção, verificar todos os sistemas
        return "healthy"

    def _check_alerts(self) -> List[Dict]:
        """Verifica alertas do sistema"""
        alerts = []

        # Verificar saldo baixo
        try:
            token_stats = token_manager.get_stats()
            balance = float(token_stats.get("current_balance", 0))
            if balance < 10.0:
                alerts.append({
                    "level": "warning",
                    "message": f"Saldo baixo: {balance:.2f} USDC",
                    "system": "token_manager",
                    "timestamp": datetime.now().isoformat()
                })
        except:
            pass

        # Verificar taxa de erro da IA
        try:
            ai_stats = router.get_stats()
            success_rate = ai_stats.get("success_rate", 100)
            if success_rate < 80:
                alerts.append({
                    "level": "error",
                    "message": f"Taxa de sucesso da IA baixa: {success_rate}%",
                    "system": "ai_router",
                    "timestamp": datetime.now().isoformat()
                })
        except:
            pass

        return alerts

    def _store_in_history(self, metrics: Dict):
        """Armazena métricas no histórico"""
        timestamp = metrics["timestamp"]

        # Revenue
        revenue = Decimal("0")
        if "systems" in metrics and "revenue_generators" in metrics["systems"]:
            rev_str = metrics["systems"]["revenue_generators"].get("total_revenue_usdc", "0")
            revenue = Decimal(rev_str)

        self.metrics_history["revenue"].append({
            "timestamp": timestamp,
            "value": float(revenue)
        })

        # Manter apenas últimas 1000 entradas
        for key in self.metrics_history:
            if len(self.metrics_history[key]) > 1000:
                self.metrics_history[key] = self.metrics_history[key][-1000:]

    def get_historical_data(self, metric: str, hours: int = 24) -> List[Dict]:
        """Retorna dados históricos de uma métrica"""
        if metric not in self.metrics_history:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_iso = cutoff_time.isoformat()

        return [
            point for point in self.metrics_history[metric]
            if point["timestamp"] >= cutoff_iso
        ]

    def get_dashboard_html(self) -> str:
        """Gera HTML do dashboard MOLTBOOK"""
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BERNAS-AGENT • MOLTBOOK Dashboard</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }

                body {
                    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                    color: #fff;
                    min-height: 100vh;
                    padding: 20px;
                }

                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                }

                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px 0;
                    border-bottom: 2px solid rgba(255, 255, 255, 0.1);
                    margin-bottom: 30px;
                }

                .logo {
                    display: flex;
                    align-items: center;
                    gap: 15px;
                }

                .logo h1 {
                    font-size: 2.5rem;
                    background: linear-gradient(90deg, #00dbde, #fc00ff);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: 800;
                }

                .status-badge {
                    background: #00c853;
                    color: white;
                    padding: 8px 20px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 0.9rem;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .status-badge::before {
                    content: "●";
                    font-size: 1.2rem;
                    animation: pulse 2s infinite;
                }

                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }

                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }

                .stat-card {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 15px;
                    padding: 25px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    transition: transform 0.3s, border-color 0.3s;
                }

                .stat-card:hover {
                    transform: translateY(-5px);
                    border-color: rgba(0, 219, 222, 0.3);
                }

                .stat-card h3 {
                    font-size: 1rem;
                    color: #aaa;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                .stat-value {
                    font-size: 2.5rem;
                    font-weight: 700;
                    background: linear-gradient(90deg, #00dbde, #fc00ff);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }

                .stat-change {
                    font-size: 0.9rem;
                    color: #4caf50;
                    margin-top: 5px;
                }

                .stat-change.negative {
                    color: #f44336;
                }

                .charts-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }

                .chart-container {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 15px;
                    padding: 25px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }

                .chart-container h3 {
                    font-size: 1.2rem;
                    margin-bottom: 20px;
                    color: #fff;
                }

                .chart-placeholder {
                    height: 300px;
                    background: rgba(255, 255, 255, 0.02);
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #666;
                    font-size: 1.1rem;
                }

                .systems-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 15px;
                    margin-bottom: 30px;
                }

                .system-card {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 10px;
                    padding: 20px;
                    border-left: 4px solid #00dbde;
                }

                .system-card h4 {
                    font-size: 1.1rem;
                    margin-bottom: 10px;
                    color: #fff;
                }

                .system-status {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 0.9rem;
                    color: #4caf50;
                }

                .system-status.error {
                    color: #f44336;
                }

                .system-status.warning {
                    color: #ff9800;
                }

                .alerts-container {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 15px;
                    padding: 25px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }

                .alerts-container h3 {
                    font-size: 1.2rem;
                    margin-bottom: 20px;
                    color: #fff;
                }

                .alert-item {
                    padding: 15px;
                    background: rgba(244, 67, 54, 0.1);
                    border-radius: 8px;
                    margin-bottom: 10px;
                    border-left: 4px solid #f44336;
                }

                .alert-item.warning {
                    background: rgba(255, 152, 0, 0.1);
                    border-left-color: #ff9800;
                }

                .alert-item.info {
                    background: rgba(33, 150, 243, 0.1);
                    border-left-color: #2196f3;
                }

                .alert-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 5px;
                }

                .alert-level {
                    font-weight: bold;
                    font-size: 0.9rem;
                }

                .alert-time {
                    font-size: 0.8rem;
                    color: #aaa;
                }

                .alert-message {
                    font-size: 0.95rem;
                    color: #fff;
                }

                .footer {
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 0.9rem;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    margin-top: 30px;
                }

                .refresh-button {
                    background: linear-gradient(90deg, #00dbde, #fc00ff);
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    border-radius: 25px;
                    font-weight: bold;
                    cursor: pointer;
                    font-size: 1rem;
                    transition: transform 0.3s, box-shadow 0.3s;
                }

                .refresh-button:hover {
                    transform: scale(1.05);
                    box-shadow: 0 5px 20px rgba(0, 219, 222, 0.3);
                }

                @media (max-width: 768px) {
                    .charts-grid {
                        grid-template-columns: 1fr;
                    }

                    .stat-card {
                        padding: 15px;
                    }

                    .stat-value {
                        font-size: 2rem;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">
                        <h1>BERNAS-AGENT</h1>
                        <div class="status-badge" id="statusBadge">
                            ONLINE • MOLTBOOK
                        </div>
                    </div>
                    <button class="refresh-button" onclick="refreshDashboard()">
                        🔄 Atualizar Dashboard
                    </button>
                </div>

                <div class="stats-grid" id="statsGrid">
                    <!-- Stats serão preenchidos via JavaScript -->
                    <div class="stat-card">
                        <h3>Receita Total</h3>
                        <div class="stat-value" id="totalRevenue">$0.00</div>
                        <div class="stat-change" id="revenueChange">+0.00% hoje</div>
                    </div>

                    <div class="stat-card">
                        <h3>Saldo USDC</h3>
                        <div class="stat-value" id="usdcBalance">0.00</div>
                        <div class="stat-change" id="balanceChange">+0.00 USDC/h</div>
                    </div>

                    <div class="stat-card">
                        <h3>Transações</h3>
                        <div class="stat-value" id="totalTransactions">0</div>
                        <div class="stat-change">+0 hoje</div>
                    </div>

                    <div class="stat-card">
                        <h3>Uptime</h3>
                        <div class="stat-value" id="uptime">0h</div>
                        <div class="stat-change" id="healthStatus">100% saúde</div>
                    </div>
                </div>

                <div class="charts-grid">
                    <div class="chart-container">
                        <h3>📈 Receita por Hora</h3>
                        <div class="chart-placeholder" id="revenueChart">
                            Gráfico de receita carregando...
                        </div>
                    </div>

                    <div class="chart-container">
                        <h3>🤖 Atividade da IA</h3>
                        <div class="chart-placeholder" id="aiActivityChart">
                            Gráfico de atividade carregando...
                        </div>
                    </div>
                </div>

                <div class="systems-grid" id="systemsGrid">
                    <!-- Sistemas serão preenchidos via JavaScript -->
                </div>

                <div class="alerts-container">
                    <h3>⚠️ Alertas do Sistema</h3>
                    <div id="alertsList">
                        <div class="alert-item info">
                            <div class="alert-header">
                                <span class="alert-level">INFO</span>
                                <span class="alert-time">Agora</span>
                            </div>
                            <div class="alert-message">
                                Dashboard MOLTBOOK inicializado. Aguardando dados...
                            </div>
                        </div>
                    </div>
                </div>

                <div class="footer">
                    <p>🤖 BERNAS-AGENT • Dashboard MOLTBOOK • Gerando receita 24/7</p>
                    <p>🌐 https://bernas-agent.onrender.com • 🕐 <span id="currentTime"></span></p>
                </div>
            </div>

            <script>
                // Atualizar hora atual
                function updateCurrentTime() {
                    const now = new Date();
                    const timeString = now.toLocaleString('pt-BR', {
                        timeZone: 'America/Sao_Paulo',
                        hour12: false
                    });
                    document.getElementById('currentTime').textContent = timeString;
                }

                // Atualizar dashboard
                async function refreshDashboard() {
                    try {
                        const response = await fetch('/api/v1/moltbook/metrics');
                        const data = await response.json();

                        if (data.error) {
                            console.error('Erro ao buscar métricas:', data.error);
                            return;
                        }

                        updateDashboard(data);
                    } catch (error) {
                        console.error('Erro ao atualizar dashboard:', error);
                    }
                }

                // Atualizar interface com dados
                function updateDashboard(metrics) {
                    // Receita Total
                    if (metrics.systems?.revenue_generators?.total_revenue_usdc) {
                        const revenue = parseFloat(metrics.systems.revenue_generators.total_revenue_usdc);
                        document.getElementById('totalRevenue').textContent = `$${revenue.toFixed(2)}`;
                    }

                    // Saldo USDC
                    if (metrics.systems?.token_manager?.current_balance) {
                        const balance = metrics.systems.token_manager.current_balance;
                        document.getElementById('usdcBalance').textContent = balance.toFixed(2);
                    }

                    // Transações
                    if (metrics.systems?.economy?.total_transactions) {
                        document.getElementById('totalTransactions').textContent =
                            metrics.systems.economy.total_transactions;
                    }

                    // Uptime
                    if (metrics.performance?.uptime_hours) {
                        const hours = Math.floor(metrics.performance.uptime_hours);
                        const minutes = Math.floor((metrics.performance.uptime_hours - hours) * 60);
                        document.getElementById('uptime').textContent = `${hours}h ${minutes}m`;
                    }

                    // Saúde do sistema
                    if (metrics.performance?.system_health) {
                        const health = metrics.performance.system_health;
                        const healthElement = document.getElementById('healthStatus');
                        healthElement.textContent = `${health === 'healthy' ? '100%' : '⚠️'} saúde`;
                        healthElement.className = `stat-change ${health === 'healthy' ? '' : 'negative'}`;
                    }

                    // Atualizar sistemas
                    updateSystemsGrid(metrics.systems || {});

                    // Atualizar alertas
                    updateAlerts(metrics.alerts || []);
                }

                // Atualizar grid de sistemas
                function updateSystemsGrid(systems) {
                    const grid = document.getElementById('systemsGrid');
                    grid.innerHTML = '';

                    const systemCards = [
                        {
                            name: 'Economia',
                            data: systems.economy,
                            color: '#4CAF50'
                        },
                        {
                            name: 'IA Router',
                            data: systems.ai_router,
                            color: '#2196F3'
                        },
                        {
                            name: 'Token Manager',
                            data: systems.token_manager,
                            color: '#FF9800'
                        },
                        {
                            name: 'Revenue Generators',
                            data: systems.revenue_generators,
                            color: '#9C27B0'
                        },
                        {
                            name: 'Solana',
                            data: systems.solana,
                            color: '#00BCD4'
                        },
                        {
                            name: 'Performance',
                            data: systems.performance,
                            color: '#607D8B'
                        }
                    ];

                    systemCards.forEach(system => {
                        if (!system.data) return;

                        const card = document.createElement('div');
                        card.className = 'system-card';
                        card.style.borderLeftColor = system.color;

                        let status = '✅ Online';
                        let statusClass = 'system-status';

                        // Verificar status baseado em métricas
                        if (system.name === 'Token Manager' && system.data.current_balance < 10) {
                            status = '⚠️ Saldo baixo';
                            statusClass += ' warning';
                        } else if (system.name === 'IA Router' && system.data.success_rate < 80) {
                            status = '❌ Erros altos';
                            statusClass += ' error';
                        }

                        let content = `<h4>${system.name}</h4>`;
                        content += `<div class="${statusClass}">${status}</div>`;

                        // Adicionar métricas específicas
                        if (system.name === 'Economy') {
                            content += `<div style="margin-top: 10px; font-size: 0.9rem; color: #ccc;">
                                💰 ${system.data.total_volume_usdc || 0} USDC<br>
                                📊 ${system.data.total_transactions || 0} transações
                            </div>`;
                        } else if (system.name === 'IA Router') {
                            content += `<div style="margin-top: 10px; font-size: 0.9rem; color: #ccc;">
                                🤖 ${system.data.total_requests || 0} requests<br>
                                ✅ ${system.data.success_rate || 0}% sucesso
                            </div>`;
                        }

                        card.innerHTML = content;
                        grid.appendChild(card);
                    });
                }

                // Atualizar alertas
                function updateAlerts(alerts) {
                    const alertsList = document.getElementById('alertsList');

                    if (alerts.length === 0) {
                        alertsList.innerHTML = `
                            <div class="alert-item info">
                                <div class="alert-header">
                                    <span class="alert-level">INFO</span>
                                    <span class="alert-time">Agora</span>
                                </div>
                                <div class="alert-message">
                                    ✅ Todos os sistemas operando normalmente
                                </div>
                            </div>
                        `;
                        return;
                    }

                    alertsList.innerHTML = '';
                    alerts.forEach(alert => {
                        const alertElement = document.createElement('div');
                        alertElement.className = `alert-item ${alert.level}`;

                        const time = new Date(alert.timestamp).toLocaleTimeString('pt-BR');

                        alertElement.innerHTML = `
                            <div class="alert-header">
                                <span class="alert-level">${alert.level.toUpperCase()}</span>
                                <span class="alert-time">${time}</span>
                            </div>
                            <div class="alert-message">
                                ${alert.message}
                            </div>
                        `;

                        alertsList.appendChild(alertElement);
                    });
                }

                // Inicializar
                document.addEventListener('DOMContentLoaded', () => {
                    updateCurrentTime();
                    setInterval(updateCurrentTime, 1000);

                    // Atualizar a cada 30 segundos
                    refreshDashboard();
                    setInterval(refreshDashboard, 30000);
                });
            </script>
        </body>
        </html>
        """

# Instância global
moltbook_dashboard = MoltbookDashboard()

async def handle_moltbook_dashboard(request: web.Request) -> web.Response:
    """Handler para o dashboard MOLTBOOK"""
    html = moltbook_dashboard.get_dashboard_html()
    return web.Response(text=html, content_type="text/html")

async def handle_moltbook_metrics(request: web.Request) -> web.Response:
    """API para métricas do MOLTBOOK"""
    metrics = await moltbook_dashboard.collect_metrics()
    return web.json_response(metrics)

async def start_moltbook_monitoring():
    """Inicia monitoramento MOLTBOOK"""
    if not MOLTBOOK_ENABLED:
        logger.warning("Módulos necessários não disponíveis. MOLTBOOK desativado.")
        return None

    logger.info("📊 MOLTBOOK Dashboard inicializado")

    # Coletar métricas periodicamente
    async def collect_periodically():
        while True:
            try:
                await moltbook_dashboard.collect_metrics()
            except Exception as e:
                logger.error(f"Erro ao coletar métricas MOLTBOOK: {e}")

            await asyncio.sleep(moltbook_dashboard.update_interval)

    # Iniciar em background
    task = asyncio.create_task(collect_periodically())
    return task

def main():
    """Função principal para teste"""
    print("🧪 Testando MOLTBOOK Dashboard...")

    # Testar coleta de métricas
    import asyncio

    async def test():
        metrics = await moltbook_dashboard.collect_metrics()
        print(f"Métricas coletadas: {json.dumps(metrics, indent=2, default=str)}")

        # Testar histórico
        historical = moltbook_dashboard.get_historical_data("revenue", 1)
        print(f"\nDados históricos (1h): {len(historical)} pontos")

        # Testar HTML
        html = moltbook_dashboard.get_dashboard_html()
        print(f"\nHTML gerado: {len(html)} caracteres")

        # Salvar para visualização
        with open("moltbook_test.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ HTML salvo em moltbook_test.html")

    asyncio.run(test())

if __name__ == "__main__":
    main()