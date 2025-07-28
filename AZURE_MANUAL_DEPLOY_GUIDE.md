# 🚀 Guia Completo - Deploy Manual do GapHunter no Azure Portal

## 📋 **Visão Geral**

Este guia te levará passo a passo para criar toda a infraestrutura do GapHunter manualmente no Azure Portal. Tempo estimado: **30-45 minutos**.

## 💰 **Recursos que Vamos Criar**

1. **Azure Database for PostgreSQL** (~$12/mês)
2. **App Service Plan** (~$13/mês ou GRATUITO)
3. **App Service** (Backend Python/FastAPI)
4. **Static Web App** (Frontend React - GRATUITO)

**Total estimado: $25/mês (ou $12/mês com plano gratuito)**

---

## 🗄️ **PASSO 1: Criar Azure Database for PostgreSQL**

### **1.1 Acessar o Portal**
1. Acesse [portal.azure.com](https://portal.azure.com)
2. Faça login com sua conta Azure
3. No menu superior, clique em **"+ Create a resource"**

### **1.2 Buscar PostgreSQL**
1. Na barra de busca, digite: **"Azure Database for PostgreSQL"**
2. Clique em **"Azure Database for PostgreSQL flexible server"**
3. Clique em **"Create"**

### **1.3 Configurar Servidor PostgreSQL**

**Aba "Basics":**
- **Subscription**: Sua assinatura
- **Resource group**: `gaphunter-rg` (use existente ou crie novo)
- **Server name**: `gaphunter-postgres` (deve ser único globalmente)
- **Region**: `East US` (ou sua região preferida)
- **PostgreSQL version**: `14`
- **Workload type**: `Development`

**Authentication:**
- **Authentication method**: `PostgreSQL authentication only`
- **Admin username**: `gaphunter`
- **Password**: `SuaSenhaSegura123!` (anote esta senha!)
- **Confirm password**: `SuaSenhaSegura123!`

### **1.4 Configurar Compute + Storage**
1. Clique em **"Configure server"**
2. **Compute tier**: `Burstable`
3. **Compute size**: `Standard_B1ms (1 vCore, 2 GiB RAM)`
4. **Storage size**: `32 GiB`
5. **Storage type**: `Premium SSD`
6. Clique **"Save"**

### **1.5 Configurar Networking**
1. **Connectivity method**: `Public access (allowed IP addresses)`
2. **Firewall rules**: 
   - Marque ✅ **"Allow public access from any Azure service within Azure"**
   - Marque ✅ **"Add current client IP address"**

### **1.6 Finalizar**
1. Clique **"Review + create"**
2. Revise as configurações
3. Clique **"Create"**
4. **⏱️ Aguarde 5-10 minutos** para criação

---

## 📊 **PASSO 2: Criar App Service Plan**

### **2.1 Criar Novo Recurso**
1. No portal, clique **"+ Create a resource"**
2. Busque por: **"App Service Plan"**
3. Clique em **"App Service Plan"**
4. Clique **"Create"**

### **2.2 Configurar App Service Plan**

**Basics:**
- **Subscription**: Sua assinatura
- **Resource group**: `gaphunter-rg` (mesmo do PostgreSQL)
- **Name**: `gaphunter-plan`
- **Operating System**: `Linux`
- **Region**: `East US` (mesma região do PostgreSQL)

**Pricing Tier:**
1. Clique **"Change size"**
2. **Para produção**: Selecione `B1 Basic` (~$13/mês)
3. **Para testes**: Selecione `F1 Free` (GRATUITO, limitações)
4. Clique **"Apply"**

### **2.3 Finalizar**
1. Clique **"Review + create"**
2. Clique **"Create"**
3. **⏱️ Aguarde 2-3 minutos**

---

## ⚙️ **PASSO 3: Criar App Service (Backend)**

### **3.1 Criar Novo Recurso**
1. Clique **"+ Create a resource"**
2. Busque por: **"Web App"**
3. Clique em **"Web App"**
4. Clique **"Create"**

### **3.2 Configurar Web App**

**Basics:**
- **Subscription**: Sua assinatura
- **Resource group**: `gaphunter-rg`
- **Name**: `gaphunter-backend` (deve ser único globalmente)
- **Publish**: `Code`
- **Runtime stack**: `Python 3.11`
- **Operating System**: `Linux`
- **Region**: `East US`

**App Service Plan:**
- **Linux Plan**: Selecione `gaphunter-plan` (criado no passo anterior)

### **3.3 Finalizar**
1. Clique **"Review + create"**
2. Clique **"Create"**
3. **⏱️ Aguarde 3-5 minutos**

---

## 🔧 **PASSO 4: Configurar Backend App Service**

### **4.1 Acessar App Service**
1. Vá para **"All resources"**
2. Clique em **"gaphunter-backend"**

### **4.2 Configurar Variáveis de Ambiente**
1. No menu lateral, clique **"Configuration"**
2. Na aba **"Application settings"**, clique **"+ New application setting"**

**Adicione estas configurações uma por uma:**

| Name | Value |
|------|-------|
| `DATABASE_URL` | `postgresql://gaphunter:SuaSenhaSegura123!@gaphunter-postgres.postgres.database.azure.com:5432/gaphunter` |
| `SECRET_KEY` | `sua-chave-secreta-jwt-aqui` |
| `OPENROUTER_API_KEY` | `sk-or-v1-sua-chave-openrouter` |
| `ENVIRONMENT` | `production` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |
| `ENABLE_ORYX_BUILD` | `true` |

**Para gerar SECRET_KEY:**
```bash
# No seu computador local:
openssl rand -base64 32
```

### **4.3 Configurar Startup Command**
1. Ainda em **"Configuration"**
2. Na aba **"General settings"**
3. **Startup Command**: `python startup.py`
4. Clique **"Save"**

### **4.4 Configurar Deploy do GitHub**
1. No menu lateral, clique **"Deployment Center"**
2. **Source**: `GitHub`
3. Faça login no GitHub se solicitado
4. **Organization**: `wrodrigobr`
5. **Repository**: `gaphunter`
6. **Branch**: `master`
7. Clique **"Save"**

---

## 🗄️ **PASSO 5: Criar Database no PostgreSQL**

### **5.1 Acessar PostgreSQL**
1. Vá para **"All resources"**
2. Clique em **"gaphunter-postgres"**

### **5.2 Criar Database**
1. No menu lateral, clique **"Databases"**
2. Clique **"+ Add"**
3. **Database name**: `gaphunter`
4. Clique **"Save"**

### **5.3 Testar Conexão (Opcional)**
1. No menu lateral, clique **"Connect"**
2. Use as credenciais:
   - **Server**: `gaphunter-postgres.postgres.database.azure.com`
   - **Username**: `gaphunter`
   - **Password**: `SuaSenhaSegura123!`
   - **Database**: `gaphunter`

---

## 🎨 **PASSO 6: Criar Static Web App (Frontend)**

### **6.1 Criar Novo Recurso**
1. Clique **"+ Create a resource"**
2. Busque por: **"Static Web App"**
3. Clique em **"Static Web App"**
4. Clique **"Create"**

### **6.2 Configurar Static Web App**

**Basics:**
- **Subscription**: Sua assinatura
- **Resource group**: `gaphunter-rg`
- **Name**: `gaphunter-frontend`
- **Plan type**: `Free`
- **Region**: `East US 2` (ou disponível)

**Deployment details:**
- **Source**: `GitHub`
- Faça login no GitHub
- **Organization**: `wrodrigobr`
- **Repository**: `gaphunter`
- **Branch**: `master`

**Build Details:**
- **Build Presets**: `React`
- **App location**: `/frontend`
- **Api location**: (deixe vazio)
- **Output location**: `dist`

### **6.3 Finalizar**
1. Clique **"Review + create"**
2. Clique **"Create"**
3. **⏱️ Aguarde 5-10 minutos** para deploy automático

---

## 🔄 **PASSO 7: Executar Migrações do Banco**

### **7.1 Aguardar Backend Ficar Online**
1. Vá para **"gaphunter-backend"** App Service
2. Clique **"Browse"** para abrir a URL
3. Aguarde até a aplicação carregar (pode demorar alguns minutos)

### **7.2 Executar Migrações**
1. Acesse: `https://gaphunter-backend.azurewebsites.net/docs`
2. Procure pelo endpoint **"/admin/migrate"**
3. Clique **"Try it out"**
4. Clique **"Execute"**
5. Verifique se retorna sucesso

**Ou via curl:**
```bash
curl -X POST https://gaphunter-backend.azurewebsites.net/admin/migrate
```

---

## 🌐 **PASSO 8: Configurar Frontend para Conectar ao Backend**

### **8.1 Obter URL do Backend**
1. No App Service **"gaphunter-backend"**
2. Copie a **URL**: `https://gaphunter-backend.azurewebsites.net`

### **8.2 Configurar Static Web App**
1. Vá para **"gaphunter-frontend"** Static Web App
2. No menu lateral, clique **"Configuration"**
3. Clique **"+ Add"**
4. **Name**: `VITE_API_BASE_URL`
5. **Value**: `https://gaphunter-backend.azurewebsites.net/api`
6. Clique **"OK"**
7. Clique **"Save"**

---

## ✅ **PASSO 9: Testar a Aplicação**

### **9.1 URLs da Aplicação**
- **Frontend**: `https://gaphunter-frontend.azurestaticapps.net`
- **Backend**: `https://gaphunter-backend.azurewebsites.net`
- **API Docs**: `https://gaphunter-backend.azurewebsites.net/docs`

### **9.2 Testes Básicos**
1. **Acesse o frontend** e verifique se carrega
2. **Teste registro** de novo usuário
3. **Teste login** com usuário criado
4. **Acesse API docs** para ver endpoints disponíveis

---

## 🔧 **PASSO 10: Configurações Opcionais**

### **10.1 Domínio Personalizado (Opcional)**
1. No App Service, vá em **"Custom domains"**
2. Clique **"+ Add custom domain"**
3. Configure seu domínio

### **10.2 SSL Certificate (Automático)**
- SSL é automático para domínios `.azurewebsites.net`
- Para domínios personalizados, configure certificado

### **10.3 Application Insights (Monitoramento)**
1. No App Service, vá em **"Application Insights"**
2. Clique **"Turn on Application Insights"**
3. Configure monitoramento

---

## 📊 **Resumo dos Recursos Criados**

| Recurso | Nome | Tipo | Custo/Mês |
|---------|------|------|-----------|
| Database | `gaphunter-postgres` | PostgreSQL B1ms | ~$12 |
| App Plan | `gaphunter-plan` | B1 Basic | ~$13 |
| Backend | `gaphunter-backend` | App Service | Incluído no plano |
| Frontend | `gaphunter-frontend` | Static Web App | GRATUITO |
| **TOTAL** | | | **~$25/mês** |

---

## 🆘 **Troubleshooting**

### **Backend não inicia:**
1. Verifique logs em **"Log stream"**
2. Confirme variáveis de ambiente
3. Verifique startup command

### **Banco não conecta:**
1. Verifique firewall rules do PostgreSQL
2. Confirme string de conexão
3. Teste conexão manual

### **Frontend não carrega:**
1. Verifique build logs no GitHub Actions
2. Confirme configuração da API URL
3. Verifique CORS no backend

---

## 🎉 **Parabéns!**

Sua plataforma GapHunter está agora rodando no Azure com:
- ✅ Backend FastAPI funcionando
- ✅ Frontend React responsivo
- ✅ Banco PostgreSQL configurado
- ✅ Deploy automático via GitHub
- ✅ SSL/HTTPS habilitado
- ✅ Monitoramento disponível

**URLs finais:**
- **App**: https://gaphunter-frontend.azurestaticapps.net
- **API**: https://gaphunter-backend.azurewebsites.net/docs

