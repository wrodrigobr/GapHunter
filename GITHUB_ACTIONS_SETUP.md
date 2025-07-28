# 🚀 Configuração GitHub Actions - Deploy Automático

Este guia explica como configurar o deploy automático do GapHunter no Azure usando GitHub Actions.

## 🎯 O que as GitHub Actions fazem

- ✅ **Deploy automático** a cada push no repositório
- ✅ **Build e push** das imagens Docker
- ✅ **Criação automática** de recursos Azure
- ✅ **Configuração otimizada** para menor custo
- ✅ **Migrações automáticas** do banco de dados

## 🔧 Configuração Necessária

### 1. Secrets do GitHub

Acesse `Settings > Secrets and variables > Actions` no seu repositório e adicione:

#### AZURE_CREDENTIALS
```json
{
  "clientId": "seu-client-id",
  "clientSecret": "seu-client-secret",
  "subscriptionId": "sua-subscription-id",
  "tenantId": "seu-tenant-id"
}
```

#### DB_ADMIN_PASSWORD
```
SuaSenhaSeguraDoSQL123!
```

#### SECRET_KEY
```
sua-chave-secreta-super-segura-para-jwt
```

#### OPENROUTER_API_KEY
```
sua-chave-da-openrouter-para-ia
```

### 2. Como obter AZURE_CREDENTIALS

#### Opção A: Azure CLI (Recomendado)
```bash
# Login no Azure
az login

# Criar Service Principal
az ad sp create-for-rbac \
  --name "GapHunter-GitHub-Actions" \
  --role contributor \
  --scopes /subscriptions/SUA-SUBSCRIPTION-ID \
  --sdk-auth
```

#### Opção B: Portal Azure
1. Acesse **Azure Active Directory**
2. Vá em **App registrations > New registration**
3. Nome: `GapHunter-GitHub-Actions`
4. Anote: `Application (client) ID` e `Directory (tenant) ID`
5. Vá em **Certificates & secrets > New client secret**
6. Anote o `Value` do secret criado
7. Vá em **Subscriptions > Sua subscription > Access control (IAM)**
8. Adicione role `Contributor` para o App criado

### 3. Formato do AZURE_CREDENTIALS
```json
{
  "clientId": "12345678-1234-1234-1234-123456789012",
  "clientSecret": "seu-client-secret-aqui",
  "subscriptionId": "87654321-4321-4321-4321-210987654321",
  "tenantId": "11111111-2222-3333-4444-555555555555"
}
```

## 🚀 Como Usar

### Deploy Automático
```bash
# Qualquer push no master/main dispara o deploy
git add .
git commit -m "Nova funcionalidade"
git push origin master
```

### Deploy Manual
1. Acesse **Actions** no GitHub
2. Selecione **Deploy GapHunter to Azure**
3. Clique **Run workflow**

## 📊 Workflow do Deploy

### 1. Preparação
- ✅ Checkout do código
- ✅ Login no Azure
- ✅ Criação do Resource Group

### 2. Container Registry
- ✅ Criação do Azure Container Registry
- ✅ Build da imagem do backend
- ✅ Build da imagem do frontend
- ✅ Push das imagens

### 3. Banco de Dados
- ✅ Criação do SQL Server
- ✅ Configuração do firewall
- ✅ Criação do banco de dados (Basic tier)

### 4. Container Apps
- ✅ Criação do environment
- ✅ Deploy do backend (configuração econômica)
- ✅ Deploy do frontend (configuração econômica)

### 5. Finalização
- ✅ Execução das migrações
- ✅ Exibição das URLs finais

## 🔍 Monitoramento

### Logs do GitHub Actions
- Acesse **Actions** no repositório
- Clique no workflow executado
- Veja logs detalhados de cada step

### Logs da Aplicação
```bash
# Backend logs
az containerapp logs show \
  --name gaphunter-backend \
  --resource-group gaphunter-rg \
  --follow

# Frontend logs  
az containerapp logs show \
  --name gaphunter-frontend \
  --resource-group gaphunter-rg \
  --follow
```

## 🛠️ Troubleshooting

### 1. Erro de Autenticação
**Problema**: `Authentication failed`
**Solução**: Verificar se `AZURE_CREDENTIALS` está correto

### 2. Erro de Permissão
**Problema**: `Insufficient privileges`
**Solução**: Garantir que Service Principal tem role `Contributor`

### 3. Erro de Build
**Problema**: Build da imagem falha
**Solução**: Verificar Dockerfile e dependências

### 4. Erro de Banco
**Problema**: Conexão com SQL falha
**Solução**: Verificar `DB_ADMIN_PASSWORD` e firewall

## 🔄 Customização

### Alterar Configurações
Edite `.github/workflows/deploy-azure.yml`:

```yaml
# Alterar recursos do backend
--cpu 1.0 \
--memory 2Gi \

# Alterar tier do banco
--service-objective S0 \

# Alterar região
AZURE_LOCATION: westus2
```

### Adicionar Environments
```yaml
# Deploy para staging
on:
  push:
    branches: [ develop ]
    
env:
  AZURE_RESOURCE_GROUP: gaphunter-staging-rg
```

### Adicionar Testes
```yaml
- name: Run Tests
  run: |
    cd backend
    pip install -r requirements.txt
    python -m pytest tests/
```

## 💰 Otimizações de Custo

### Configurações Aplicadas
- **Scale-to-zero**: Apps "dormem" quando não há tráfego
- **Recursos mínimos**: CPU e memória otimizados
- **SQL Basic**: Tier mais barato (5 DTU)
- **Container Registry Basic**: SKU econômico

### Monitorar Custos
```bash
# Verificar gastos
az consumption usage list --top 10

# Configurar alertas
az consumption budget create \
  --budget-name "GapHunter-Budget" \
  --amount 50
```

## 🎯 Próximos Passos

### 1. Configurar Secrets
- [ ] AZURE_CREDENTIALS
- [ ] DB_ADMIN_PASSWORD  
- [ ] SECRET_KEY
- [ ] OPENROUTER_API_KEY

### 2. Testar Deploy
- [ ] Fazer push no repositório
- [ ] Verificar Actions no GitHub
- [ ] Acessar aplicação deployada

### 3. Configurar Monitoramento
- [ ] Alertas de custo
- [ ] Logs centralizados
- [ ] Health checks

---

## 🎉 Pronto!

Com essa configuração, você terá:
- ✅ **Deploy automático** a cada push
- ✅ **Infraestrutura como código**
- ✅ **Custos otimizados** ($15-30/mês)
- ✅ **Zero configuração manual**

**🚀 Sua pipeline de CI/CD está pronta para produção!**

