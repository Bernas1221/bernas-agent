"""
Gerenciador Automático de Tokens BERNAS-AGENT
Sistema para garantir que o bot nunca fique sem tokens
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import aiohttp
from aiohttp import web
import random

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TokenManager:
    """Gerenciador inteligente de tokens para múltiplos provedores"""

    def __init__(self):
        self.providers = {
            "gemini": {
                "min_tokens": 10000,
                "max_tokens": 100000,
                "current_tokens": 0,
                "cost_per_token": 0.00000025,
                "recharge_threshold": 0.1,  # Recarregar quando chegar a 10%
                "recharge_amount": 50000,
                "last_recharge": None,
                "daily_limit": 1000000,
                "used_today": 0
            },
            "openclaude": {
                "min_tokens": 5000,
                "max_tokens": 50000,
                "current_tokens": 0,
                "cost_per_token": 0.000003,
                "recharge_threshold": 0.2,
                "recharge_amount": 25000,
                "last_recharge": None,
                "daily_limit": 500000,
                "used_today": 0
            },
            "kiro": {
                "min_tokens": 10000,
                "max_tokens": 100000,
                "current_tokens": 0,
                "cost_per_token": 0.000002,
                "recharge_threshold": 0.15,
                "recharge_amount": 50000,
                "last_recharge": None,
                "daily_limit": 1000000,
                "used_today": 0
            },
            "openrouter": {
                "min_tokens": 20000,
                "max_tokens": 200000,
                "current_tokens": 0,
                "cost_per_token": 0.000001,
                "recharge_threshold": 0.1,
                "recharge_amount": 100000,
                "last_recharge": None,
                "daily_limit": 2000000,
                "used_today": 0
            },
            "nvidia": {
                "min_tokens": 15000,
                "max_tokens": 150000,
                "current_tokens": 0,
                "cost_per_token": 0.0000007,
                "recharge_threshold": 0.15,
                "recharge_amount": 75000,
                "last_recharge": None,
                "daily_limit": 1500000,
                "used_today": 0
            },
            "9router": {
                "min_tokens": 50000,
                "max_tokens": 500000,
                "current_tokens": 0,
                "cost_per_token": 0.0000005,
                "recharge_threshold": 0.05,  # Recarregar mais cedo (local)
                "recharge_amount": 250000,
                "last_recharge": None,
                "daily_limit": 5000000,
                "used_today": 0
            }
        }

        self.balance_usdc = Decimal('1000')  # Saldo inicial em USDC
        self.recharge_history = []
        self.usage_history = []
        self.start_time = datetime.now()
        self.running = False

    async def initialize(self):
        """Inicializa o gerenciador de tokens"""
        logger.info("🚀 Inicializando Gerenciador de Tokens...")

        # Carregar estado salvo
        await self._load_state()

        # Inicializar tokens com valores padrão
        for provider in self.providers:
            if self.providers[provider]["current_tokens"] == 0:
                self.providers[provider]["current_tokens"] = self.providers[provider]["max_tokens"] // 2

        self.running = True

        # Iniciar tarefas de monitoramento
        asyncio.create_task(self._monitor_tokens_loop())
        asyncio.create_task(self._auto_recharge_loop())
        asyncio.create_task(self._generate_revenue_loop())

        logger.info("✅ Gerenciador de Tokens inicializado")
        logger.info(f"💰 Saldo inicial: {self.balance_usdc} USDC")

    async def _monitor_tokens_loop(self):
        """Monitora níveis de tokens periodicamente"""
        while self.running:
            try:
                await self._check_token_levels()
                await self._update_usage_stats()
                await asyncio.sleep(60)  # Verificar a cada minuto
            except Exception as e:
                logger.error(f"Erro no monitoramento de tokens: {e}")
                await asyncio.sleep(30)

    async def _auto_recharge_loop(self):
        """Recarrega tokens automaticamente quando necessário"""
        while self.running:
            try:
                await self._recharge_low_providers()
                await asyncio.sleep(300)  # Verificar a cada 5 minutos
            except Exception as e:
                logger.error(f"Erro no auto-recharge: {e}")
                await asyncio.sleep(60)

    async def _generate_revenue_loop(self):
        """Gera receita automaticamente através de serviços"""
        while self.running:
            try:
                await self._execute_revenue_generation()
                await asyncio.sleep(3600)  # Executar a cada hora
            except Exception as e:
                logger.error(f"Erro na geração de receita: {e}")
                await asyncio.sleep(300)

    async def _check_token_levels(self):
        """Verifica níveis de tokens de todos os provedores"""
        alerts = []

        for provider_name, provider_data in self.providers.items():
            current = provider_data["current_tokens"]
            max_tokens = provider_data["max_tokens"]
            threshold = provider_data["recharge_threshold"]
            min_level = max_tokens * threshold

            if current < min_level:
                alerts.append({
                    "provider": provider_name,
                    "current": current,
                    "min_level": int(min_level),
                    "percentage": (current / max_tokens) * 100
                })

        if alerts:
            logger.warning(f"Provedores com tokens baixos: {len(alerts)}")
            for alert in alerts:
                logger.warning(f"  {alert['provider']}: {alert['current']} tokens ({alert['percentage']:.1f}%)")

        return alerts

    async def _recharge_low_providers(self):
        """Recarrega provedores com tokens baixos"""
        recharged = []

        for provider_name, provider_data in self.providers.items():
            current = provider_data["current_tokens"]
            max_tokens = provider_data["max_tokens"]
            threshold = provider_data["recharge_threshold"]
            recharge_amount = provider_data["recharge_amount"]
            cost_per_token = provider_data["cost_per_token"]

            min_level = max_tokens * threshold

            if current < min_level:
                # Calcular custo da recarga
                recharge_cost = Decimal(str(recharge_amount * cost_per_token))

                # Verificar se há saldo suficiente
                if self.balance_usdc >= recharge_cost:
                    # Executar recarga
                    provider_data["current_tokens"] += recharge_amount
                    if provider_data["current_tokens"] > max_tokens:
                        provider_data["current_tokens"] = max_tokens

                    self.balance_usdc -= recharge_cost
                    provider_data["last_recharge"] = datetime.now()

                    recharge_record = {
                        "provider": provider_name,
                        "amount": recharge_amount,
                        "cost_usdc": float(recharge_cost),
                        "timestamp": datetime.now().isoformat(),
                        "new_balance": provider_data["current_tokens"]
                    }

                    self.recharge_history.append(recharge_record)
                    recharged.append(recharge_record)

                    logger.info(f"🔋 Recarregado {provider_name}: +{recharge_amount} tokens (${recharge_cost:.6f})")
                else:
                    logger.warning(f"Saldo insuficiente para recarregar {provider_name}: {self.balance_usdc} USDC")

        # Salvar estado após recargas
        if recharged:
            await self._save_state()

        return recharged

    async def _execute_revenue_generation(self):
        """Executa estratégias para gerar receita"""
        revenue_strategies = [
            self._execute_market_analysis,
            self._execute_content_generation,
            self._execute_code_review,
            self._execute_data_analysis,
            self._execute_translation_service
        ]

        # Executar 2-3 estratégias aleatórias por ciclo
        strategies_to_run = random.sample(revenue_strategies, random.randint(2, 3))

        total_revenue = Decimal('0')

        for strategy in strategies_to_run:
            try:
                revenue = await strategy()
                if revenue:
                    total_revenue += revenue
                    logger.info(f"💰 Receita gerada: ${revenue:.4f} USDC")
            except Exception as e:
                logger.error(f"Erro na estratégia de receita: {e}")

        if total_revenue > 0:
            self.balance_usdc += total_revenue
            logger.info(f"📈 Receita total deste ciclo: ${total_revenue:.4f} USDC")
            logger.info(f"💰 Saldo atual: {self.balance_usdc} USDC")

            # Salvar estado
            await self._save_state()

        return total_revenue

    async def _execute_market_analysis(self) -> Decimal:
        """Executa análise de mercado para gerar receita"""
        # Simulação de análise de mercado
        await asyncio.sleep(random.uniform(2, 5))

        # Consumir tokens
        tokens_used = random.randint(500, 2000)
        await self.consume_tokens("gemini", tokens_used)

        # Gerar receita
        revenue = Decimal(str(random.uniform(0.05, 0.20)))

        self.usage_history.append({
            "service": "market_analysis",
            "tokens_used": tokens_used,
            "revenue_usdc": float(revenue),
            "timestamp": datetime.now().isoformat()
        })

        return revenue

    async def _execute_content_generation(self) -> Decimal:
        """Executa geração de conteúdo para gerar receita"""
        # Simulação de geração de conteúdo
        await asyncio.sleep(random.uniform(3, 7))

        # Consumir tokens
        tokens_used = random.randint(1000, 3000)
        await self.consume_tokens("kiro", tokens_used)

        # Gerar receita
        revenue = Decimal(str(random.uniform(0.10, 0.30)))

        self.usage_history.append({
            "service": "content_generation",
            "tokens_used": tokens_used,
            "revenue_usdc": float(revenue),
            "timestamp": datetime.now().isoformat()
        })

        return revenue

    async def _execute_code_review(self) -> Decimal:
        """Executa revisão de código para gerar receita"""
        # Simulação de revisão de código
        await asyncio.sleep(random.uniform(4, 8))

        # Consumir tokens
        tokens_used = random.randint(800, 2500)
        await self.consume_tokens("openclaude", tokens_used)

        # Gerar receita
        revenue = Decimal(str(random.uniform(0.15, 0.35)))

        self.usage_history.append({
            "service": "code_review",
            "tokens_used": tokens_used,
            "revenue_usdc": float(revenue),
            "timestamp": datetime.now().isoformat()
        })

        return revenue

    async def _execute_data_analysis(self) -> Decimal:
        """Executa análise de dados para gerar receita"""
        # Simulação de análise de dados
        await asyncio.sleep(random.uniform(5, 10))

        # Consumir tokens
        tokens_used = random.randint(1500, 4000)
        await self.consume_tokens("nvidia", tokens_used)

        # Gerar receita
        revenue = Decimal(str(random.uniform(0.20, 0.50)))

        self.usage_history.append({
            "service": "data_analysis",
            "tokens_used": tokens_used,
            "revenue_usdc": float(revenue),
            "timestamp": datetime.now().isoformat()
        })

        return revenue

    async def _execute_translation_service(self) -> Decimal:
        """Executa serviço de tradução para gerar receita"""
        # Simulação de tradução
        await asyncio.sleep(random.uniform(2, 6))

        # Consumir tokens
        tokens_used = random.randint(1200, 3500)
        await self.consume_tokens("9router", tokens_used)

        # Gerar receita
        revenue = Decimal(str(random.uniform(0.08, 0.25)))

        self.usage_history.append({
            "service": "translation",
            "tokens_used": tokens_used,
            "revenue_usdc": float(revenue),
            "timestamp": datetime.now().isoformat()
        })

        return revenue

    async def consume_tokens(self, provider: str, tokens: int) -> bool:
        """Consome tokens de um provedor"""
        if provider not in self.providers:
            logger.error(f"Provedor {provider} não encontrado")
            return False

        provider_data = self.providers[provider]

        if provider_data["current_tokens"] < tokens:
            logger.warning(f"Tokens insuficientes em {provider}: {provider_data['current_tokens']}/{tokens}")
            return False

        provider_data["current_tokens"] -= tokens
        provider_data["used_today"] += tokens

        logger.debug(f"Consumidos {tokens} tokens de {provider}")

        return True

    async def _update_usage_stats(self):
        """Atualiza estatísticas de uso"""
        now = datetime.now()

        # Resetar uso diário se passou um dia
        for provider_data in self.providers.values():
            if provider_data.get("last_recharge"):
                last_recharge = provider_data["last_recharge"]
                if isinstance(last_recharge, str):
                    last_recharge = datetime.fromisoformat(last_recharge)

                if (now - last_recharge).days >= 1:
                    provider_data["used_today"] = 0

    async def _load_state(self):
        """Carrega estado salvo do gerenciador"""
        state_file = "data/token_manager_state.json"

        try:
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)

                self.balance_usdc = Decimal(str(state.get("balance_usdc", 1000)))

                for provider_name, provider_data in state.get("providers", {}).items():
                    if provider_name in self.providers:
                        self.providers[provider_name].update(provider_data)

                self.recharge_history = state.get("recharge_history", [])
                self.usage_history = state.get("usage_history", [])

                logger.info(f"Estado carregado de {state_file}")
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")

    async def _save_state(self):
        """Salva estado do gerenciador"""
        state_file = "data/token_manager_state.json"

        try:
            os.makedirs(os.path.dirname(state_file), exist_ok=True)

            state = {
                "balance_usdc": str(self.balance_usdc),
                "providers": self.providers,
                "recharge_history": self.recharge_history[-100:],  # Últimas 100 recargas
                "usage_history": self.usage_history[-100:],  # Últimos 100 usos
                "last_saved": datetime.now().isoformat()
            }

            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)

            logger.debug(f"Estado salvo em {state_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do gerenciador"""
        total_tokens = sum(p["current_tokens"] for p in self.providers.values())
        max_tokens = sum(p["max_tokens"] for p in self.providers.values())
        total_used_today = sum(p["used_today"] for p in self.providers.values())

        provider_stats = {}
        for name, data in self.providers.items():
            provider_stats[name] = {
                "current_tokens": data["current_tokens"],
                "max_tokens": data["max_tokens"],
                "percentage": (data["current_tokens"] / data["max_tokens"]) * 100,
                "used_today": data["used_today"],
                "daily_limit": data["daily_limit"],
                "last_recharge": data["last_recharge"]
            }

        return {
            "balance_usdc": str(self.balance_usdc),
            "total_tokens": total_tokens,
            "max_tokens": max_tokens,
            "total_used_today": total_used_today,
            "providers": provider_stats,
            "recharge_count": len(self.recharge_history),
            "usage_count": len(self.usage_history),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "timestamp": datetime.now().isoformat()
        }

    async def shutdown(self):
        """Desliga o gerenciador"""
        self.running = False
        await self._save_state()
        logger.info("🛑 Gerenciador de Tokens desligado")


# Instância global do gerenciador
token_manager = TokenManager()


async def start_token_manager():
    """Inicia o gerenciador de tokens"""
    manager = TokenManager()
    await manager.initialize()
    return manager