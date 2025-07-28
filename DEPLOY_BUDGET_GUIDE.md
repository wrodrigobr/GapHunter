# 💰 Guia de Deploy ECONÔMICO - GapHunter no Azure

Este documento fornece instruções para fazer o deploy da plataforma GapHunter no Microsoft Azure com **FOCO TOTAL EM ECONOMIA DE CUSTOS**, ideal para MVPs e projetos em fase inicial.

## 🎯 Objetivo: Menor Custo Possível

**Meta de custo**: $15-30/mês para um MVP funcional
**Estratégia**: Configurações mínimas + Scale-to-zero + Azure SQL Basic

## 📊 Comparação de Custos

### Deploy Padrão vs Deploy Econômico

| Recurso | Deploy Padrão | Deploy Econômico | Economia |
|---------|---------------|------------------|----------|
| **Azure SQL Database** | Standard (50 DTU) ~$15/mês | Basic (5 DTU) ~$5/mês | **67% menos** |
| **Container Apps Backend** | 1 CPU, 2GB RAM | 0.5 CPU, 1GB RAM | **50% menos** |
| **Container Apps Frontend** | 0.5 CPU, 1GB RAM | 0.25 CPU, 0.5GB RAM | **50% menos** |
| **Min Replicas** | 1 réplica sempre ativa | 0 réplicas (scale-to-zero) | **100% economia quando inativo** |
| **Container Registry** | Standard | Basic | **50% menos** |
| **Total Estimado** | $75-150/mês | **$15-30/mês** | **80% menos** |

## 🚀 Deploy Rápido (Recomendado)

### Script Automatizado Econômico

```bash
# 1. Extrair projeto
tar -xzf gaphunter-azure-deploy.tar.gz
cd gaphunter

# 2. Configurar variável da API OpenRouter
export OPENROUTER_API_KEY="sua-chave-openrouter"

# 3. Executar deploy econômico
chmod +x deploy-azure-budget.sh
./deploy-azure-budget.sh
```

**Tempo estimado**: 15-20 minutos
**Custo resultante**: $15-30/mês

## 🔧 Configurações Econômicas Aplicadas

### 1. Azure SQL Database - Basic Tier
```bash
# Configuração mais barata possível
Service Tier: Basic
DTUs: 5 (mínimo)
Storage: 2GB (mínimo)
Backup: Local (não geo-redundante)
```

**Custo**: ~$5/mês

### 2. Container Apps - Recursos Mínimos
```yaml
Backend:
  CPU: 0.5 vCPU (50% menos que padrão)
  Memory: 1GB (50% menos que padrão)
  Min Replicas: 0 (scale-to-zero)
  Max Replicas: 3 (reduzido)

Frontend:
  CPU: 0.25 vCPU (50% menos que padrão)
  Memory: 0.5GB (50% menos que padrão)
  Min Replicas: 0 (scale-to-zero)
  Max Replicas: 2 (reduzido)
```

**Custo**: ~$8-15/mês (dependendo do uso)

### 3. Scale-to-Zero (Economia Máxima)
- **0 réplicas mínimas**: Aplicação "dorme" quando não há tráfego
- **Cold start**: ~10-15 segundos para "acordar"
- **Economia**: 100% quando inativo

### 4. Container Registry - Basic
```bash
SKU: Basic (mais barato)
Storage: Ilimitado
Bandwidth: 10GB/mês incluído
```

**Custo**: ~$5/mês

## 📋 Pré-requisitos

### Ferramentas Necessárias
- **Azure CLI** (versão 2.40+)
- **Conta Azure** com créditos ou cartão
- **Chave OpenRouter** (para IA)

### Instalação Azure CLI
```bash
# Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# macOS
brew install azure-cli

# Windows
# Baixar de: https://aka.ms/installazurecliwindows
```

## 🎯 Deploy Passo a Passo

### 1. Login e Configuração
```bash
# Login no Azure
az login

# Verificar subscription
az account show

# Definir subscription (se necessário)
az account set --subscription "sua-subscription-id"
```

### 2. Configurar Variáveis
```bash
# Definir chave da OpenRouter
export OPENROUTER_API_KEY="sua-chave-openrouter"

# Verificar se foi definida
echo $OPENROUTER_API_KEY
```

### 3. Executar Deploy Econômico
```bash
# Tornar script executável
chmod +x deploy-azure-budget.sh

# Executar deploy
./deploy-azure-budget.sh
```

### 4. Aguardar Conclusão
O script irá:
- ✅ Criar Resource Group
- ✅ Criar Container Registry (Basic)
- ✅ Build e push das imagens
- ✅ Criar Azure SQL Database (Basic)
- ✅ Deploy dos Container Apps (configuração mínima)
- ✅ Configurar scale-to-zero

## 💡 Otimizações de Custo Implementadas

### 1. Scale-to-Zero
```bash
# Aplicação "dorme" quando não há tráfego
Min Replicas: 0

# "Acorda" automaticamente quando recebe requisição
Auto-scaling: Baseado em HTTP requests
```

### 2. Recursos Mínimos
```yaml
# Backend otimizado
CPU: 0.5 vCPU (suficiente para MVP)
Memory: 1GB (suficiente para FastAPI)

# Frontend otimizado  
CPU: 0.25 vCPU (suficiente para Nginx)
Memory: 0.5GB (suficiente para servir arquivos estáticos)
```

### 3. Banco de Dados Econômico
```sql
-- Azure SQL Database Basic
DTUs: 5 (suficiente para MVP)
Storage: 2GB (expansível conforme necessário)
Backup: 7 dias (padrão)
Geo-redundância: Desabilitada (economia)
```

### 4. Sem Recursos Desnecessários
- ❌ Azure Storage (usa storage local)
- ❌ Application Insights (usa logs básicos)
- ❌ Load Balancer adicional
- ❌ CDN
- ❌ Backup geo-redundante

## 📊 Monitoramento de Custos

### 1. Verificar Custos Atuais
```bash
# Listar custos por resource group
az consumption usage list --top 10

# Verificar custos específicos
az billing invoice list
```

### 2. Configurar Alertas de Custo
```bash
# Criar alerta para gastos acima de $50
az consumption budget create \
    --budget-name "GapHunter-Budget" \
    --amount 50 \
    --time-grain Monthly \
    --time-period start-date=2024-01-01 \
    --notifications \
        enabled=true \
        operator=GreaterThan \
        threshold=80 \
        contact-emails=["seu-email@example.com"]
```

### 3. Parar Aplicação (Economia Total)
```bash
# Parar backend (custo = $0)
az containerapp update \
    --name gaphunter-backend \
    --resource-group gaphunter-rg \
    --min-replicas 0 \
    --max-replicas 0

# Parar frontend (custo = $0)
az containerapp update \
    --name gaphunter-frontend \
    --resource-group gaphunter-rg \
    --min-replicas 0 \
    --max-replicas 0
```

## 🔄 Escalabilidade Futura

### Quando Escalar?
- **Usuários**: >100 usuários ativos
- **Tráfego**: >1000 requests/dia
- **Performance**: Response time >2 segundos

### Como Escalar?
```bash
# Aumentar recursos do backend
az containerapp update \
    --name gaphunter-backend \
    --resource-group gaphunter-rg \
    --cpu 1.0 \
    --memory 2Gi \
    --min-replicas 1 \
    --max-replicas 5

# Upgrade do banco de dados
az sql db update \
    --resource-group gaphunter-rg \
    --server gaphunter-sql-server \
    --name gaphunter \
    --service-objective S1  # Standard tier
```

## 🛠️ Troubleshooting Econômico

### 1. Cold Start Lento
**Problema**: Aplicação demora para "acordar"
**Solução**: 
```bash
# Manter 1 réplica mínima (aumenta custo ~$5/mês)
az containerapp update \
    --name gaphunter-backend \
    --resource-group gaphunter-rg \
    --min-replicas 1
```

### 2. Banco de Dados Lento
**Problema**: Queries demoradas
**Solução**:
```bash
# Upgrade para Standard S0 (+$15/mês)
az sql db update \
    --resource-group gaphunter-rg \
    --server gaphunter-sql-server \
    --name gaphunter \
    --service-objective S0
```

### 3. Limite de Storage
**Problema**: Banco atingiu 2GB
**Solução**:
```bash
# Expandir para 10GB (+$2/mês)
az sql db update \
    --resource-group gaphunter-rg \
    --server gaphunter-sql-server \
    --name gaphunter \
    --max-size 10GB
```

## 💰 Plano de Crescimento de Custos

### Fase 1: MVP ($15-30/mês)
- Azure SQL Basic (5 DTU)
- Container Apps mínimos
- Scale-to-zero ativo

### Fase 2: Primeiros Usuários ($30-60/mês)
- Azure SQL Standard S0 (10 DTU)
- 1 réplica mínima (sem cold start)
- Monitoramento básico

### Fase 3: Crescimento ($60-120/mês)
- Azure SQL Standard S1 (20 DTU)
- 2-3 réplicas mínimas
- Application Insights
- CDN básico

### Fase 4: Escala ($120-300/mês)
- Azure SQL Standard S2+ (50+ DTU)
- Auto-scaling agressivo
- Múltiplas regiões
- Backup geo-redundante

## 📞 Suporte e Recursos

### Comandos Úteis
```bash
# Verificar status
az containerapp list --resource-group gaphunter-rg --output table

# Ver logs
az containerapp logs show --name gaphunter-backend --resource-group gaphunter-rg --follow

# Verificar custos
az consumption usage list --top 5

# Parar tudo (emergência)
az group delete --name gaphunter-rg --yes --no-wait
```

### Links Importantes
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
- [Azure SQL Database Pricing](https://azure.microsoft.com/en-us/pricing/details/sql-database/)
- [Container Apps Pricing](https://azure.microsoft.com/en-us/pricing/details/container-apps/)

---

## 🎉 Resumo

✅ **Deploy econômico configurado**
✅ **Custo estimado: $15-30/mês**
✅ **Scale-to-zero implementado**
✅ **Azure SQL Database Basic**
✅ **Recursos mínimos otimizados**

**🚀 Sua aplicação está pronta para rodar com o menor custo possível!**

Para dúvidas ou otimizações adicionais, consulte a documentação oficial do Azure ou ajuste as configurações conforme sua necessidade específica.

