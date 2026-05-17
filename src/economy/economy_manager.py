"""
Gerenciador de Economia - Sistema de pagamentos HTTP 402 e marketplace IA-to-IA
Baseado na arquitetura Moltbook Crypto Bot
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from decimal import Decimal
import aiohttp
from aiohttp import web

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Service:
    """Serviço disponível no marketplace"""
    service_id: str
    name: str
    description: str
    price_usdc: Decimal  # Preço em USDC
    provider: str  # Provedor de IA que oferece o serviço
    endpoint: str  # Endpoint HTTP para consumir o serviço
    rate_limit_per_minute: int = 10
    enabled: bool = True


@dataclass
class Transaction:
    """Transação econômica entre IAs"""
    tx_id: str
    from_agent: str
    to_agent: str
    amount_usdc: Decimal
    service_id: str
    status: str  # pending, completed, failed, refunded
    created_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Wallet:
    """Carteira de um agente"""
    agent_id: str
    balance_usdc: Decimal
    public_key: str  # Chave pública da carteira Solana
    last_updated: datetime
    pending_balance: Decimal = Decimal('0')


class EconomyManager:
    """Gerenciador central da economia IA-to-IA"""

    def __init__(self):
        self.services: Dict[str, Service] = self._load_default_services()
        self.transactions: Dict[str, Transaction] = {}
        self.wallets: Dict[str, Wallet] = {}
        self.http_server: Optional[web.Application] = None
        self.running = False

    def _load_default_services(self) -> Dict[str, Service]:
        """Carrega serviços padrão do marketplace"""
        return {
            "analysis_001": Service(
                service_id="analysis_001",
                name="Análise de Mercado",
                description="Análise detalhada de tendências de mercado cripto",
                price_usdc=Decimal('0.05'),
                provider="gemini",
                endpoint="/api/v1/analyze/market",
                rate_limit_per_minute=5
            ),
            "code_review_002": Service(
                service_id="code_review_002",
                name="Revisão de Código",
                description="Revisão de código Python/JavaScript com sugestões",
                price_usdc=Decimal('0.10'),
                provider="openclaude",
                endpoint="/api/v1/review/code",
                rate_limit_per_minute=3
            ),
            "content_gen_003": Service(
                service_id="content_gen_003",
                name="Geração de Conteúdo",
                description="Geração de conteúdo técnico e marketing",
                price_usdc=Decimal('0.15'),
                provider="kiro",
                endpoint="/api/v1/generate/content",
                rate_limit_per_minute=8
            ),
            "data_analysis_004": Service(
                service_id="data_analysis_004",
                name="Análise de Dados",
                description="Análise de datasets e geração de insights",
                price_usdc=Decimal('0.20'),
                provider="nvidia",
                endpoint="/api/v1/analyze/data",
                rate_limit_per_minute=2
            ),
            "translation_005": Service(
                service_id="translation_005",
                name="Tradução Técnica",
                description="Tradução de documentação técnica entre idiomas",
                price_usdc=Decimal('0.08'),
                provider="openrouter",
                endpoint="/api/v1/translate/tech",
                rate_limit_per_minute=10
            )
        }

    async def start_http_server(self, host: str = "0.0.0.0", port: int = 4020):
        """Inicia servidor HTTP 402 para pagamentos"""
        app = web.Application()

        # Endpoints do marketplace
        app.router.add_get('/api/v1/services', self.handle_list_services)
        app.router.add_get('/api/v1/services/{service_id}', self.handle_service_detail)
        app.router.add_post('/api/v1/purchase', self.handle_purchase)
        app.router.add_get('/api/v1/transactions/{tx_id}', self.handle_transaction_status)
        app.router.add_get('/api/v1/wallet/{agent_id}', self.handle_wallet_balance)

        # Endpoints de serviço
        for service in self.services.values():
            app.router.add_post(service.endpoint, self.handle_service_execution)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)

        self.http_server = app
        self.running = True

        logger.info(f"Servidor HTTP 402 iniciado em http://{host}:{port}")
        await site.start()

    async def handle_list_services(self, request: web.Request) -> web.Response:
        """Lista todos os serviços disponíveis"""
        services_list = []
        for service in self.services.values():
            if service.enabled:
                service_dict = asdict(service)
                # Converter Decimal para string para serialização JSON
                service_dict['price_usdc'] = str(service_dict['price_usdc'])
                services_list.append(service_dict)

        return web.json_response({
            "status": "success",
            "services": services_list,
            "timestamp": datetime.now().isoformat()
        })

    async def handle_service_detail(self, request: web.Request) -> web.Response:
        """Detalhes de um serviço específico"""
        service_id = request.match_info['service_id']

        if service_id not in self.services:
            return web.json_response({
                "status": "error",
                "message": f"Serviço {service_id} não encontrado"
            }, status=404)

        service = self.services[service_id]
        if not service.enabled:
            return web.json_response({
                "status": "error",
                "message": f"Serviço {service_id} desabilitado"
            }, status=403)

        service_dict = asdict(service)
        service_dict['price_usdc'] = str(service_dict['price_usdc'])

        return web.json_response({
            "status": "success",
            "service": service_dict,
            "timestamp": datetime.now().isoformat()
        })

    async def handle_purchase(self, request: web.Request) -> web.Response:
        """Processa compra de um serviço"""
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response({
                "status": "error",
                "message": "JSON inválido"
            }, status=400)

        required_fields = ['service_id', 'from_agent', 'to_agent', 'payment_signature']
        for field in required_fields:
            if field not in data:
                return web.json_response({
                    "status": "error",
                    "message": f"Campo obrigatório faltando: {field}"
                }, status=400)

        service_id = data['service_id']
        from_agent = data['from_agent']
        to_agent = data['to_agent']
        payment_signature = data['payment_signature']

        # Verificar se serviço existe e está habilitado
        if service_id not in self.services:
            return web.json_response({
                "status": "error",
                "message": f"Serviço {service_id} não encontrado"
            }, status=404)

        service = self.services[service_id]
        if not service.enabled:
            return web.json_response({
                "status": "error",
                "message": f"Serviço {service_id} desabilitado"
            }, status=403)

        # Verificar saldo do comprador
        if from_agent not in self.wallets:
            return web.json_response({
                "status": "error",
                "message": f"Carteira do agente {from_agent} não encontrada"
            }, status=404)

        wallet = self.wallets[from_agent]
        if wallet.balance_usdc < service.price_usdc:
            return web.json_response({
                "status": "error",
                "message": "Saldo insuficiente",
                "required": str(service.price_usdc),
                "available": str(wallet.balance_usdc)
            }, status=402)  # HTTP 402 Payment Required

        # Verificar assinatura de pagamento (simplificado)
        if not await self._verify_payment_signature(payment_signature, from_agent, service.price_usdc):
            return web.json_response({
                "status": "error",
                "message": "Assinatura de pagamento inválida"
            }, status=400)

        # Criar transação
        tx_id = f"tx_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{from_agent[:8]}"
        transaction = Transaction(
            tx_id=tx_id,
            from_agent=from_agent,
            to_agent=to_agent,
            amount_usdc=service.price_usdc,
            service_id=service_id,
            status="pending",
            created_at=datetime.now(),
            metadata=data.get('metadata', {})
        )

        self.transactions[tx_id] = transaction

        # Reservar saldo
        wallet.pending_balance += service.price_usdc
        wallet.balance_usdc -= service.price_usdc

        logger.info(f"Transação {tx_id} criada: {from_agent} -> {to_agent} ({service.price_usdc} USDC)")

        return web.json_response({
            "status": "success",
            "transaction_id": tx_id,
            "service": service.name,
            "price": str(service.price_usdc),
            "next_step": f"POST {service.endpoint} com transaction_id={tx_id}",
            "timestamp": datetime.now().isoformat()
        })

    async def handle_service_execution(self, request: web.Request) -> web.Response:
        """Executa um serviço após pagamento confirmado"""
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response({
                "status": "error",
                "message": "JSON inválido"
            }, status=400)

        if 'transaction_id' not in data:
            return web.json_response({
                "status": "error",
                "message": "transaction_id obrigatório"
            }, status=400)

        tx_id = data['transaction_id']

        if tx_id not in self.transactions:
            return web.json_response({
                "status": "error",
                "message": f"Transação {tx_id} não encontrada"
            }, status=404)

        transaction = self.transactions[tx_id]

        if transaction.status != "pending":
            return web.json_response({
                "status": "error",
                "message": f"Transação já está {transaction.status}"
            }, status=400)

        # Verificar se serviço ainda está disponível
        service_id = transaction.service_id
        if service_id not in self.services:
            transaction.status = "failed"
            return web.json_response({
                "status": "error",
                "message": f"Serviço {service_id} não existe mais"
            }, status=404)

        service = self.services[service_id]

        # Executar serviço (simulação)
        try:
            # Aqui integraria com o roteador de IA
            result = await self._execute_service(service, data.get('input', {}))

            # Completar transação
            transaction.status = "completed"
            transaction.completed_at = datetime.now()

            # Liberar saldo pendente e transferir para vendedor
            from_wallet = self.wallets[transaction.from_agent]
            from_wallet.pending_balance -= transaction.amount_usdc

            if transaction.to_agent not in self.wallets:
                # Criar carteira para vendedor se não existir
                self.wallets[transaction.to_agent] = Wallet(
                    agent_id=transaction.to_agent,
                    balance_usdc=Decimal('0'),
                    public_key="",  # Será configurada depois
                    last_updated=datetime.now()
                )

            to_wallet = self.wallets[transaction.to_agent]
            to_wallet.balance_usdc += transaction.amount_usdc
            to_wallet.last_updated = datetime.now()

            logger.info(f"Transação {tx_id} completada: {transaction.amount_usdc} USDC transferidos")

            return web.json_response({
                "status": "success",
                "transaction_id": tx_id,
                "service": service.name,
                "result": result,
                "completed_at": transaction.completed_at.isoformat(),
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            transaction.status = "failed"
            logger.error(f"Erro ao executar serviço {service_id}: {e}")

            # Reembolsar comprador
            from_wallet = self.wallets[transaction.from_agent]
            from_wallet.pending_balance -= transaction.amount_usdc
            from_wallet.balance_usdc += transaction.amount_usdc

            return web.json_response({
                "status": "error",
                "message": f"Erro ao executar serviço: {str(e)}",
                "refunded": True,
                "timestamp": datetime.now().isoformat()
            }, status=500)

    async def handle_transaction_status(self, request: web.Request) -> web.Response:
        """Consulta status de uma transação"""
        tx_id = request.match_info['tx_id']

        if tx_id not in self.transactions:
            return web.json_response({
                "status": "error",
                "message": f"Transação {tx_id} não encontrado"
            }, status=404)

        transaction = self.transactions[tx_id]
        transaction_dict = asdict(transaction)
        transaction_dict['amount_usdc'] = str(transaction_dict['amount_usdc'])

        return web.json_response({
            "status": "success",
            "transaction": transaction_dict,
            "timestamp": datetime.now().isoformat()
        })

    async def handle_wallet_balance(self, request: web.Request) -> web.Response:
        """Consulta saldo de uma carteira"""
        agent_id = request.match_info['agent_id']

        if agent_id not in self.wallets:
            return web.json_response({
                "status": "error",
                "message": f"Carteira do agente {agent_id} não encontrada"
            }, status=404)

        wallet = self.wallets[agent_id]

        return web.json_response({
            "status": "success",
            "agent_id": agent_id,
            "balance_usdc": str(wallet.balance_usdc),
            "pending_balance": str(wallet.pending_balance),
            "total_balance": str(wallet.balance_usdc + wallet.pending_balance),
            "last_updated": wallet.last_updated.isoformat(),
            "timestamp": datetime.now().isoformat()
        })

    async def _verify_payment_signature(self, signature: str, agent_id: str, amount: Decimal) -> bool:
        """Verifica assinatura de pagamento (simplificado)"""
        # Em produção, integraria com Solana para verificar assinatura real
        # Por enquanto, aceita qualquer assinatura não vazia
        return bool(signature and signature.strip())

    async def _execute_service(self, service: Service, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa um serviço específico"""
        # Simulação de execução de serviço
        # Em produção, integraria com o roteador de IA

        service_map = {
            "analysis_001": {
                "result": "Análise de mercado: Tendência bullish detectada com 85% de confiança",
                "confidence": 0.85,
                "recommendation": "Hold position"
            },
            "code_review_002": {
                "result": "Código revisado: 3 issues encontrados, 2 críticos, 1 warning",
                "issues": 3,
                "critical": 2,
                "warnings": 1,
                "suggestions": ["Use type hints", "Add error handling"]
            },
            "content_gen_003": {
                "result": "Conteúdo gerado: Artigo técnico sobre blockchain de 500 palavras",
                "word_count": 500,
                "topics": ["blockchain", "smart contracts", "decentralization"]
            },
            "data_analysis_004": {
                "result": "Análise de dados: Padrões identificados, outliers detectados",
                "patterns": 5,
                "outliers": 2,
                "insights": ["Correlação forte entre variáveis A e B"]
            },
            "translation_005": {
                "result": "Tradução concluída: Documentação técnica de EN para PT-BR",
                "source_lang": "EN",
                "target_lang": "PT-BR",
                "word_count": 1200,
                "accuracy": 0.95
            }
        }

        return service_map.get(service.service_id, {
            "result": f"Serviço {service.name} executado com sucesso",
            "input_received": input_data
        })

    def register_wallet(self, agent_id: str, public_key: str, initial_balance: Decimal = Decimal('100')):
        """Registra uma nova carteira"""
        if agent_id in self.wallets:
            logger.warning(f"Carteira do agente {agent_id} já registrada")
            return False

        wallet = Wallet(
            agent_id=agent_id,
            balance_usdc=initial_balance,
            public_key=public_key,
            last_updated=datetime.now()
        )

        self.wallets[agent_id] = wallet
        logger.info(f"Carteira registrada para agente {agent_id} com saldo inicial {initial_balance} USDC")
        return True

    def add_service(self, service: Service):
        """Adiciona um novo serviço ao marketplace"""
        if service.service_id in self.services:
            logger.warning(f"Serviço {service.service_id} já existe")
            return False

        self.services[service.service_id] = service
        logger.info(f"Serviço {service.name} adicionado ao marketplace")
        return True

    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do marketplace"""
        total_services = len(self.services)
        enabled_services = sum(1 for s in self.services.values() if s.enabled)
        total_transactions = len(self.transactions)
        completed_transactions = sum(1 for t in self.transactions.values() if t.status == "completed")
        total_volume = sum(t.amount_usdc for t in self.transactions.values() if t.status == "completed")

        return {
            "total_services": total_services,
            "enabled_services": enabled_services,
            "total_transactions": total_transactions,
            "completed_transactions": completed_transactions,
            "total_volume_usdc": str(total_volume),
            "active_wallets": len(self.wallets),
            "timestamp": datetime.now().isoformat()
        }


# Instância global do gerenciador de economia
economy_manager = EconomyManager()


async def start_economy_server():
    """Função para iniciar o servidor de economia"""
    manager = EconomyManager()

    # Registrar algumas carteiras de exemplo
    manager.register_wallet("agent_alpha", "AlphaPublicKey123", Decimal('500'))
    manager.register_wallet("agent_beta", "BetaPublicKey456", Decimal('300'))
    manager.register_wallet("agent_gamma", "GammaPublicKey789", Decimal('200'))

    await manager.start_http_server()
    return manager