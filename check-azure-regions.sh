#!/bin/bash

# Script para verificar regiões Azure disponíveis
# GapHunter - Verificação de Quota por Região

echo "🌍 Verificando regiões Azure disponíveis para App Service..."

# Regiões recomendadas (custo-benefício)
REGIONS=(
    "eastus"
    "eastus2" 
    "westus2"
    "westus3"
    "centralus"
    "southcentralus"
    "westeurope"
    "northeurope"
    "brazilsouth"
    "southeastasia"
)

echo "📊 Verificando quota de App Service por região..."
echo ""

for region in "${REGIONS[@]}"; do
    echo "🔍 Verificando região: $region"
    
    # Verificar quota de Basic VMs
    basic_quota=$(az vm list-usage --location $region --query "[?name.value=='basicAFamily'].{current:currentValue,limit:limit}" --output tsv 2>/dev/null)
    
    if [ $? -eq 0 ] && [ ! -z "$basic_quota" ]; then
        current=$(echo $basic_quota | cut -f1)
        limit=$(echo $basic_quota | cut -f2)
        available=$((limit - current))
        
        if [ $available -gt 0 ]; then
            echo "✅ $region: $available/$limit Basic VMs disponíveis"
        else
            echo "❌ $region: $current/$limit Basic VMs (sem quota)"
        fi
    else
        echo "⚠️  $region: Não foi possível verificar quota"
    fi
    
    # Verificar quota de Free VMs
    free_quota=$(az vm list-usage --location $region --query "[?name.value=='standardAFamily'].{current:currentValue,limit:limit}" --output tsv 2>/dev/null)
    
    if [ $? -eq 0 ] && [ ! -z "$free_quota" ]; then
        current_free=$(echo $free_quota | cut -f1)
        limit_free=$(echo $free_quota | cut -f2)
        available_free=$((limit_free - current_free))
        
        if [ $available_free -gt 0 ]; then
            echo "✅ $region: $available_free/$limit_free Standard VMs disponíveis"
        fi
    fi
    
    echo ""
done

echo "💡 Recomendações:"
echo "1. Use uma região com quota disponível"
echo "2. Regiões mais baratas: eastus, eastus2, southcentralus"
echo "3. Regiões na Europa: westeurope, northeurope"
echo "4. Região no Brasil: brazilsouth"
echo ""
echo "🔧 Para alterar região no deploy:"
echo "export AZURE_LOCATION=\"westus2\"  # ou outra região disponível"
echo "./deploy-azure.sh"

