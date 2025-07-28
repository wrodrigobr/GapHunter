# 🚀 Guia de Deploy - GapHunter no Azure

Este documento fornece instruções completas para fazer o deploy da plataforma GapHunter no Microsoft Azure usando Container Apps e banco de dados PostgreSQL.

## 📋 Pré-requisitos

### 1. Ferramentas Necessárias
- **Azure CLI** (versão 2.40+)
- **Docker** (para builds locais opcionais)
- **Git** (para versionamento)
- **OpenSSL** (para geração de chaves)

### 2. Contas e Credenciais
- **Conta Azure** com permissões de administrador
- **Chave da API OpenRouter** para funcionalidades de IA
- **Domínio personalizado** (opcional)

### 3. Instalação do Azure CLI

```bash
# Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# macOS
brew install azure-cli

# Windows
# Baixar de: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
```

## 🏗️ Arquitetura da Solução

### Componentes Azure
- **Azure Container Apps**: Hospedagem de frontend e backend
- **Azure Database for PostgreSQL**: Banco de dados principal
- **Azure Container Registry**: Armazenamento de imagens Docker
- **Azure Log Analytics**: Monitoramento e logs

### Estrutura da Aplicação
```
gaphunter/
├── backend/                 # API FastAPI
│   ├── app/                # Código da aplicação
│   ├── alembic/            # Migrações do banco
│   ├── Dockerfile          # Imagem Docker
│   ├── requirements-prod.txt
│   └── startup.py          # Script de inicialização
├── frontend/               # Interface React
│   ├── src/                # Código fonte
│   ├── dist/               # Build de produção
│   ├── Dockerfile          # Imagem Docker
│   └── nginx.conf          # Configuração do servidor
├── docker-compose.yml      # Orquestração local
├── azure-deploy.yml        # Configuração Azure
└── deploy-azure.sh         # Script de deploy
```

## 🔧 Configuração Inicial

### 1. Preparar Variáveis de Ambiente

Crie um arquivo `.env.deploy` com suas configurações:

```bash
# Configurações Azure
SUBSCRIPTION_ID="sua-subscription-id"
RESOURCE_GROUP="gaphunter-rg"
LOCATION="eastus"

# Configurações da Aplicação
OPENROUTER_API_KEY="sua-chave-openrouter"
SECRET_KEY="sua-chave-secreta-super-segura"

# Configurações do Banco
DB_ADMIN_PASSWORD="senha-super-segura-do-banco"

# Configurações de Email (opcional)
SMTP_SERVER="smtp.gmail.com"
SMTP_USERNAME="seu-email@gmail.com"
SMTP_PASSWORD="sua-senha-de-app"
```

### 2. Login no Azure

```bash
# Fazer login
az login

# Verificar subscription
az account show

# Definir subscription (se necessário)
az account set --subscription "sua-subscription-id"
```

## 🚀 Deploy Automático

### Opção 1: Script Automático (Recomendado)

```bash
# Tornar o script executável
chmod +x deploy-azure.sh

# Executar deploy
./deploy-azure.sh
```

O script automaticamente:
- Cria todos os recursos necessários
- Faz build e push das imagens Docker
- Configura banco de dados PostgreSQL
- Deploya backend e frontend
- Configura networking e SSL

### Opção 2: Deploy Manual

Se preferir controle total sobre cada etapa:

#### 1. Criar Resource Group
```bash
az group create \
    --name gaphunter-rg \
    --location eastus
```

#### 2. Criar Container Registry
```bash
az acr create \
    --resource-group gaphunter-rg \
    --name gaphunterregistry \
    --sku Basic \
    --admin-enabled true
```

#### 3. Build e Push das Imagens
```bash
# Backend
cd backend
az acr build --registry gaphunterregistry --image gaphunter-backend:latest .

# Frontend
cd ../frontend
az acr build --registry gaphunterregistry --image gaphunter-frontend:latest .
cd ..
```

#### 4. Criar Banco de Dados
```bash
az postgres flexible-server create \
    --resource-group gaphunter-rg \
    --name gaphunter-postgres-server \
    --location eastus \
    --admin-user gaphunteradmin \
    --admin-password "SuaSenhaSegura123!" \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 15 \
    --public-access 0.0.0.0

az postgres flexible-server db create \
    --resource-group gaphunter-rg \
    --server-name gaphunter-postgres-server \
    --database-name gaphunter
```

#### 5. Criar Container Apps Environment
```bash
az containerapp env create \
    --name gaphunter-env \
    --resource-group gaphunter-rg \
    --location eastus
```

#### 6. Deploy do Backend
```bash
az containerapp create \
    --name gaphunter-backend \
    --resource-group gaphunter-rg \
    --environment gaphunter-env \
    --image gaphunterregistry.azurecr.io/gaphunter-backend:latest \
    --registry-server gaphunterregistry.azurecr.io \
    --target-port 8000 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 10 \
    --cpu 1.0 \
    --memory 2Gi \
    --secrets database-url="postgresql://gaphunteradmin:SuaSenhaSegura123!@gaphunter-postgres-server.postgres.database.azure.com:5432/gaphunter" \
    --env-vars DATABASE_URL=secretref:database-url ENVIRONMENT=production
```

#### 7. Deploy do Frontend
```bash
# Obter URL do backend
BACKEND_URL=$(az containerapp show --name gaphunter-backend --resource-group gaphunter-rg --query "properties.configuration.ingress.fqdn" --output tsv)

az containerapp create \
    --name gaphunter-frontend \
    --resource-group gaphunter-rg \
    --environment gaphunter-env \
    --image gaphunterregistry.azurecr.io/gaphunter-frontend:latest \
    --registry-server gaphunterregistry.azurecr.io \
    --target-port 80 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 5 \
    --cpu 0.5 \
    --memory 1Gi \
    --env-vars VITE_API_BASE_URL="https://$BACKEND_URL/api"
```

## 🔍 Verificação e Testes

### 1. Verificar Status dos Containers
```bash
# Status do backend
az containerapp show --name gaphunter-backend --resource-group gaphunter-rg --query "properties.provisioningState"

# Status do frontend
az containerapp show --name gaphunter-frontend --resource-group gaphunter-rg --query "properties.provisioningState"
```

### 2. Obter URLs da Aplicação
```bash
# URL do frontend
FRONTEND_URL=$(az containerapp show --name gaphunter-frontend --resource-group gaphunter-rg --query "properties.configuration.ingress.fqdn" --output tsv)
echo "Frontend: https://$FRONTEND_URL"

# URL do backend
BACKEND_URL=$(az containerapp show --name gaphunter-backend --resource-group gaphunter-rg --query "properties.configuration.ingress.fqdn" --output tsv)
echo "Backend: https://$BACKEND_URL"
echo "API Docs: https://$BACKEND_URL/docs"
```

### 3. Testar Endpoints
```bash
# Health check do backend
curl https://$BACKEND_URL/health

# Health check do frontend
curl https://$FRONTEND_URL/health
```

## 📊 Monitoramento e Logs

### 1. Visualizar Logs em Tempo Real
```bash
# Logs do backend
az containerapp logs show --name gaphunter-backend --resource-group gaphunter-rg --follow

# Logs do frontend
az containerapp logs show --name gaphunter-frontend --resource-group gaphunter-rg --follow
```

### 2. Métricas de Performance
```bash
# Métricas do backend
az containerapp show --name gaphunter-backend --resource-group gaphunter-rg --query "properties.template.scale"

# Status das réplicas
az containerapp replica list --name gaphunter-backend --resource-group gaphunter-rg
```

### 3. Configurar Alertas
```bash
# Criar alerta para alta utilização de CPU
az monitor metrics alert create \
    --name "GapHunter High CPU" \
    --resource-group gaphunter-rg \
    --scopes "/subscriptions/sua-subscription/resourceGroups/gaphunter-rg/providers/Microsoft.App/containerApps/gaphunter-backend" \
    --condition "avg Percentage CPU > 80" \
    --description "Alert when CPU usage is above 80%"
```

## 🔄 Atualizações e Manutenção

### 1. Atualizar Aplicação
```bash
# Fazer novo build e push
cd backend
az acr build --registry gaphunterregistry --image gaphunter-backend:latest .

# Atualizar container app
az containerapp update \
    --name gaphunter-backend \
    --resource-group gaphunter-rg \
    --image gaphunterregistry.azurecr.io/gaphunter-backend:latest
```

### 2. Executar Migrações do Banco
```bash
# Conectar ao container e executar migrações
az containerapp exec \
    --name gaphunter-backend \
    --resource-group gaphunter-rg \
    --command "alembic upgrade head"
```

### 3. Backup do Banco de Dados
```bash
# Criar backup
az postgres flexible-server backup create \
    --resource-group gaphunter-rg \
    --server-name gaphunter-postgres-server \
    --backup-name "backup-$(date +%Y%m%d)"
```

## 🔒 Segurança e SSL

### 1. Configurar Domínio Personalizado
```bash
# Adicionar domínio personalizado
az containerapp hostname add \
    --hostname "app.gaphunter.com" \
    --name gaphunter-frontend \
    --resource-group gaphunter-rg
```

### 2. Configurar SSL/TLS
```bash
# Certificado gerenciado pelo Azure
az containerapp hostname bind \
    --hostname "app.gaphunter.com" \
    --name gaphunter-frontend \
    --resource-group gaphunter-rg \
    --environment gaphunter-env
```

### 3. Configurar Firewall do Banco
```bash
# Permitir apenas Container Apps
az postgres flexible-server firewall-rule create \
    --resource-group gaphunter-rg \
    --name gaphunter-postgres-server \
    --rule-name "AllowContainerApps" \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 255.255.255.255
```

## 💰 Estimativa de Custos

### Recursos e Custos Mensais (USD)
- **Container Apps**: ~$30-100 (dependendo do tráfego)
- **PostgreSQL Flexible Server**: ~$25-50
- **Container Registry**: ~$5
- **Log Analytics**: ~$10-20
- **Bandwidth**: ~$5-15

**Total estimado**: $75-190/mês

### Otimização de Custos
- Use **Burstable tier** para banco de dados
- Configure **auto-scaling** adequado
- Monitore **métricas de utilização**
- Use **reserved capacity** para workloads previsíveis

## 🛠️ Solução de Problemas

### 1. Container não inicia
```bash
# Verificar logs detalhados
az containerapp logs show --name gaphunter-backend --resource-group gaphunter-rg --tail 100

# Verificar configuração
az containerapp show --name gaphunter-backend --resource-group gaphunter-rg
```

### 2. Erro de conexão com banco
```bash
# Testar conectividade
az postgres flexible-server connect \
    --name gaphunter-postgres-server \
    --admin-user gaphunteradmin \
    --database-name gaphunter
```

### 3. Problemas de SSL/HTTPS
```bash
# Verificar certificados
az containerapp hostname list \
    --name gaphunter-frontend \
    --resource-group gaphunter-rg
```

### 4. Alto uso de recursos
```bash
# Verificar métricas
az monitor metrics list \
    --resource "/subscriptions/sua-subscription/resourceGroups/gaphunter-rg/providers/Microsoft.App/containerApps/gaphunter-backend" \
    --metric "CpuPercentage,MemoryPercentage"
```

## 📞 Suporte e Recursos

### Documentação Oficial
- [Azure Container Apps](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Azure Database for PostgreSQL](https://docs.microsoft.com/en-us/azure/postgresql/)
- [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/)

### Comandos Úteis
```bash
# Listar todos os recursos
az resource list --resource-group gaphunter-rg --output table

# Verificar custos
az consumption usage list --top 10

# Limpar recursos (CUIDADO!)
az group delete --name gaphunter-rg --yes --no-wait
```

---

**🎉 Parabéns!** Sua aplicação GapHunter está agora rodando no Azure com alta disponibilidade, escalabilidade automática e monitoramento completo.

Para suporte adicional, consulte a documentação oficial do Azure ou entre em contato com a equipe de desenvolvimento.

