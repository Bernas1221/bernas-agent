# Guia de Configuração do Discord Bot - BERNAS-DA-SAL

## Status Atual
- ✅ Token do Discord: **CONFIGURADO** (72 caracteres, formato correto)
- ❌ Bot offline: **INTENTS PRIVILEGIADOS NÃO ATIVADOS**
- ✅ Render.com: **ONLINE** (https://bernas-agent.onrender.com)
- ✅ Código: **ATUALIZADO** (correções de encoding e comandos)

## Problema Identificado
O bot está solicitando intents privilegiados que não foram ativados no portal do Discord Developer.

## Passos para Resolver

### 1. Ativar Intents no Discord Developer Portal
1. Acesse: https://discord.com/developers/applications
2. Faça login com sua conta do Discord
3. Selecione o aplicativo "BERNAS-DA-SAL" (ID: 1505474529257066506)
4. No menu lateral, clique em **"Bot"**
5. Na seção **"Privileged Gateway Intents"**, ative:
   - ✅ **MESSAGE CONTENT INTENT** (OBRIGATÓRIO)
   - ✅ **SERVER MEMBERS INTENT** (RECOMENDADO)
   - ❌ PRESENCE INTENT (opcional, pode deixar desativado)
6. Clique em **"Save Changes"**

### 2. Verificar Token no Render.com
1. Acesse: https://dashboard.render.com
2. Vá para seu serviço "bernas-agent"
3. Clique em **"Environment"**
4. Verifique se a variável `DISCORD_BOT_TOKEN` está configurada com seu token
   - O token deve ter aproximadamente 72 caracteres
   - Deve começar com "MTUw"

### 3. Forçar Novo Deploy
1. No Render.com, vá para seu serviço "bernas-agent"
2. Clique em **"Manual Deploy"** (canto superior direito)
3. Selecione **"Deploy latest commit"**
4. Aguarde 2-3 minutos para o deploy completar

### 4. Testar o Bot
1. Adicione o bot ao seu servidor usando este link:
   ```
   https://discord.com/oauth2/authorize?client_id=1505474529257066506&permissions=8&integration_type=0&scope=bot
   ```
2. No Discord, use os comandos:
   - `!chat Olá, como vai?` - Conversa com a IA
   - `!economy` - Estatísticas da economia
   - `!services` - Lista serviços disponíveis
   - `!status` - Status do bot
   - `!bothelp` - Ajuda completa

## Verificação de Status
Após seguir os passos acima, verifique se o bot está online:

1. **Endpoint de status:** https://bernas-agent.onrender.com/api/v1/status
2. **No Discord:** O bot deve aparecer como "Online" na lista de membros
3. **Comandos:** Devem responder normalmente

## Solução de Problemas

### Se o bot ainda estiver offline:
1. **Verifique os logs do Render.com:**
   - Vá para "Logs" no dashboard do Render.com
   - Procure por erros relacionados ao Discord

2. **Teste o token localmente:**
   ```bash
   python test_discord.py
   ```

3. **Verifique se o bot foi adicionado ao servidor:**
   - Use o link de convite acima
   - Confirme que tem permissões de administrador no servidor

### Se os comandos não funcionarem:
1. **Verifique intents:** Confirme que "Message Content Intent" está ativado
2. **Reinicie o bot:** Force um novo deploy no Render.com
3. **Aguarde:** Pode levar 1-2 minutos para o bot reconectar

## Links Úteis
- **Dashboard:** https://bernas-agent.onrender.com/dashboard
- **Health Check:** https://bernas-agent.onrender.com/api/v1/health
- **GitHub:** https://github.com/Bernas1221/bernas-agent
- **Discord Developer Portal:** https://discord.com/developers/applications/1505474529257066506/bot

## Suporte
Se ainda tiver problemas após seguir este guia:
1. Verifique os logs detalhados no Render.com
2. Teste o token com o script `test_discord_endpoint.py`
3. Entre em contato para mais assistência

---

**Última atualização:** 2026-05-17  
**Status:** Aguardando ativação de intents privilegiados