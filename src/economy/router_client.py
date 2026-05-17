"""
Roteador de IA - Sistema de rotação automática entre provedores de IA
Baseado na arquitetura Moltbook Crypto Bot
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import httpx
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Provedores de IA suportados"""
    GEMINI = "gemini"
    OPENCLAUDE = "openclaude"
    KIRO = "kiro"
    OPENROUTER = "openrouter"
    NVIDIA = "nvidia"
    NINEROUTER = "9router"  # Provedor específico para 9ROUTER


@dataclass
class AIRequest:
    """Estrutura de requisição para IA"""
    prompt: str
    provider: Optional[AIProvider] = None
    max_tokens: int = 2048
    temperature: float = 0.7
    context: Optional[Dict[str, Any]] = None


@dataclass
class AIResponse:
    """Estrutura de resposta da IA"""
    content: str
    provider: AIProvider
    tokens_used: int
    cost_usdc: float
    latency_ms: float
    timestamp: datetime


@dataclass
class ProviderConfig:
    """Configuração de provedor de IA"""
    provider: AIProvider
    api_key_env: str
    base_url: str
    model: str
    cost_per_token: float  # USDC por token
    max_tokens_per_minute: int
    enabled: bool = True
    priority: int = 1  # 1 = mais alta prioridade


class AIRouter:
    """Roteador inteligente de provedores de IA"""

    def __init__(self):
        self.providers: Dict[AIProvider, ProviderConfig] = self._load_providers_config()
        self.usage_stats: Dict[AIProvider, Dict[str, Any]] = {}
        self._initialize_stats()

    def _load_providers_config(self) -> Dict[AIProvider, ProviderConfig]:
        """Carrega configuração dos provedores do ambiente"""
        return {
            AIProvider.GEMINI: ProviderConfig(
                provider=AIProvider.GEMINI,
                api_key_env="GEMINI_API_KEY",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                model="gemini-2.0-flash",  # Modelo correto e disponível
                cost_per_token=0.00000025,  # $0.25 por 1M tokens
                max_tokens_per_minute=15000,
                enabled=bool(os.getenv("GEMINI_API_KEY")),
                priority=1
            ),
            AIProvider.OPENCLAUDE: ProviderConfig(
                provider=AIProvider.OPENCLAUDE,
                api_key_env="OPENCLAUDE_API_KEY",
                base_url="https://api.openclaude.ai/v1",
                model="claude-3-5-sonnet-20241022",
                cost_per_token=0.000003,  # $3 por 1M tokens
                max_tokens_per_minute=10000,
                enabled=bool(os.getenv("OPENCLAUDE_API_KEY")),
                priority=2
            ),
            AIProvider.KIRO: ProviderConfig(
                provider=AIProvider.KIRO,
                api_key_env="KIRO_API_KEY",
                base_url="https://api.kiro.ai/v1",
                model="kiro-1.0",
                cost_per_token=0.000002,  # $2 por 1M tokens
                max_tokens_per_minute=20000,
                enabled=bool(os.getenv("KIRO_API_KEY")),
                priority=3
            ),
            AIProvider.OPENROUTER: ProviderConfig(
                provider=AIProvider.OPENROUTER,
                api_key_env="OPENROUTER_API_KEY",
                base_url="http://localhost:20128/v1",  # 9ROUTER local
                model="gemini/gemini-3-flash-preview",  # Modelo do seu 9ROUTER
                cost_per_token=0.000001,  # Custo estimado
                max_tokens_per_minute=10000,
                enabled=bool(os.getenv("OPENROUTER_API_KEY")),
                priority=2  # Prioridade mais alta já que está local
            ),
            AIProvider.NVIDIA: ProviderConfig(
                provider=AIProvider.NVIDIA,
                api_key_env="NVIDIA_API_KEY",
                base_url="https://integrate.api.nvidia.com/v1",
                model="meta/llama-3.1-70b-instruct",
                cost_per_token=0.0000007,  # $0.70 por 1M tokens
                max_tokens_per_minute=30000,
                enabled=bool(os.getenv("NVIDIA_API_KEY")),
                priority=5
            ),
            AIProvider.NINEROUTER: ProviderConfig(
                provider=AIProvider.NINEROUTER,
                api_key_env="NINEROUTER_API_KEY",
                base_url="http://localhost:20128/v1",  # 9ROUTER local
                model="gemini/gemini-3-flash-preview",  # Modelo do seu 9ROUTER
                cost_per_token=0.0000005,  # Custo mais baixo (local)
                max_tokens_per_minute=20000,
                enabled=bool(os.getenv("NINEROUTER_API_KEY")),
                priority=1  # Prioridade mais alta (local, rápido)
            )
        }

    def _initialize_stats(self):
        """Inicializa estatísticas de uso"""
        for provider in self.providers:
            self.usage_stats[provider] = {
                "tokens_used": 0,
                "cost_usdc": 0.0,
                "requests": 0,
                "errors": 0,
                "last_used": None,
                "tokens_this_minute": 0,
                "minute_start": datetime.now()
            }

    def _select_provider(self, preferred_provider: Optional[AIProvider] = None) -> Optional[AIProvider]:
        """Seleciona o melhor provedor baseado em disponibilidade, custo e uso"""
        now = datetime.now()
        available_providers = []

        for provider, config in self.providers.items():
            if not config.enabled:
                continue

            # Verificar limite de tokens por minuto
            stats = self.usage_stats[provider]
            minute_start = stats["minute_start"]
            if now - minute_start > timedelta(minutes=1):
                stats["tokens_this_minute"] = 0
                stats["minute_start"] = now

            if stats["tokens_this_minute"] >= config.max_tokens_per_minute:
                continue

            available_providers.append((provider, config.priority, stats["cost_usdc"]))

        if not available_providers:
            return None

        # Ordenar por prioridade (mais alta primeiro) e custo (menor primeiro)
        available_providers.sort(key=lambda x: (x[1], x[2]))

        # Se há provedor preferido e ele está disponível, usá-lo
        if preferred_provider and preferred_provider in [p[0] for p in available_providers]:
            return preferred_provider

        return available_providers[0][0]

    async def process_request(self, request: AIRequest) -> Optional[AIResponse]:
        """Processa uma requisição através do provedor selecionado"""
        provider_name = request.provider or self._select_provider()
        if not provider_name:
            logger.error("Nenhum provedor de IA disponível")
            return None

        config = self.providers[provider_name]
        api_key = os.getenv(config.api_key_env)

        if not api_key:
            logger.error(f"API key não configurada para {provider_name}")
            return None

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await self._make_api_call(client, config, api_key, request)

                if response:
                    latency_ms = (time.time() - start_time) * 1000
                    tokens_used = self._estimate_tokens(response, request.prompt)
                    cost_usdc = tokens_used * config.cost_per_token

                    # Atualizar estatísticas
                    self._update_stats(provider_name, tokens_used, cost_usdc)

                    return AIResponse(
                        content=response,
                        provider=provider_name,
                        tokens_used=tokens_used,
                        cost_usdc=cost_usdc,
                        latency_ms=latency_ms,
                        timestamp=datetime.now()
                    )

        except Exception as e:
            logger.error(f"Erro ao processar requisição com {provider_name}: {e}")
            self.usage_stats[provider_name]["errors"] += 1
            return None

    async def _make_api_call(self, client: httpx.AsyncClient, config: ProviderConfig,
                           api_key: str, request: AIRequest) -> Optional[str]:
        """Faz chamada à API do provedor específico ou simula"""

        # Modo simulação para desenvolvimento
        if not api_key or api_key == "simulated":
            logger.info(f"[SIMULAÇÃO] Respondendo via {config.provider.value}")
            await asyncio.sleep(0.5)  # Simular latência

            # Respostas simuladas baseadas no provedor
            simulated_responses = {
                AIProvider.GEMINI: f"[Gemini Simulado] Resposta para: {request.prompt[:50]}...",
                AIProvider.OPENCLAUDE: f"[OpenClaude Simulado] Processado: {request.prompt[:50]}...",
                AIProvider.KIRO: f"[Kiro Simulado] Análise: {request.prompt[:50]}...",
                AIProvider.OPENROUTER: f"[OpenRouter Simulado] Via Claude 3.5 Sonnet: {request.prompt[:50]}...",
                AIProvider.NVIDIA: f"[NVIDIA Simulado] Modelo Llama 3.1: {request.prompt[:50]}..."
            }

            return simulated_responses.get(config.provider, f"Resposta simulada: {request.prompt[:100]}...")

        # Código real da API (mantido para quando tiver chaves)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": config.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }

        # Configurar URL baseada no provedor
        if config.provider == AIProvider.GEMINI:
            url = f"{config.base_url}/models/{config.model}:generateContent"
            payload = {
                "contents": [{"parts": [{"text": request.prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": request.max_tokens,
                    "temperature": request.temperature
                }
            }
        elif config.provider == AIProvider.NINEROUTER:
            # 9ROUTER usa endpoint padrão de chat/completions
            url = f"{config.base_url}/chat/completions"
            # Adicionar headers específicos do 9ROUTER se necessário
            headers["X-9Router-Version"] = "1.0"
        else:
            url = f"{config.base_url}/chat/completions"

        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if config.provider == AIProvider.GEMINI:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return data["choices"][0]["message"]["content"]

        except httpx.HTTPError as e:
            logger.error(f"HTTP error from {config.provider}: {e}")
            # Fallback para simulação em caso de erro
            return f"[Fallback Simulado] {config.provider.value}: {request.prompt[:50]}..."

    def _estimate_tokens(self, response: str, prompt: str) -> int:
        """Estima número de tokens (aproximação simples)"""
        # Aproximação: 1 token ≈ 4 caracteres em inglês
        total_text = prompt + response
        return len(total_text) // 4

    def _update_stats(self, provider: AIProvider, tokens_used: int, cost_usdc: float):
        """Atualiza estatísticas de uso"""
        stats = self.usage_stats[provider]
        stats["tokens_used"] += tokens_used
        stats["cost_usdc"] += cost_usdc
        stats["requests"] += 1
        stats["last_used"] = datetime.now()
        stats["tokens_this_minute"] += tokens_used

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso"""
        total_stats = {
            "total_tokens": 0,
            "total_cost_usdc": 0.0,
            "total_requests": 0,
            "total_errors": 0,
            "providers": {}
        }

        for provider, stats in self.usage_stats.items():
            total_stats["total_tokens"] += stats["tokens_used"]
            total_stats["total_cost_usdc"] += stats["cost_usdc"]
            total_stats["total_requests"] += stats["requests"]
            total_stats["total_errors"] += stats["errors"]

            total_stats["providers"][provider.value] = {
                "tokens_used": stats["tokens_used"],
                "cost_usdc": stats["cost_usdc"],
                "requests": stats["requests"],
                "errors": stats["errors"],
                "last_used": stats["last_used"].isoformat() if stats["last_used"] else None,
                "enabled": self.providers[provider].enabled
            }

        return total_stats

    def enable_provider(self, provider: AIProvider, enable: bool = True):
        """Habilita ou desabilita um provedor"""
        if provider in self.providers:
            self.providers[provider].enabled = enable
            logger.info(f"Provedor {provider.value} {'habilitado' if enable else 'desabilitado'}")

    def set_provider_priority(self, provider: AIProvider, priority: int):
        """Define prioridade de um provedor"""
        if provider in self.providers and 1 <= priority <= 10:
            self.providers[provider].priority = priority
            logger.info(f"Prioridade do provedor {provider.value} definida para {priority}")


# Instância global do roteador
router = AIRouter()


async def process_ai_request(prompt: str, provider: Optional[str] = None,
                           max_tokens: int = 2048, temperature: float = 0.7) -> Optional[AIResponse]:
    """
    Função de conveniência para processar requisições de IA

    Args:
        prompt: Texto do prompt
        provider: Nome do provedor (opcional)
        max_tokens: Máximo de tokens na resposta
        temperature: Temperatura para geração

    Returns:
        AIResponse ou None em caso de erro
    """
    provider_enum = None
    if provider:
        try:
            provider_enum = AIProvider(provider.lower())
        except ValueError:
            logger.warning(f"Provedor {provider} inválido, usando seleção automática")

    request = AIRequest(
        prompt=prompt,
        provider=provider_enum,
        max_tokens=max_tokens,
        temperature=temperature
    )

    return await router.process_request(request)