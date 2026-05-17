# Guia de Mensagens do Discord - BERNAS-DA-SAL

## 📱 Como Enviar Mensagens para Qualquer Pessoa

### 1. Via Comandos no Discord (Fácil)

#### Comandos Disponíveis:

**Para encontrar usuários:**
```
!finduser nome_do_usuario
```
Exemplo: `!finduser carlos` - Encontra todos os usuários com "carlos" no nome

**Para enviar mensagem direta (apenas você):**
```
!dm ID_DO_USUARIO sua mensagem aqui
```
Exemplo: `!dm 123456789012345678 Olá, como vai?`

**Para fazer anúncio em todos os servidores (apenas você):**
```
!broadcast mensagem de anuncio
```
Exemplo: `!broadcast Novo serviço disponível! Use !services para ver`

### 2. Via API HTTP (Avançado)

#### Endpoints Disponíveis:

**Encontrar usuário:**
```
GET https://bernas-agent.onrender.com/api/v1/discord/find_user?username=nome&auth_token=bernassecret
```

**Enviar mensagem direta:**
```
POST https://bernas-agent.onrender.com/api/v1/discord/send_dm
Content-Type: application/json

{
  "user_id": "123456789012345678",
  "message": "Sua mensagem aqui",
  "auth_token": "bernassecret"
}
```

**Estatísticas do bot:**
```
GET https://bernas-agent.onrender.com/api/v1/discord/stats?auth_token=bernassecret
```

**Broadcast para todos os servidores:**
```
POST https://bernas-agent.onrender.com/api/v1/discord/broadcast
Content-Type: application/json

{
  "message": "Mensagem de anuncio",
  "auth_token": "bernassecret"
}
```

### 3. Como Obter IDs de Usuários

#### Método 1: Usando o Discord
1. Ative o **Modo Desenvolvedor** no Discord:
   - Configurações → Avançado → Modo Desenvolvedor (ativar)
2. Clique com o botão direito em qualquer usuário → Copiar ID

#### Método 2: Usando o comando `!finduser`
```
!finduser nome_do_usuario
```
O comando retornará o ID do usuário junto com o nome.

### 4. Exemplos Práticos

#### Exemplo 1: Encontrar e enviar mensagem para um amigo
```
!finduser joao
# Resultado: João Silva (123456789012345678) - Servidor do BERNAS

!dm 123456789012345678 Eae João, tudo bem? O bot está funcionando!
```

#### Exemplo 2: Fazer anúncio importante
```
!broadcast 🚀 NOVO RECURSO: Agora você pode comprar serviços com !buy! Confira !services
```

#### Exemplo 3: Usando a API (com curl)
```bash
# Encontrar usuário
curl "https://bernas-agent.onrender.com/api/v1/discord/find_user?username=carlos&auth_token=bernassecret"

# Enviar mensagem
curl -X POST https://bernas-agent.onrender.com/api/v1/discord/send_dm \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123456789012345678", "message": "Teste via API", "auth_token": "bernassecret"}'
```

### 5. Segurança

- **Token de autenticação:** `bernassecret` (padrão)
- **Apenas você** pode usar os comandos `!dm` e `!broadcast`
- **Configure um token personalizado** no Render.com:
  ```
  API_AUTH_TOKEN=seu_token_secreto_aqui
  ```

### 6. Solução de Problemas

#### O bot não responde aos comandos:
1. Verifique se o bot está online no servidor
2. Confirme que você tem permissões adequadas
3. Use `!status` para verificar o status do bot

#### Comando `!dm` não funciona:
1. Verifique se o ID do usuário está correto
2. O usuário pode ter DMs (mensagens diretas) desativadas
3. O bot precisa estar no mesmo servidor que o usuário

#### API retorna erro:
1. Verifique se o token de autenticação está correto
2. Confirme que o bot está rodando (health check)
3. Verifique os logs no Render.com

### 7. Dicas Avançadas

#### Automatizar mensagens:
```python
import requests
import time

def send_automated_message(user_id, message):
    url = "https://bernas-agent.onrender.com/api/v1/discord/send_dm"
    data = {
        "user_id": user_id,
        "message": message,
        "auth_token": "bernassecret"
    }
    response = requests.post(url, json=data)
    return response.json()

# Enviar mensagem para múltiplos usuários
users = ["123456789012345678", "987654321098765432"]
for user_id in users:
    send_automated_message(user_id, "Mensagem automática!")
    time.sleep(1)  # Esperar 1 segundo entre mensagens
```

#### Monitorar respostas:
O bot não tem sistema de respostas automáticas para DMs enviadas por você, mas você pode:
1. Pedir para as pessoas responderem no servidor
2. Configurar um canal específico para respostas
3. Usar `!chat` para conversar com a IA do bot

---

**Última atualização:** 2026-05-17  
**Status:** ✅ Funcional - Pronto para uso