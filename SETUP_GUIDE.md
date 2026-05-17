# 🚀 GUIA DE CONFIGURAÇÃO COMPLETA - BERNAS-AGENT

**Data:** 2026-05-17  
**Status:** ✅ BOT FUNCIONANDO LOCALMENTE

---

## 📋 RESUMO DO STATUS

✅ **BOT RODANDO LOCALMENTE** - Testado e funcionando  
✅ **API HTTP ATIVA** - Porta 8080 respondendo  
✅ **ECONOMIA ATIVA** - Servidor HTTP 402 na porta 4020  
✅ **ESTRUTURA COMPLETA** - Todos os módulos implementados  
⚠️ **CHAVES DE API** - Aguardando configuração  
⚠️ **SQUARE CLOUD** - Pronto para deploy

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

### 1. **CONFIGURAR CHAVES DE API** (CRÍTICO)

Edite o arquivo `.env` com suas chaves reais:

```bash
cd C:\Users\Carlos\bernas-agent
notepad .env
```

**MÍNIMO NECESSÁRIO:**
```env
# Pelo menos UMA API de IA
GEMINI_API_KEY=sua_chave_aqui

# Carteira Solana (para testes, pode ser simulada)
SOLANA_PRIVATE_KEY=sua_chave_privada_base58

# WhatsApp para alertas
ALERT_CONTACTS=+5511999999999
```

### 2. **OBTER CHAVES DE API**

#### IA APIs (Escolha pelo menos uma):
- **Gemini**: https://makersuite.google.com/app/apikey
- **OpenClaude**: https://openclaude.ai
- **OpenRouter**: https://openrouter.ai/keys
- **NVIDIA**: https://build.nvidia.com/

#### WhatsApp:
- **CallMeBot**: https://www.callmebot.com/blog/free-api-whatsapp-messages/
- **Twilio** (opcional): https://www.twilio.com/whatsapp

#### Solana:
- Crie carteira: https://solflare.com
- Obtenha USDC de teste: https://spl-token-faucet.com

### 3. **TESTAR COM CHAVES REAIS**

```bash
# Parar bot atual (Ctrl+C no terminal)
# Editar .env com chaves reais
# Reiniciar bot
python main.py
```

O bot deve:
- ✅ Inicializar todos os componentes
- 📱 Enviar "Bot Online" para WhatsApp
- 🌐 Responder na porta 8080

---

## 🚀 DEPLOY NO SQUARE CLOUD (24/7)

### Pré-requisitos:
1. Conta em https://squarecloud.app
2. Square CLI instalado

### Passo a passo:

```bash
# 1. Instalar Square CLI
npm install -g @squarecloud/cli
# ou
curl -fsSL https://squarecloud.app/install.sh | sh

# 2. Login
square login

# 3. Fazer deploy
python scripts\deploy_squarecloud.py
```

### Configurar variáveis no Square Cloud:
1. Acesse https://squarecloud.app/dashboard
2. Vá em "Environment Variables"
3. Adicione as mesmas variáveis do seu `.env`

---

## 🧪 TESTES E VERIFICAÇÕES

### API Endpoints (localhost:8080):

```bash
# Status do bot
curl http://localhost:8080/api/v1/status

# Health check
curl http://localhost:8080/api/v1/health

# Estatísticas
curl http://localhost:8080/api/v1/stats

# Testar IA (com API configurada)
curl -X POST http://localhost:8080/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Olá, como vai o bot?"}'
```

### Marketplace (localhost:4020):

```bash
# Listar serviços
curl http://localhost:4020/api/v1/services

# Ver carteira de exemplo
curl http://localhost:4020/api/v1/wallet/agent_alpha
```

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### Problemas Comuns:

1. **"API key não configurada"**
   - Verifique se `.env` está no diretório correto
   - Confirme nomes das variáveis

2. **WhatsApp não envia**
   - Teste CallMeBot manualmente primeiro
   - Verifique formato do número (+55DDDNúmero)

3. **Erros de porta**
   - Verifique se portas 8080 e 4020 estão livres
   - Altere no `.env` se necessário

4. **Bot não inicia**
   ```bash
   # Debug detalhado
   DEBUG=true python main.py
   
   # Ver logs
   type logs\bernas_agent.log
   ```

### Logs:
```bash
# Monitorar logs em tempo real
Get-Content -Path "logs\bernas_agent.log" -Wait -Encoding UTF8
```

---

## 📊 MONITORAMENTO EM PRODUÇÃO

### Métricas a monitorar:
- ✅ Uptime do bot
- 📈 Transações por hora
- 💰 Saldo das carteiras
- 🤖 Requisições de IA
- 📱 Mensagens WhatsApp

### Alertas automáticos:
- Bot Online/Offline
- Erros críticos
- Transações acima de limite
- Quota de API atingida

---

## 🔒 SEGURANÇA

### CRÍTICO - NUNCA FAÇA:
- ❌ Commit arquivos `.env` com chaves reais
- ❌ Compartilhar chaves privadas
- ❌ Usar mesma senha em múltiplos serviços
- ❌ Deixar bot sem monitoramento

### RECOMENDADO:
- ✅ Use variáveis de ambiente
- ✅ Backup regular das carteiras
- ✅ Rotação periódica de chaves
- ✅ 2FA em todas as contas

---

## 📞 SUPORTE

### Em caso de problemas:

1. **Verifique logs**: `logs\bernas_agent.log`
2. **Teste APIs individualmente**
3. **Consulte este guia**
4. **Contate suporte das APIs**

### Recursos:
- Documentação: `README.md`
- Configuração: `.env.example`
- Scripts: `scripts\`
- Código fonte: `src\`

---

## 🎉 PARABÉNS!

Seu bot **BERNAS-AGENT** está:

✅ **Implementado** - Código completo  
✅ **Testado** - Funcionando localmente  
✅ **Documentado** - Guias e instruções  
✅ **Pronto para produção** - Square Cloud configurado

**Próximas ações:**
1. Configure pelo menos UMA API de IA
2. Teste com chaves reais
3. Faça deploy no Square Cloud
4. Monitore os primeiros dias

---

**Última atualização:** 2026-05-17  
**Bot Status:** 🟢 OPERACIONAL (modo simulação)  
**Próxima etapa:** Configurar chaves reais

> "A economia autônoma entre IAs começa aqui" 🤖💸🚀