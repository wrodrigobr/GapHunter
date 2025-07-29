#!/bin/bash

# Script de Deploy PRINCIPAL - Azure App Service
# GapHunter - Plataforma de Análise de Poker
# FOCO: Máxima simplicidade e menor custo

set -e

echo "🚀 Iniciando deploy ECONÔMICO do GapHunter com App Service..."

# Configurações OTIMIZADAS PARA CUSTO
RESOURCE_GROUP="gaphunter-rg"
LOCATION="${AZURE_LOCATION:-westus2}"  # Alterado de eastus, permite override via variável
BACKEND_APP_NAME="gaphunter-backend"
FRONTEND_APP_NAME="gaphunter-frontend-static"
POSTGRES_SERVER_NAME="gaphunter-postgres"
DATABASE_NAME="gaphunter"
APP_SERVICE_PLAN="gaphunter-plan"

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

# Criar Azure Database for PostgreSQL (CONFIGURAÇÃO MAIS BARATA)
echo "🗄️ Criando Azure Database for PostgreSQL (configuração econômica)..."
if [ -z "$DB_ADMIN_PASSWORD" ]; then
    DB_ADMIN_PASSWORD=$(openssl rand -base64 32)
    echo "🔑 Senha do banco gerada: $DB_ADMIN_PASSWORD"
    echo "⚠️  IMPORTANTE: Salve esta senha!"
fi

# Criar PostgreSQL Flexible Server (mais barato que SQL Server)
if ! az postgres flexible-server show --name $POSTGRES_SERVER_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "📊 Criando PostgreSQL Flexible Server..."
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
fi

# Criar database
if ! az postgres flexible-server db show --database-name $DATABASE_NAME --server-name $POSTGRES_SERVER_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "📋 Criando database..."
    az postgres flexible-server db create \
        --resource-group $RESOURCE_GROUP \
        --server-name $POSTGRES_SERVER_NAME \
        --database-name $DATABASE_NAME
fi

# Connection string para PostgreSQL
DATABASE_URL="postgresql://gaphunter:$DB_ADMIN_PASSWORD@$POSTGRES_SERVER_NAME.postgres.database.azure.com:5432/$DATABASE_NAME"

# Criar App Service Plan (B1 Basic - compartilhado entre front e back)
echo "📋 Criando App Service Plan (B1 Basic)..."
if ! az appservice plan show --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP &> /dev/null; then
    az appservice plan create \
        --name $APP_SERVICE_PLAN \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku B1 \
        --is-linux
fi

# Criar Backend App Service (Python/FastAPI)
echo "⚙️ Criando Backend App Service..."
if ! az webapp show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    az webapp create \
        --resource-group $RESOURCE_GROUP \
        --plan $APP_SERVICE_PLAN \
        --name $BACKEND_APP_NAME \
        --runtime "PYTHON|3.11" \
        --deployment-local-git
fi

# Configurar variáveis de ambiente do backend
echo "🔧 Configurando variáveis de ambiente do backend..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $BACKEND_APP_NAME \
    --settings \
    DATABASE_URL="$DATABASE_URL" \
    SECRET_KEY="${SECRET_KEY:-$(openssl rand -base64 32)}" \
    OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
    ENVIRONMENT="production" \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    ENABLE_ORYX_BUILD=true

# Configurar startup command
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $BACKEND_APP_NAME \
    --startup-file "python startup.py"

# Deploy do backend via GitHub
echo "📤 Configurando deploy do backend via GitHub..."
az webapp deployment source config \
    --resource-group $RESOURCE_GROUP \
    --name $BACKEND_APP_NAME \
    --repo-url "https://github.com/wrodrigobr/gaphunter" \
    --branch master \
    --manual-integration

# Obter URL do backend
BACKEND_URL=$(az webapp show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --query "defaultHostName" --output tsv)
echo "🔗 Backend URL: https://$BACKEND_URL"

# Criar Frontend como Static Web App (GRATUITO!)
echo "🎨 Criando Frontend como Static Web App (GRATUITO)..."
STATIC_APP_NAME="gaphunter-frontend-static"

if ! az staticwebapp show --name $STATIC_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    az staticwebapp create \
        --name $STATIC_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --source "https://github.com/wrodrigobr/gaphunter" \
        --branch master \
        --app-location "/frontend" \
        --api-location "/backend" \
        --output-location "dist"
fi

# Obter URL do frontend
FRONTEND_URL=$(az staticwebapp show --name $STATIC_APP_NAME --resource-group $RESOURCE_GROUP --query "defaultHostname" --output tsv)

echo ""
echo "🎉 Deploy concluído com sucesso!"
echo ""
echo "🌐 URLs da aplicação:"
echo "Frontend: https://$FRONTEND_URL"
echo "Backend:  https://$BACKEND_URL"
echo "API Docs: https://$BACKEND_URL/docs"
echo ""
echo "💰 Configuração econômica aplicada:"
echo "- PostgreSQL Flexible Server: B1ms (~$12/mês)"
echo "- App Service Plan: B1 Basic (~$13/mês)"
echo "- Static Web App: GRATUITO"
echo "- Custo total estimado: ~$25/mês"
echo ""
echo "🔑 Credenciais do banco:"
echo "Servidor: $POSTGRES_SERVER_NAME.postgres.database.azure.com"
echo "Usuário: gaphunter"
echo "Senha: $DB_ADMIN_PASSWORD"
echo "Database: $DATABASE_NAME"
echo ""
echo "⚠️  IMPORTANTE: Salve as credenciais do banco em local seguro!"

# Executar migrações do banco
echo ""
echo "🔄 Executando migrações do banco de dados..."
echo "Aguarde o backend ficar online e execute manualmente:"
echo "curl -X POST https://$BACKEND_URL/admin/migrate"

