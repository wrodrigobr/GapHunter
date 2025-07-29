#!/bin/bash

# Script de Deploy INTELIGENTE - Azure App Service
# GapHunter - Plataforma de Análise de Poker
# FOCO: Encontrar região com quota disponível automaticamente

set -e

echo "🧠 Iniciando deploy INTELIGENTE do GapHunter..."

# Configurações base
RESOURCE_GROUP="gaphunter-rg"
BACKEND_APP_NAME="gaphunter-backend"
FRONTEND_APP_NAME="gaphunter-frontend-static"
POSTGRES_SERVER_NAME="gaphunter-postgres"
DATABASE_NAME="gaphunter"
APP_SERVICE_PLAN="gaphunter-plan"

# Regiões para testar (ordenadas por custo-benefício)
REGIONS=(
    "westus2"
    "eastus2"
    "southcentralus"
    "centralus"
    "westus3"
    "eastus"
    "westeurope"
    "northeurope"
    "brazilsouth"
    "southeastasia"
)

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

# Função para testar quota em uma região
test_region_quota() {
    local region=$1
    echo "🔍 Testando região: $region"
    
    # Tentar criar um App Service Plan temporário para testar quota
    local test_plan="quota-test-$(date +%s)"
    
    if az appservice plan create \
        --name $test_plan \
        --resource-group $RESOURCE_GROUP \
        --location $region \
        --sku B1 \
        --is-linux \
        --only-show-errors &> /dev/null; then
        
        echo "✅ $region: Quota B1 disponível!"
        
        # Limpar plano de teste
        az appservice plan delete \
            --name $test_plan \
            --resource-group $RESOURCE_GROUP \
            --yes \
            --only-show-errors &> /dev/null
        
        return 0
    else
        echo "❌ $region: Sem quota B1, testando F1..."
        
        # Testar F1
        if az appservice plan create \
            --name $test_plan \
            --resource-group $RESOURCE_GROUP \
            --location $region \
            --sku F1 \
            --is-linux \
            --only-show-errors &> /dev/null; then
            
            echo "✅ $region: Quota F1 disponível!"
            
            # Limpar plano de teste
            az appservice plan delete \
                --name $test_plan \
                --resource-group $RESOURCE_GROUP \
                --yes \
                --only-show-errors &> /dev/null
            
            return 1  # F1 disponível (código 1)
        else
            echo "❌ $region: Sem quota F1 também"
            return 2  # Sem quota
        fi
    fi
}

# Criar Resource Group
echo "📦 Criando Resource Group..."
az group create \
    --name $RESOURCE_GROUP \
    --location westus2 \
    --only-show-errors > /dev/null

# Encontrar região com quota
SELECTED_REGION=""
SELECTED_SKU=""

echo ""
echo "🌍 Procurando região com quota disponível..."

for region in "${REGIONS[@]}"; do
    test_region_quota $region
    result=$?
    
    if [ $result -eq 0 ]; then
        SELECTED_REGION=$region
        SELECTED_SKU="B1"
        echo "🎯 Região selecionada: $region (B1 Basic)"
        break
    elif [ $result -eq 1 ]; then
        if [ -z "$SELECTED_REGION" ]; then
            SELECTED_REGION=$region
            SELECTED_SKU="F1"
            echo "⚠️  Região com F1: $region (continuando busca por B1...)"
        fi
    fi
done

# Verificar se encontrou região
if [ -z "$SELECTED_REGION" ]; then
    echo ""
    echo "❌ ERRO: Nenhuma região com quota disponível encontrada!"
    echo ""
    echo "💡 Soluções:"
    echo "1. Solicite aumento de quota no Portal Azure"
    echo "2. Tente regiões diferentes manualmente"
    echo "3. Use Container Instances como alternativa"
    echo ""
    exit 1
fi

echo ""
echo "🎉 Região encontrada: $SELECTED_REGION ($SELECTED_SKU)"
echo ""

# Continuar com deploy usando região selecionada
LOCATION=$SELECTED_REGION

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
        --public-access 0.0.0.0 \
        --only-show-errors
fi

# Criar database
if ! az postgres flexible-server db show --database-name $DATABASE_NAME --server-name $POSTGRES_SERVER_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "📋 Criando database..."
    az postgres flexible-server db create \
        --resource-group $RESOURCE_GROUP \
        --server-name $POSTGRES_SERVER_NAME \
        --database-name $DATABASE_NAME \
        --only-show-errors
fi

# Connection string para PostgreSQL
DATABASE_URL="postgresql://gaphunter:$DB_ADMIN_PASSWORD@$POSTGRES_SERVER_NAME.postgres.database.azure.com:5432/$DATABASE_NAME"

# Criar App Service Plan com SKU selecionado
echo "📋 Criando App Service Plan ($SELECTED_SKU) em $LOCATION..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku $SELECTED_SKU \
    --is-linux \
    --only-show-errors

# Criar Backend App Service
echo "⚙️ Criando Backend App Service..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $BACKEND_APP_NAME \
    --runtime "PYTHON|3.11" \
    --deployment-local-git \
    --only-show-errors

# Configurar variáveis de ambiente
echo "🔧 Configurando variáveis de ambiente..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $BACKEND_APP_NAME \
    --settings \
    DATABASE_URL="$DATABASE_URL" \
    SECRET_KEY="${SECRET_KEY:-$(openssl rand -base64 32)}" \
    OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
    ENVIRONMENT="production" \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    ENABLE_ORYX_BUILD=true \
    --only-show-errors

# Otimizações para F1
if [ "$SELECTED_SKU" = "F1" ]; then
    echo "🔧 Aplicando otimizações para F1..."
    az webapp config appsettings set \
        --resource-group $RESOURCE_GROUP \
        --name $BACKEND_APP_NAME \
        --settings \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE=false \
        WEBSITE_HTTPLOGGING_RETENTION_DAYS=1 \
        GUNICORN_WORKERS=1 \
        GUNICORN_TIMEOUT=120 \
        --only-show-errors
fi

# Configurar startup
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $BACKEND_APP_NAME \
    --startup-file "python startup.py" \
    --only-show-errors

# Deploy do backend via GitHub
echo "📤 Configurando deploy do backend via GitHub..."
az webapp deployment source config \
    --resource-group $RESOURCE_GROUP \
    --name $BACKEND_APP_NAME \
    --repo-url "https://github.com/wrodrigobr/gaphunter" \
    --branch master \
    --manual-integration \
    --only-show-errors

# Obter URL do backend
BACKEND_URL=$(az webapp show --name $BACKEND_APP_NAME --resource-group $RESOURCE_GROUP --query "defaultHostName" --output tsv)

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
        --output-location "dist" \
        --only-show-errors
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
echo "💰 Plano utilizado: $SELECTED_SKU"
echo ""
if [ "$SELECTED_SKU" = "F1" ]; then
    echo "💰 Custo estimado: ~$12/mês (PostgreSQL apenas)"
    echo "⚠️  Limitações F1: 60min/dia CPU, sem Always-On"
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

