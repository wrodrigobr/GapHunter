# 🚀 Guia de Deploy - GapHunter no Azure App Service

## 📋 **Visão Geral**

Este guia mostra como fazer deploy da plataforma GapHunter no Azure usando **App Service**, a opção mais econômica e simples para MVPs.

## 💰 **Custos Estimados**

- **Azure Database for PostgreSQL**: B1ms (~$12/mês)
- **App Service Plan**: B1 Basic (~$13/mês)
- **Static Web App**: GRATUITO
- **Total**: ~$25/mês

## 🎯 **Opções de Deploy**

### **Opção 1: Deploy Automático (GitHub Actions)**
✅ **Recomendado** - Deploy automático a cada push

### **Opção 2: Deploy Manual (Script)**
⚙️ Para deploy único ou troubleshooting

## 🚀 **Deploy Automático (GitHub Actions)**

### **Pré-requisitos**
1. Conta no Azure com assinatura ativa
2. Azure CLI instalado localmente
3. Repositório GitHub (já configurado)

### **Passo 1: Configurar Credenciais Azure**

```bash
# 1. Fazer login no Azure
az login

# 2. Criar Service Principal
az ad sp create-for-rbac \
  --name "gaphunter-deploy" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
  --sdk-auth
```

**Copie todo o JSON retornado!**

### **Passo 2: Configurar Secrets no GitHub**

Acesse: `Settings > Secrets and variables > Actions > New repository secret`

Adicione os seguintes secrets:

1. **AZURE_CREDENTIALS**
   ```json
   {
     "clientId": "xxx",
     "clientSecret": "xxx",
     "subscriptionId": "xxx",
     "tenantId": "xxx"
   }
   ```

2. **DB_ADMIN_PASSWORD**
   ```
   SuaSenhaSeguraDoPostgreSQL123!
   ```

3. **SECRET_KEY**
   ```bash
   # Gerar chave segura:
   openssl rand -base64 32
   ```

4. **OPENROUTER_API_KEY**
   ```
   sk-or-v1-xxxxx
   ```

### **Passo 3: Executar Deploy**

1. Faça qualquer push no repositório
2. Acesse `Actions` no GitHub
3. Acompanhe o progresso do deploy
4. URLs serão exibidas no final

## ⚙️ **Deploy Manual (Script)**

### **Pré-requisitos**
```bash
# Instalar Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Fazer login
az login
```

### **Configurar Variáveis**
```bash
export DB_ADMIN_PASSWORD="SuaSenhaSegura123!"
export SECRET_KEY="$(openssl rand -base64 32)"
export OPENROUTER_API_KEY="sk-or-v1-xxxxx"
```

### **Executar Deploy**
```bash
chmod +x deploy-azure.sh
./deploy-azure.sh
```

## 🔧 **Configurações Pós-Deploy**

### **1. Verificar Aplicação**
- Frontend: Acesse a URL do Static Web App
- Backend: Acesse `/docs` para ver a API
- Banco: Teste login/registro

### **2. Configurar Domínio Personalizado (Opcional)**
```bash
# Para o backend
az webapp config hostname add \
  --webapp-name gaphunter-backend \
  --resource-group gaphunter-rg \
  --hostname api.seudominio.com

# Para o frontend (via portal Azure)
```

### **3. Configurar SSL (Automático)**
- App Service: SSL automático com domínio personalizado
- Static Web App: SSL sempre ativo

### **4. Monitoramento**
```bash
# Habilitar Application Insights
az webapp config appsettings set \
  --resource-group gaphunter-rg \
  --name gaphunter-backend \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="xxx"
```

## 🛠️ **Troubleshooting**

### **Problema: Backend não inicia**
```bash
# Verificar logs
az webapp log tail \
  --resource-group gaphunter-rg \
  --name gaphunter-backend
```

### **Problema: Banco não conecta**
```bash
# Testar conexão
az postgres flexible-server connect \
  --name gaphunter-postgres \
  --admin-user gaphunter \
  --admin-password "SuaSenha"
```

### **Problema: Migrações não executam**
```bash
# Executar manualmente
curl -X POST https://gaphunter-backend.azurewebsites.net/admin/migrate
```

## 📊 **Monitoramento e Logs**

### **Logs do Backend**
```bash
az webapp log tail --name gaphunter-backend --resource-group gaphunter-rg
```

### **Métricas do Banco**
```bash
az postgres flexible-server show \
  --name gaphunter-postgres \
  --resource-group gaphunter-rg
```

### **Status dos Serviços**
```bash
# Backend
curl https://gaphunter-backend.azurewebsites.net/health

# Frontend
curl https://gaphunter-frontend-static.azurestaticapps.net
```

## 🔄 **Atualizações**

### **Automáticas (GitHub Actions)**
- Qualquer push no repositório dispara deploy automático
- Zero configuração adicional necessária

### **Manuais**
```bash
# Re-executar script
./deploy-azure.sh

# Ou fazer push no GitHub
git push origin master
```

## 💡 **Dicas de Otimização**

### **Reduzir Custos**
1. **Usar Always On apenas em produção**
2. **Configurar auto-scaling baseado em CPU**
3. **Usar PostgreSQL Burstable para desenvolvimento**

### **Melhorar Performance**
1. **Habilitar CDN no Static Web App**
2. **Configurar cache no App Service**
3. **Usar Application Insights para monitoramento**

## 🆘 **Suporte**

### **Logs Importantes**
- Backend: Azure App Service Logs
- Frontend: Static Web App Logs
- Banco: PostgreSQL Logs

### **Comandos Úteis**
```bash
# Restart do backend
az webapp restart --name gaphunter-backend --resource-group gaphunter-rg

# Verificar configurações
az webapp config appsettings list --name gaphunter-backend --resource-group gaphunter-rg

# Backup do banco
az postgres flexible-server backup list --name gaphunter-postgres --resource-group gaphunter-rg
```

---

**🎉 Sua plataforma GapHunter está pronta para produção com App Service!**

