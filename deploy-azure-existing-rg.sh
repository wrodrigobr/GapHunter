#!/bin/bash

# Script de Deploy para Resource Group EXISTENTE - Azure App Service
# GapHunter - Plataforma de Análise de Poker
# FOCO: Usar Resource Group existente e sua região

set -e

echo "🔄 Iniciando deploy do GapHunter usando Resource Group existente..."

# Configurações base
RESOURCE_GROUP="gaphunter-rg"
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

# Verificar se Resource Group existe e obter sua localização
echo "📍 Verificando Resource Group existente..."
if az group show --name $RESOURCE_GROUP &> /dev/null; then
    LOCATION=$(az group show --name $RESOURCE_GROUP --query location --output tsv)
    echo "✅ Resource Group '$RESOURCE_GROUP' encontrado em: $LOCATION"
else
    echo "❌ Resource Group '$RESOURCE_GROUP' não encontrado!"
    echo "💡 Criando novo Resource Group em eastus..."
    LOCATION="eastus"
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION
    echo "✅ Resource Group criado em: $LOCATION"
fi

echo "🌍 Usando região: $LOCATION"

# Criar Azure Database for PostgreSQL
echo "🗄️ Criando Azure Database for PostgreSQL..."
if [ -z "$DB_ADMIN_PASSWORD" ]; then
    DB_ADMIN_PASSWORD=$(openssl rand -base64 32)
    echo "🔑 Senha do banco gerada: $DB_ADMIN_PASSWORD"
    echo "⚠️  IMPORTANTE: Salve esta senha!"
fi

# Criar PostgreSQL Flexible Server
if ! az postgres flexible-server show --name $POSTGRES_SERVER_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "📊 Criando PostgreSQL Flexible Server em $LOCATION..."
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
else
    echo "✅ PostgreSQL Server já existe"
fi

# Criar database
if ! az postgres flexible-server db show --database-name $DATABASE_NAME --server-name $POSTGRES_SERVER_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "📋 Criando database..."
    az postgres flexible-server db create \
        --resource-group $RESOURCE_GROUP \
        --server-name $POSTGRES_SERVER_NAME \
        --database-name $DATABASE_NAME
else
    echo "✅ Database já existe"
fi

# Connection string para PostgreSQL
DATABASE_URL="postgresql://gaphunter:$DB_ADMIN_PASSWORD@$POSTGRES_SERVER_NAME.postgres.database.azure.com:5432/$DATABASE_NAME"

# Criar App Service Plan com fallback inteligente
echo "📋 Criando App Service Plan em $LOCATION..."
PLAN_SKU=""

if ! az appservice plan show --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "🎯 Tentando criar plano B1 Basic..."
    if az appservice plan create \
        --name $APP_SERVICE_PLAN \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku B1 \
        --is-linux 2>/dev/null; then
        echo "✅ Plano B1 Basic criado com sucesso!"
        PLAN_SKU="B1"
    else
        echo "⚠️  B1 não disponível devido a quota. Tentando F1 GRATUITO..."
        if az appservice plan create \
            --name $APP_SERVICE_PLAN \
            --resource-group $RESOURCE_GROUP \
            --location $LOCATION \
            --sku F1 \
            --is-linux 2>/dev/null; then
            echo "✅ Plano F1 GRATUITO criado com sucesso!"
            PLAN_SKU="F1"
            echo "💡 F1 tem limitações: 60min/dia CPU, sem Always-On"
        else
            echo "❌ Nem B1 nem F1 disponíveis na região $LOCATION"
            echo "💡 Possíveis soluções:"
            echo "1. Solicite aumento de quota no Portal Azure"
            echo "2. Tente uma região diferente"
            echo "3. Use Container Instances como alternativa"
            exit 1
        fi
    fi
else
    echo "✅ App Service Plan já existe"
    PLAN_SKU=$(az appservice plan show --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --query sku.name --output tsv)
    echo "📊 Plano atual: $PLAN_SKU"
fi

# Criar Backend App Service
echo "⚙️ Criando Backend App Service..."
if ! az webapp show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    az webapp create \
        --resource-group $RESOURCE_GROUP \
        --plan $APP_SERVICE_PLAN \
        --name $BACKEND_APP_NAME \
        --runtime "PYTHON|3.11" \
        --deployment-local-git
else
    echo "✅ Backend App Service já existe"
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

# Otimizações específicas para F1
if [ "$PLAN_SKU" = "F1" ]; then
    echo "🔧 Aplicando otimizações para plano F1..."
    az webapp config appsettings set \
        --resource-group $RESOURCE_GROUP \
        --name $BACKEND_APP_NAME \
        --settings \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE=false \
        WEBSITE_HTTPLOGGING_RETENTION_DAYS=1 \
        GUNICORN_WORKERS=1 \
        GUNICORN_TIMEOUT=120
fi

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

# Criar Frontend como Static Web App
echo "🎨 Criando Frontend como Static Web App..."
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
else
    echo "✅ Static Web App já existe"
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
echo "📍 Região utilizada: $LOCATION"
echo "💰 Plano utilizado: $PLAN_SKU"
echo ""
if [ "$PLAN_SKU" = "F1" ]; then
    echo "💰 Custo estimado: ~$12/mês (PostgreSQL apenas)"
    echo "⚠️  Limitações F1: 60min/dia CPU, sem Always-On"
    echo "💡 Para produção, solicite aumento de quota para B1"
else
    echo "💰 Custo estimado: ~$25/mês"
fi
echo ""
echo "🔑 Credenciais do banco:"
echo "Servidor: $POSTGRES_SERVER_NAME.postgres.database.azure.com"
echo "Usuário: gaphunter"
echo "Senha: $DB_ADMIN_PASSWORD"
echo ""
echo "⚠️  IMPORTANTE: Salve as credenciais!"

# Aguardar backend ficar online
echo ""
echo "🔄 Aguardando backend ficar online..."
if [ "$PLAN_SKU" = "F1" ]; then
    echo "⏱️  Plano F1 pode ter cold start mais lento..."
    sleep 180  # 3 minutos para F1
else
    sleep 120  # 2 minutos para B1
fi

echo "🔄 Tentando executar migrações do banco de dados..."
for i in {1..5}; do
    if curl -X POST "https://$BACKEND_URL/admin/migrate" -f &> /dev/null; then
        echo "✅ Migrações executadas com sucesso!"
        break
    else
        echo "Tentativa $i/5 - aguardando backend..."
        sleep 60
    fi
done

echo ""
echo "🎯 Próximos passos:"
echo "1. Teste a aplicação nas URLs acima"
echo "2. Configure sua API key da OpenRouter"
echo "3. Faça upload de hand histories para testar"
if [ "$PLAN_SKU" = "F1" ]; then
    echo "4. Solicite aumento de quota para B1 quando necessário"
fi

