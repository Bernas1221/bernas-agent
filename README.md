# 🤖 BERNAS-AGENT

**Bot de Economia Autônoma entre IAs**  
*Integração: IA + Blockchain (Solana) + WhatsApp*  
*Baseado na arquitetura Moltbook Crypto Bot*

---

## 📋 Visão Geral

O **BERNAS-AGENT** é um bot autônomo que implementa uma economia IA-to-IA, permitindo que diferentes agentes de IA comprem e vendem serviços entre si usando criptomoedas (USDC na Solana) e se comuniquem via WhatsApp.

### ✨ Funcionalidades Principais

- **🧠 Roteador de IA Inteligente**: Rotação automática entre 5 provedores (Gemini, OpenClaude, Kiro, OpenRouter, NVIDIA)
- **💼 Marketplace IA-to-IA**: Sistema de pagamentos HTTP 402 com múltiplos serviços
- **🔗 Integração Blockchain**: Carteiras Solana e transações USDC (SPL Token)
- **📱 WhatsApp Multi-camadas**: 4 camadas de fallback para notificações
- **⏰ Agendador Automático**: Cronjobs para tarefas periódicas e controle de cotas
- **🌐 API REST**: Monitoramento e controle via HTTP
- **🛡️ Segurança**: Chaves privadas apenas via variáveis de ambiente

---

## 🏗️ Arquitetura

```
bernas-agent/
├── src/
│   ├── economy/           # Núcleo de economia e roteador de IA
│   │   ├── router_client.py
│   │   └── economy_manager.py
│   ├── solana/           # Integração Solana e carteiras
│   │   └── solana_client.py
│   └── whatsapp/         # Sistema de notificações WhatsApp
│       └── whatsapp_client.py
├── config/               # Configurações e templates
├── scripts/             # Scripts de inicialização
├── logs/                # Logs do sistema
├── data/                # Dados persistentes
├── main.py              # Ponto de entrada principal
├── requirements.txt     # Dependências Python
├── .env.example         # Template de configuração
└── README.md           # Esta documentação
```

---

## 🚀 Instalação Rápida

### 1. Pré-requisitos

- **Python 3.11+**
- **Git** (opcional)
- **Contas nas APIs** (Gemini, OpenClaude, etc.)
- **Carteira Solana** com USDC para testes
- **Número WhatsApp** para alertas

### 2. Clonar e Configurar

```bash
# Clone o repositório (ou copie os arquivos)
cd C:\Users\Carlos\bernas-agent

# Copie o template de configuração
copy .env.example .env

# Edite o arquivo .env com suas chaves
notepad .env
```

### 3. Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar no Windows
.venv\Scripts\activate

# Ativar no Linux/Mac
source .venv/bin/activate
```

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Nota**: Para desenvolvimento inicial, você pode instalar apenas as dependências essenciais:

```bash
pip install aiohttp httpx python-dotenv
```

---

## ⚙️ Configuração

### Arquivo `.env` - Variáveis Essenciais

```env
# IA APIs (pelo menos uma necessária)
GEMINI_API_KEY=your_key_here

# Solana
SOLANA_PRIVATE_KEY=your_base58_private_key

# WhatsApp (pelo menos uma camada)
CALLMEBOT_API_KEY=your_key_here
ALERT_CONTACTS=+5511999999999
```

### Configurações Recomendadas

1. **Para testes**: Use apenas CallMeBot (gratuito) e uma API de IA
2. **Para produção**: Configure todas as camadas e APIs
3. **Segurança**: Nunca commit arquivos `.env` com chaves reais

---

## 🎯 Uso

### Iniciar o Bot

```bash
# Método 1: Script de inicialização
python scripts/start_bot.py

# Método 2: Direto
python main.py
```

### Verificar Status

```bash
# API de status (porta 8080)
curl http://localhost:8080/api/v1/status

# Health check
curl http://localhost:8080/api/v1/health
```

### Testar Funcionalidades

```bash
# Testar roteador de IA
curl -X POST http://localhost:8080/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Olá, como vai?"}'

# Listar serviços do marketplace
curl http://localhost:8080/api/v1/economy/stats
```

---

## 📱 WhatsApp - Camadas de Fallback

O bot usa 4 camadas em ordem de tentativa:

1. **CallMeBot** (gratuito) - API simples com limites
2. **Selenium** (automação) - WebDriver local
3. **Evolution API** (self-hosted) - Controle total
4. **Twilio** (pago) - Mais confiável

**Alerta automático**: Ao iniciar, o bot envia "🤖 BERNAS-AGENT ONLINE" para os contatos configurados.

---

## 💰 Economia IA-to-IA

### Serviços Disponíveis

| ID | Nome | Preço | Provedor |
|----|------|-------|----------|
| analysis_001 | Análise de Mercado | 0.05 USDC | Gemini |
| code_review_002 | Revisão de Código | 0.10 USDC | OpenClaude |
| content_gen_003 | Geração de Conteúdo | 0.15 USDC | Kiro |
| data_analysis_004 | Análise de Dados | 0.20 USDC | NVIDIA |
| translation_005 | Tradução Técnica | 0.08 USDC | OpenRouter |

### Fluxo de Pagamento

1. Cliente solicita serviço via HTTP 402
2. Sistema verifica saldo e assinatura
3. Executa serviço via roteador de IA
4. Transfere USDC para o provedor
5. Envia confirmação via WhatsApp

---

## 🔧 Implantação

### Square Cloud (Recomendado para 24/7)

1. Crie uma conta em [Square Cloud](https://squarecloud.app)
2. Crie um novo aplicativo "Worker"
3. Configure:
   - **Start Command**: `python scripts/start_bot.py`
   - **Python Version**: 3.11+
   - **Environment Variables**: Copie do seu `.env`

### Docker (Opcional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

### Servidor Dedicado

```bash
# Usar systemd para serviço 24/7
sudo nano /etc/systemd/system/bernas-agent.service

# Conteúdo:
[Unit]
Description=BERNAS-AGENT Bot
After=network.target

[Service]
Type=simple
User=bernas
WorkingDirectory=/opt/bernas-agent
EnvironmentFile=/opt/bernas-agent/.env
ExecStart=/opt/bernas-agent/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🛠️ Desenvolvimento

### Estrutura de Código

```python
# Exemplo: Adicionar novo provedor de IA
# 1. Adicione ao enum em src/economy/router_client.py
# 2. Configure em _load_providers_config()
# 3. Implemente _make_api_call() específico
```

### Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio

# Executar testes
pytest tests/
```

### Logs

```bash
# Monitorar logs em tempo real
tail -f logs/bernas_agent.log

# Logs estruturados (JSON)
cat logs/bernas_agent.log | jq .
```

---

## ⚠️ Solução de Problemas

### Problemas Comuns

1. **"API key não configurada"**
   - Verifique se o `.env` está no diretório correto
   - Confirme se as variáveis têm os nomes corretos

2. **"Nenhum provedor de IA disponível"**
   - Configure pelo menos uma API de IA
   - Verifique limites de quota/tokens

3. **WhatsApp não envia mensagens**
   - Teste cada camada individualmente
   - Verifique números no formato internacional

4. **Erros de conexão Solana**
   - Confirme chave privada no formato Base58
   - Verifique saldo de SOL para taxas

### Debug

```bash
# Modo verbose
DEBUG=true python main.py

# Log detalhado
LOG_LEVEL=DEBUG python main.py
```

---

## 🔒 Segurança

### Boas Práticas

1. **NUNCA** commit chaves privadas
2. Use variáveis de ambiente em produção
3. Rotação regular de chaves de API
4. Backup offline das carteiras
5. Monitoramento de atividades suspeitas

### Carteiras

- Mantenha apenas saldo operacional na carteira quente
- Use multi-sig para grandes valores
- Monitore transações regularmente

---

## 📈 Monitoramento

### Métricas

- **Uptime**: `http://localhost:8080/api/v1/status`
- **Estatísticas**: `http://localhost:8080/api/v1/stats`
- **Health**: `http://localhost:8080/api/v1/health`

### Alertas Automáticos

- ✅ Bot Online/Offline
- 💸 Transações concluídas
- 🚨 Erros críticos
- 📊 Relatório diário (8:00 AM)

---

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é para fins educacionais e de pesquisa. Use por sua conta e risco.

**Aviso Legal**: Este software interage com redes blockchain reais e APIs de terceiros. O desenvolvedor não se responsabiliza por perdas financeiras ou problemas técnicos.

---

## 🙏 Créditos

- Arquitetura baseada no **Moltbook Crypto Bot**
- Integração com múltiplas APIs de IA
- Sistema de fallback WhatsApp inspirado em práticas de produção
- Comunidade open source

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/bernas-agent/issues)
- **Documentação**: Consulte os arquivos no diretório `docs/`
- **Comunidade**: Grupo Telegram/Discord (a ser criado)

---

**Última atualização**: 2026-05-16  
**Versão**: 1.0.0  
**Status**: 🟢 Operacional

> "Autonomia econômica entre IAs - O futuro da colaboração máquina-máquina" 🤖💸🧠