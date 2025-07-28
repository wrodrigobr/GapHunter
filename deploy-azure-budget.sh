#!/bin/bash

# Script de Deploy OTIMIZADO PARA CUSTO - Azure Container Apps
# GapHunter - Plataforma de Análise de Poker
# FOCO: Menor custo possível para MVP

set -e

echo "💰 Iniciando deploy ECONÔMICO do GapHunter no Azure..."

# Configurações OTIMIZADAS PARA CUSTO
RESOURCE_GROUP="gaphunter-rg"
LOCATION="eastus"  # Região mais barata
CONTAINER_REGISTRY="gaphunterregistry"
ENVIRONMENT_NAME="gaphunter-env"
BACKEND_APP_NAME="gaphunter-backend"
FRONTEND_APP_NAME="gaphunter-frontend"
SQL_SERVER_NAME="gaphunter-sql-server"
DATABASE_NAME="gaphunter"

# Verificar se Azure CLI está instalado
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI não está instalado. Instale em: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login no Azure (se necessário)
echo "🔐 Verificando login no Azure..."
if ! az account show &> /dev/null; then
    echo "Por favor, faça login no Azure:"
    az login
fi

# Criar Resource Group
echo "📦 Criando Resource Group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# Criar Azure Container Registry (SKU Basic - mais barato)
echo "📋 Criando Azure Container Registry (Basic SKU)..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_REGISTRY \
    --sku Basic \
    --admin-enabled true

# Obter credenciais do registry
echo "🔑 Obtendo credenciais do Container Registry..."
ACR_SERVER=$(az acr show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
ACR_USERNAME=$(az acr credential show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP --query "username" --output tsv)
ACR_PASSWORD=$(az acr credential show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP --query "passwords[0].value" --output tsv)

# Build e push das imagens Docker
echo "🐳 Fazendo build e push das imagens Docker..."

# Backend
echo "📊 Build da imagem do backend..."
cd backend
az acr build --registry $CONTAINER_REGISTRY --image gaphunter-backend:latest .
cd ..

# Frontend
echo "🎨 Build da imagem do frontend..."
cd frontend
az acr build --registry $CONTAINER_REGISTRY --image gaphunter-frontend:latest .
cd ..

# Criar Azure Database for PostgreSQL (CONFIGURAÇÃO MAIS BARATA)
echo "🗄️ Criando Azure Database for PostgreSQL (configuração econômica)..."
DB_ADMIN_PASSWORD=$(openssl rand -base64 32)
POSTGRES_SERVER_NAME="gaphunter-postgres"

# Criar PostgreSQL Flexible Server (mais barato que SQL Server)
az postgres flexible-server create \
    --resource-group $RESOURCE_GROUP \
    --name $POSTGRES_SERVER_NAME \
    --location $LOCATION \
    --admin-user gaphunter \
    --admin-password $DB_ADMIN_PASSWORD \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 14 \
    --public-access 0.0.0.0

# Criar database
az postgres flexible-server db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $POSTGRES_SERVER_NAME \
    --database-name $DATABASE_NAME

# Connection string para PostgreSQL
DATABASE_URL="postgresql://gaphunter:$DB_ADMIN_PASSWORD@$POSTGRES_SERVER_NAME.postgres.database.azure.com:5432/$DATABASE_NAME"

# Criar Container Apps Environment
echo "🏗️ Criando Container Apps Environment..."
az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Deploy do Backend (CONFIGURAÇÃO MÍNIMA PARA ECONOMIZAR)
echo "⚙️ Fazendo deploy do backend (configuração econômica)..."
az containerapp create \
    --name $BACKEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $ACR_SERVER/gaphunter-backend:latest \
    --registry-server $ACR_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 8000 \
    --ingress external \
    --min-replicas 0 \
    --max-replicas 3 \
    --cpu 0.5 \
    --memory 1Gi \
    --secrets database-url="$DATABASE_URL" secret-key="$(openssl rand -base64 32)" openrouter-api-key="$OPENROUTER_API_KEY" \
    --env-vars DATABASE_URL=secretref:database-url SECRET_KEY=secretref:secret-key OPENROUTER_API_KEY=secretref:openrouter-api-key ENVIRONMENT=production

# Obter URL do backend
BACKEND_URL=$(az containerapp show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" --output tsv)

# Deploy do Frontend (CONFIGURAÇÃO MÍNIMA PARA ECONOMIZAR)
echo "🎨 Fazendo deploy do frontend (configuração econômica)..."
az containerapp create \
    --name $FRONTEND_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $ACR_SERVER/gaphunter-frontend:latest \
    --registry-server $ACR_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 80 \
    --ingress external \
    --min-replicas 0 \
    --max-replicas 2 \
    --cpu 0.25 \
    --memory 0.5Gi \
    --env-vars VITE_API_BASE_URL="https://$BACKEND_URL/api"

# Obter URL do frontend
FRONTEND_URL=$(az containerapp show --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" --output tsv)

echo "✅ Deploy ECONÔMICO concluído com sucesso!"
echo ""
echo "🌐 URLs da aplicação:"
echo "Frontend: https://$FRONTEND_URL"
echo "Backend:  https://$BACKEND_URL"
echo "API Docs: https://$BACKEND_URL/docs"
echo ""
echo "🗄️ Informações do banco de dados:"
echo "Servidor: $SQL_SERVER_NAME.database.windows.net"
echo "Database: $DATABASE_NAME"
echo "Usuário:  gaphunter"
echo "Senha:    $DB_ADMIN_PASSWORD"
echo ""
echo "📋 Container Registry:"
echo "Servidor: $ACR_SERVER"
echo "Usuário:  $ACR_USERNAME"
echo ""
echo "💰 CONFIGURAÇÃO ECONÔMICA APLICADA:"
echo "- Azure SQL Database: Basic tier (2GB)"
echo "- Container Apps: CPU/Memory mínimos"
echo "- Auto-scaling: 0 réplicas mínimas (scale-to-zero)"
echo "- Container Registry: Basic SKU"
echo ""
echo "💡 Custo estimado: $15-30/mês"
echo "💡 Para monitorar custos: az consumption usage list"
echo "💡 Para parar aplicação: az containerapp update --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --min-replicas 0"

