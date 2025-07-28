# 🚀 Guia Completo - Deploy Manual do GapHunter com Azure SQL Database

## 📋 **Visão Geral**

Este guia te levará passo a passo para criar toda a infraestrutura do GapHunter usando **Azure SQL Database** (gratuito/barato). Tempo estimado: **30-45 minutos**.

## 💰 **Recursos que Vamos Criar**

1. **Azure SQL Database** (GRATUITO ou ~$5/mês)
2. **App Service Plan** (~$13/mês ou GRATUITO)
3. **App Service** (Backend Python/FastAPI)
4. **Static Web App** (Frontend React - GRATUITO)

**Total estimado: $5-18/mês (ou GRATUITO para desenvolvimento)**

---

## 🗄️ **PASSO 1: Criar Azure SQL Database**

### **1.1 Acessar o Portal**
1. Acesse [portal.azure.com](https://portal.azure.com)
2. Faça login com sua conta Azure
3. No menu superior, clique em **"+ Create a resource"**

### **1.2 Buscar SQL Database**
1. Na barra de busca, digite: **"SQL Database"**
2. Clique em **"SQL Database"**
3. Clique em **"Create"**

### **1.3 Configurar SQL Database**

**Aba "Basics":**
- **Subscription**: Sua assinatura
- **Resource group**: `gaphunter-rg` (use existente ou crie novo)
- **Database name**: `gaphunter`
- **Server**: Clique **"Create new"**

### **1.4 Criar SQL Server**

**No popup "New server":**
- **Server name**: `gaphunter-sql-server` (deve ser único globalmente)
- **Location**: `East US` (ou sua região preferida)
- **Authentication method**: `Use SQL authentication`
- **Server admin login**: `gaphunter`
- **Password**: `SuaSenhaSegura123!` (anote esta senha!)
- **Confirm password**: `SuaSenhaSegura123!`
- Clique **"OK"**

### **1.5 Configurar Compute + Storage**

**Voltando à tela principal:**
- **Want to use SQL elastic pool?**: `No`
- **Compute + storage**: Clique **"Configure database"**

**Para GRATUITO (desenvolvimento):**
- **Service tier**: `Basic`
- **Compute tier**: `Serverless`
- **Max vCores**: `1`
- **Min vCores**: `0.5`
- **Data max size**: `2 GB`
- **Auto-pause delay**: `1 hour`

**Para PRODUÇÃO (baixo custo):**
- **Service tier**: `Basic`
- **Compute tier**: `Provisioned`
- **DTUs**: `5 DTUs`
- **Data max size**: `2 GB`

Clique **"Apply"**

### **1.6 Configurar Networking**
1. Clique na aba **"Networking"**
2. **Connectivity method**: `Public endpoint`
3. **Firewall rules**:
   - **Allow Azure services**: `Yes`
   - **Add current client IP**: `Yes`

### **1.7 Finalizar**
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
- **Resource group**: `gaphunter-rg` (mesmo do SQL)
- **Name**: `gaphunter-plan`
- **Operating System**: `Linux`
- **Region**: `East US` (mesma região do SQL)

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

### **4.2 Obter Connection String do SQL**
1. Vá para **"All resources"**
2. Clique em **"gaphunter"** (SQL Database)
3. No menu lateral, clique **"Connection strings"**
4. Copie a **ADO.NET** connection string
5. **Substitua** `{your_password}` por `SuaSenhaSegura123!`

**Exemplo da connection string:**
```
Server=tcp:gaphunter-sql-server.database.windows.net,1433;Initial Catalog=gaphunter;Persist Security Info=False;User ID=gaphunter;Password=SuaSenhaSegura123!;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;
```

### **4.3 Converter para SQLAlchemy URL**
Converta a connection string para formato SQLAlchemy:
```
mssql+pyodbc://gaphunter:SuaSenhaSegura123!@gaphunter-sql-server.database.windows.net:1433/gaphunter?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes
```

### **4.4 Configurar Variáveis de Ambiente**
1. No **gaphunter-backend** App Service
2. No menu lateral, clique **"Configuration"**
3. Na aba **"Application settings"**, clique **"+ New application setting"**

**Adicione estas configurações uma por uma:**

| Name | Value |
|------|-------|
| `DATABASE_URL` | `mssql+pyodbc://gaphunter:SuaSenhaSegura123!@gaphunter-sql-server.database.windows.net:1433/gaphunter?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes` |
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

### **4.5 Configurar Startup Command**
1. Ainda em **"Configuration"**
2. Na aba **"General settings"**
3. **Startup Command**: `python startup.py`
4. Clique **"Save"**

### **4.6 Configurar Deploy do GitHub**
1. No menu lateral, clique **"Deployment Center"**
2. **Source**: `GitHub`
3. Faça login no GitHub se solicitado
4. **Organization**: `wrodrigobr`
5. **Repository**: `gaphunter`
6. **Branch**: `master`
7. Clique **"Save"**

---

## 🎨 **PASSO 5: Criar Static Web App (Frontend)**

### **5.1 Criar Novo Recurso**
1. Clique **"+ Create a resource"**
2. Busque por: **"Static Web App"**
3. Clique em **"Static Web App"**
4. Clique **"Create"**

### **5.2 Configurar Static Web App**

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

### **5.3 Finalizar**
1. Clique **"Review + create"**
2. Clique **"Create"**
3. **⏱️ Aguarde 5-10 minutos** para deploy automático

---

## 🔄 **PASSO 6: Executar Migrações do Banco**

### **6.1 Aguardar Backend Ficar Online**
1. Vá para **"gaphunter-backend"** App Service
2. Clique **"Browse"** para abrir a URL
3. Aguarde até a aplicação carregar (pode demorar alguns minutos)

### **6.2 Executar Migrações**
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

## 🌐 **PASSO 7: Configurar Frontend para Conectar ao Backend**

### **7.1 Obter URL do Backend**
1. No App Service **"gaphunter-backend"**
2. Copie a **URL**: `https://gaphunter-backend.azurewebsites.net`

### **7.2 Configurar Static Web App**
1. Vá para **"gaphunter-frontend"** Static Web App
2. No menu lateral, clique **"Configuration"**
3. Clique **"+ Add"**
4. **Name**: `VITE_API_BASE_URL`
5. **Value**: `https://gaphunter-backend.azurewebsites.net/api`
6. Clique **"OK"**
7. Clique **"Save"**

---

## ✅ **PASSO 8: Testar a Aplicação**

### **8.1 URLs da Aplicação**
- **Frontend**: `https://gaphunter-frontend.azurestaticapps.net`
- **Backend**: `https://gaphunter-backend.azurewebsites.net`
- **API Docs**: `https://gaphunter-backend.azurewebsites.net/docs`

### **8.2 Testes Básicos**
1. **Acesse o frontend** e verifique se carrega
2. **Teste registro** de novo usuário
3. **Teste login** com usuário criado
4. **Acesse API docs** para ver endpoints disponíveis

---

## 🔧 **PASSO 9: Configurações Opcionais**

### **9.1 Configurar Firewall do SQL (Se necessário)**
1. Vá para **"gaphunter-sql-server"** (SQL Server)
2. No menu lateral, clique **"Networking"**
3. Em **"Firewall rules"**, adicione:
   - **Rule name**: `AllowAppService`
   - **Start IP**: `0.0.0.0`
   - **End IP**: `0.0.0.0`
4. Clique **"Save"**

### **9.2 Monitoramento (Opcional)**
1. No App Service, vá em **"Application Insights"**
2. Clique **"Turn on Application Insights"**
3. Configure monitoramento

---

## 📊 **Resumo dos Recursos Criados**

| Recurso | Nome | Tipo | Custo/Mês |
|---------|------|------|-----------|
| Database | `gaphunter` | Azure SQL Basic | GRATUITO-$5 |
| SQL Server | `gaphunter-sql-server` | SQL Server | Incluído |
| App Plan | `gaphunter-plan` | B1 Basic/F1 Free | $13/GRATUITO |
| Backend | `gaphunter-backend` | App Service | Incluído no plano |
| Frontend | `gaphunter-frontend` | Static Web App | GRATUITO |
| **TOTAL** | | | **$5-18/mês** |

---

## 💡 **Opções de Custo Azure SQL**

### **Desenvolvimento (GRATUITO):**
- **Basic Serverless**: 0.5-1 vCore, 2GB
- **Auto-pause**: 1 hora de inatividade
- **Custo**: GRATUITO quando pausado

### **Produção Básica (~$5/mês):**
- **Basic DTU**: 5 DTUs, 2GB
- **Always-on**: Sem pausa automática
- **Custo**: ~$5/mês

### **Produção Avançada (~$15/mês):**
- **Standard S0**: 10 DTUs, 250GB
- **Backup automático**: 7 dias
- **Custo**: ~$15/mês

---

## 🆘 **Troubleshooting**

### **Backend não conecta ao SQL:**
1. Verifique connection string no App Service
2. Confirme firewall rules do SQL Server
3. Teste conexão manual via SQL Server Management Studio

### **Erro de driver ODBC:**
1. Verifique se `pyodbc` está em requirements-prod.txt
2. Confirme que o driver está especificado na connection string
3. Aguarde build completo do App Service

### **Frontend não carrega:**
1. Verifique build logs no GitHub Actions
2. Confirme configuração da API URL
3. Verifique CORS no backend

---

## 🎉 **Parabéns!**

Sua plataforma GapHunter está agora rodando no Azure com:
- ✅ **Azure SQL Database** (gratuito ou baixo custo)
- ✅ Backend FastAPI funcionando
- ✅ Frontend React responsivo
- ✅ Deploy automático via GitHub
- ✅ SSL/HTTPS habilitado
- ✅ Monitoramento disponível

**URLs finais:**
- **App**: https://gaphunter-frontend.azurestaticapps.net
- **API**: https://gaphunter-backend.azurewebsites.net/docs

## 🔑 **Credenciais para Salvar**

- **SQL Server**: `gaphunter-sql-server.database.windows.net`
- **Database**: `gaphunter`
- **Username**: `gaphunter`
- **Password**: `SuaSenhaSegura123!`
- **Connection String**: (salve a que você configurou)

---

## 💰 **Vantagens do Azure SQL vs PostgreSQL**

✅ **Custo**: Opção gratuita disponível  
✅ **Familiaridade**: Sintaxe SQL Server conhecida  
✅ **Integração**: Nativa com Azure  
✅ **Ferramentas**: SQL Server Management Studio  
✅ **Backup**: Automático e point-in-time recovery  
✅ **Escalabilidade**: Fácil upgrade de tier

