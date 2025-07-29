#!/bin/bash

# Script de Deploy para Azure Container Apps
# GapHunter - Plataforma de Análise de Poker

set -e

echo "🚀 Iniciando deploy do GapHunter no Azure..."

# Configurações
RESOURCE_GROUP="gaphunter-rg"
LOCATION="eastus"
CONTAINER_REGISTRY="gaphunterregistry"
ENVIRONMENT_NAME="gaphunter-env"
BACKEND_APP_NAME="gaphunter-backend"
FRONTEND_APP_NAME="gaphunter-frontend"
DATABASE_SERVER_NAME="gaphunter-postgres-server"
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

# Criar Azure Container Registry
echo "📋 Criando Azure Container Registry..."
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

# Criar Azure Database for PostgreSQL
echo "🗄️ Criando banco de dados PostgreSQL..."
DB_ADMIN_PASSWORD=$(openssl rand -base64 32)
az postgres flexible-server create \
    --resource-group $RESOURCE_GROUP \
    --name $DATABASE_SERVER_NAME \
    --location $LOCATION \
    --admin-user gaphunteradmin \
    --admin-password $DB_ADMIN_PASSWORD \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 15 \
    --public-access 0.0.0.0

# Criar database
az postgres flexible-server db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $DATABASE_SERVER_NAME \
    --database-name $DATABASE_NAME

# Obter connection string
DATABASE_URL="postgresql://gaphunteradmin:$DB_ADMIN_PASSWORD@$DATABASE_SERVER_NAME.postgres.database.azure.com:5432/$DATABASE_NAME"

# Criar Container Apps Environment
echo "🏗️ Criando Container Apps Environment..."
az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Deploy do Backend
echo "⚙️ Fazendo deploy do backend..."
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
    --min-replicas 1 \
    --max-replicas 10 \
    --cpu 1.0 \
    --memory 2Gi \
    --secrets database-url="$DATABASE_URL" secret-key="$(openssl rand -base64 32)" openrouter-api-key="$OPENROUTER_API_KEY" \
    --env-vars DATABASE_URL=secretref:database-url SECRET_KEY=secretref:secret-key OPENROUTER_API_KEY=secretref:openrouter-api-key ENVIRONMENT=production

# Obter URL do backend
BACKEND_URL=$(az containerapp show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" --output tsv)

# Deploy do Frontend
echo "🎨 Fazendo deploy do frontend..."
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
    --min-replicas 1 \
    --max-replicas 5 \
    --cpu 0.5 \
    --memory 1Gi \
    --env-vars VITE_API_BASE_URL="https://$BACKEND_URL/api"

# Obter URL do frontend
FRONTEND_URL=$(az containerapp show --name $FRONTEND_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" --output tsv)

echo "✅ Deploy concluído com sucesso!"
echo ""
echo "🌐 URLs da aplicação:"
echo "Frontend: https://$FRONTEND_URL"
echo "Backend:  https://$BACKEND_URL"
echo "API Docs: https://$BACKEND_URL/docs"
echo ""
echo "🗄️ Informações do banco de dados:"
echo "Servidor: $DATABASE_SERVER_NAME.postgres.database.azure.com"
echo "Database: $DATABASE_NAME"
echo "Usuário:  gaphunteradmin"
echo "Senha:    $DB_ADMIN_PASSWORD"
echo ""
echo "📋 Container Registry:"
echo "Servidor: $ACR_SERVER"
echo "Usuário:  $ACR_USERNAME"
echo ""
echo "💡 Para atualizar a aplicação, execute novamente este script."
echo "💡 Para monitorar logs: az containerapp logs show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --follow"

