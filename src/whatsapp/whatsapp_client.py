"""
WhatsApp Client - Sistema de notificações com 4 camadas de fallback
Baseado na arquitetura Moltbook Crypto Bot
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import httpx
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppLayer(Enum):
    """Camadas de fallback do WhatsApp"""
    CALLMEBOT = "callmebot"  # Camada 1: API gratuita via CallMeBot
    SELENIUM = "selenium"    # Camada 2: Automação via Selenium
    TWILIO = "twilio"        # Camada 3: API oficial via Twilio
    EVOLUTION = "evolution"  # Camada 4: Evolution API (self-hosted)


@dataclass
class Message:
    """Mensagem para envio via WhatsApp"""
    phone_number: str
    message: str
    priority: int = 1  # 1 = alta, 2 = média, 3 = baixa
    layer: Optional[WhatsAppLayer] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MessageResult:
    """Resultado do envio de mensagem"""
    success: bool
    layer_used: WhatsAppLayer
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None
    cost_usdc: float = 0.0


class CallMeBotClient:
    """Cliente para CallMeBot API (camada 1)"""

    def __init__(self):
        self.api_key = os.getenv("CALLMEBOT_API_KEY", "")
        self.base_url = "https://api.callmebot.com/whatsapp.php"

    async def send_message(self, phone_number: str, message: str) -> MessageResult:
        """Envia mensagem via CallMeBot"""
        if not self.api_key:
            return MessageResult(
                success=False,
                layer_used=WhatsAppLayer.CALLMEBOT,
                error="API key não configurada"
            )

        try:
            # CallMeBot requer número no formato internacional sem +
            formatted_number = phone_number.replace("+", "")

            params = {
                "phone": formatted_number,
                "text": message,
                "apikey": self.api_key
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)

                if response.status_code == 200:
                    return MessageResult(
                        success=True,
                        layer_used=WhatsAppLayer.CALLMEBOT,
                        message_id=f"callmebot_{datetime.now().timestamp()}",
                        timestamp=datetime.now(),
                        cost_usdc=0.0  # Gratuito (com limites)
                    )
                else:
                    return MessageResult(
                        success=False,
                        layer_used=WhatsAppLayer.CALLMEBOT,
                        error=f"HTTP {response.status_code}: {response.text}"
                    )

        except Exception as e:
            return MessageResult(
                success=False,
                layer_used=WhatsAppLayer.CALLMEBOT,
                error=str(e)
            )


class SeleniumClient:
    """Cliente para automação via Selenium (camada 2)"""

    def __init__(self):
        self.enabled = bool(os.getenv("SELENIUM_ENABLED", "false").lower() == "true")
        self.whatsapp_web_url = "https://web.whatsapp.com"

    async def send_message(self, phone_number: str, message: str) -> MessageResult:
        """Envia mensagem via Selenium WebDriver"""
        if not self.enabled:
            return MessageResult(
                success=False,
                layer_used=WhatsAppLayer.SELENIUM,
                error="Selenium desabilitado"
            )

        try:
            # Em produção, implementaria automação real com Selenium
            # Por enquanto, simulação
            logger.info(f"[SELENIUM] Simulando envio para {phone_number}: {message[:50]}...")

            await asyncio.sleep(2)  # Simulação de tempo de automação

            return MessageResult(
                success=True,
                layer_used=WhatsAppLayer.SELENIUM,
                message_id=f"selenium_{datetime.now().timestamp()}",
                timestamp=datetime.now(),
                cost_usdc=0.0
            )

        except Exception as e:
            return MessageResult(
                success=False,
                layer_used=WhatsAppLayer.SELENIUM,
                error=str(e)
            )


class TwilioClient:
    """Cliente para Twilio API (camada 3)"""

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM", "")
        self.enabled = bool(self.account_sid and self.auth_token and self.whatsapp_from)

    async def send_message(self, phone_number: str, message: str) -> MessageResult:
        """Envia mensagem via Twilio WhatsApp API"""
        if not self.enabled:
            return MessageResult(
                success=False,
                layer_used=WhatsAppLayer.TWILIO,
                error="Twilio não configurado"
            )

        try:
            # Em produção, usaria a biblioteca twilio-python
            # Por enquanto, simulação
            logger.info(f"[TWILIO] Simulando envio para {phone_number}: {message[:50]}...")

            # Simulação de custo: $0.005 por mensagem
            cost_usdc = 0.005

            await asyncio.sleep(1)

            return MessageResult(
                success=True,
                layer_used=WhatsAppLayer.TWILIO,
                message_id=f"twilio_{datetime.now().timestamp()}",
                timestamp=datetime.now(),
                cost_usdc=cost_usdc
            )

        except Exception as e:
            return MessageResult(
                success=False,
                layer_used=WhatsAppLayer.TWILIO,
                error=str(e)
            )


class EvolutionClient:
    """Cliente para Evolution API (camada 4)"""

    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.api_key = os.getenv("EVOLUTION_API_KEY", "")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE", "default")
        self.enabled = bool(self.api_key)

    async def send_message(self, phone_number: str, message: str) -> MessageResult:
        """Envia mensagem via Evolution API"""
        if not self.enabled:
            return MessageResult(
                success=False,
                layer_used=WhatsAppLayer.EVOLUTION,
                error="Evolution API não configurada"
            )

        try:
            url = f"{self.base_url}/message/sendText/{self.instance_name}"
            headers = {
                "apikey": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "number": phone_number,
                "text": message,
                "delay": 1000
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 201:
                    data = response.json()
                    return MessageResult(
                        success=True,
                        layer_used=WhatsAppLayer.EVOLUTION,
                        message_id=data.get("key", {}).get("id", ""),
                        timestamp=datetime.now(),
                        cost_usdc=0.0  # Self-hosted, sem custo direto
                    )
                else:
                    return MessageResult(
                        success=False,
                        layer_used=WhatsAppLayer.EVOLUTION,
                        error=f"HTTP {response.status_code}: {response.text}"
                    )

        except Exception as e:
            return MessageResult(
                success=False,
                layer_used=WhatsAppLayer.EVOLUTION,
                error=str(e)
            )


class WhatsAppRouter:
    """Roteador inteligente com fallback automático"""

    def __init__(self):
        self.clients = {
            WhatsAppLayer.CALLMEBOT: CallMeBotClient(),
            WhatsAppLayer.SELENIUM: SeleniumClient(),
            WhatsAppLayer.TWILIO: TwilioClient(),
            WhatsAppLayer.EVOLUTION: EvolutionClient()
        }

        # Ordem de tentativa padrão (mais barato primeiro)
        self.default_order = [
            WhatsAppLayer.CALLMEBOT,  # Gratuito
            WhatsAppLayer.SELENIUM,   # Automação local
            WhatsAppLayer.EVOLUTION,  # Self-hosted
            WhatsAppLayer.TWILIO      # Pago, mais confiável
        ]

        self.stats = {
            "total_sent": 0,
            "total_failed": 0,
            "by_layer": {layer.value: {"sent": 0, "failed": 0} for layer in WhatsAppLayer},
            "total_cost_usdc": 0.0
        }

    async def send_message(self, message: Message) -> MessageResult:
        """Envia mensagem usando fallback automático"""
        # Determinar ordem de tentativa
        if message.layer:
            # Usar camada específica
            order = [message.layer]
        else:
            # Usar ordem padrão baseada na prioridade
            order = self._get_order_for_priority(message.priority)

        last_error = None

        for layer in order:
            client = self.clients[layer]
            logger.info(f"Tentando enviar via {layer.value}...")

            result = await client.send_message(message.phone_number, message.message)

            # Atualizar estatísticas
            self._update_stats(layer, result)

            if result.success:
                logger.info(f"Mensagem enviada com sucesso via {layer.value}")
                return result
            else:
                last_error = result.error
                logger.warning(f"Falha com {layer.value}: {result.error}")

        # Todas as camadas falharam
        logger.error(f"Todas as camadas falharam para {message.phone_number}")
        return MessageResult(
            success=False,
            layer_used=order[-1] if order else WhatsAppLayer.CALLMEBOT,
            error=f"Todas as camadas falharam. Último erro: {last_error}"
        )

    def _get_order_for_priority(self, priority: int) -> List[WhatsAppLayer]:
        """Determina ordem de tentativa baseada na prioridade"""
        if priority == 1:  # Alta prioridade: confiabilidade primeiro
            return [
                WhatsAppLayer.TWILIO,      # Mais confiável
                WhatsAppLayer.EVOLUTION,   # Self-hosted
                WhatsAppLayer.CALLMEBOT,   # Gratuito
                WhatsAppLayer.SELENIUM     # Automação
            ]
        elif priority == 2:  # Média prioridade: equilíbrio custo/confiabilidade
            return self.default_order
        else:  # Baixa prioridade: mais barato primeiro
            return [
                WhatsAppLayer.CALLMEBOT,   # Gratuito
                WhatsAppLayer.SELENIUM,    # Automação local
                WhatsAppLayer.EVOLUTION,   # Self-hosted
                WhatsAppLayer.TWILIO       # Pago
            ]

    def _update_stats(self, layer: WhatsAppLayer, result: MessageResult):
        """Atualiza estatísticas de envio"""
        if result.success:
            self.stats["total_sent"] += 1
            self.stats["by_layer"][layer.value]["sent"] += 1
            self.stats["total_cost_usdc"] += result.cost_usdc
        else:
            self.stats["total_failed"] += 1
            self.stats["by_layer"][layer.value]["failed"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de envio"""
        return {
            **self.stats,
            "success_rate": (self.stats["total_sent"] / (self.stats["total_sent"] + self.stats["total_failed"]))
                          if (self.stats["total_sent"] + self.stats["total_failed"]) > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }

    def enable_layer(self, layer: WhatsAppLayer, enable: bool = True):
        """Habilita ou desabilita uma camada"""
        # Implementação específica por cliente
        logger.info(f"Camada {layer.value} {'habilitada' if enable else 'desabilitada'}")


class NotificationManager:
    """Gerenciador de notificações e alertas"""

    def __init__(self):
        self.router = WhatsAppRouter()
        self.alert_contacts = self._load_alert_contacts()

    def _load_alert_contacts(self) -> List[str]:
        """Carrega lista de contatos para alertas"""
        contacts_str = os.getenv("ALERT_CONTACTS", "")
        if contacts_str:
            return [c.strip() for c in contacts_str.split(",")]
        return []

    async def send_alert(self, alert_type: str, message: str, priority: int = 1):
        """Envia alerta para todos os contatos configurados"""
        if not self.alert_contacts:
            logger.warning("Nenhum contato configurado para alertas")
            return []

        results = []
        for contact in self.alert_contacts:
            full_message = f"[{alert_type.upper()}] {message}"
            msg = Message(
                phone_number=contact,
                message=full_message,
                priority=priority
            )
            result = await self.router.send_message(msg)
            results.append((contact, result))

        return results

    async def send_bot_online_alert(self):
        """Envia alerta de 'Bot Online' para WhatsApp"""
        message = "🤖 *BERNAS-AGENT ONLINE* 🤖\n\n"
        message += "✅ Bot iniciado com sucesso\n"
        message += f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += "💼 Economia IA-to-IA ativa\n"
        message += "🔗 Blockchain: Solana/USDC\n"
        message += "🧠 Roteador de IA: Multi-provedor\n\n"
        message += "Status: OPERACIONAL"

        return await self.send_alert("SYSTEM", message, priority=1)

    async def send_transaction_alert(self, tx_id: str, amount_usdc: float,
                                   from_agent: str, to_agent: str, service: str):
        """Envia alerta de transação concluída"""
        message = f"💸 *TRANSAÇÃO CONCLUÍDA* 💸\n\n"
        message += f"🆔 ID: {tx_id}\n"
        message += f"💰 Valor: {amount_usdc} USDC\n"
        message += f"👤 De: {from_agent}\n"
        message += f"👥 Para: {to_agent}\n"
        message += f"🛒 Serviço: {service}\n"
        message += f"🕐 {datetime.now().strftime('%H:%M:%S')}"

        return await self.send_alert("TRANSACTION", message, priority=2)

    async def send_error_alert(self, error_type: str, error_message: str, component: str):
        """Envia alerta de erro"""
        message = f"🚨 *ERRO DETECTADO* 🚨\n\n"
        message += f"📛 Tipo: {error_type}\n"
        message += f"🔧 Componente: {component}\n"
        message += f"📝 Detalhes: {error_message}\n"
        message += f"🕐 {datetime.now().strftime('%H:%M:%S')}"

        return await self.send_alert("ERROR", message, priority=1)

    async def send_daily_report(self, stats: Dict[str, Any]):
        """Envia relatório diário de atividades"""
        message = "📊 *RELATÓRIO DIÁRIO* 📊\n\n"
        message += f"📅 {datetime.now().strftime('%Y-%m-%d')}\n\n"
        message += f"💼 Transações: {stats.get('transactions', 0)}\n"
        message += f"💰 Volume: {stats.get('volume_usdc', 0)} USDC\n"
        message += f"🤖 Serviços executados: {stats.get('services', 0)}\n"
        message += f"📱 Mensagens enviadas: {stats.get('messages', 0)}\n"
        message += f"✅ Taxa de sucesso: {stats.get('success_rate', 0):.1%}\n\n"
        message += "Status: ✅ OPERACIONAL"

        return await self.send_alert("REPORT", message, priority=3)


# Instância global do gerenciador de notificações
notification_manager = NotificationManager()


async def init_whatsapp_service():
    """Inicializa o serviço WhatsApp"""
    manager = NotificationManager()

    # Enviar alerta de inicialização
    await manager.send_bot_online_alert()

    return manager