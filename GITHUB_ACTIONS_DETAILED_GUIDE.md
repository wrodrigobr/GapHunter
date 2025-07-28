# 🚀 Guia Detalhado: GitHub Actions para Deploy no Azure

Este guia foi criado para quem nunca configurou GitHub Actions antes. Vamos cobrir cada passo em detalhes, explicando onde encontrar as informações e como preenchê-las.

## Parte 1: Visão Geral e Pré-requisitos

### O que são GitHub Actions?

GitHub Actions é uma plataforma de Integração Contínua e Entrega Contínua (CI/CD) nativa do GitHub. Ela permite automatizar, personalizar e executar seus fluxos de trabalho de desenvolvimento de software diretamente no seu repositório GitHub. Isso significa que você pode automatizar tarefas como:

- **Build de código**: Compilar seu projeto.
- **Testes**: Executar testes unitários, de integração, etc.
- **Deploy**: Publicar sua aplicação em servidores (como o Azure).
- **Notificações**: Enviar mensagens sobre o status do deploy.

No nosso caso, usaremos as GitHub Actions para automatizar o processo de build das imagens Docker do GapHunter e o deploy dessas imagens no Azure Container Apps, além de configurar o Azure SQL Database.

### Por que usar GitHub Actions para este projeto?

- **Automação**: Chega de deploy manual! Cada vez que você fizer uma alteração no código e enviar para o GitHub, o deploy será feito automaticamente.
- **Consistência**: Garante que o processo de deploy seja sempre o mesmo, reduzindo erros humanos.
- **Visibilidade**: Você pode ver o status do seu deploy diretamente no GitHub, com logs detalhados.
- **Custo-benefício**: É gratuito para repositórios públicos e oferece um bom plano gratuito para repositórios privados.

### Pré-requisitos

Antes de começarmos, você precisará ter acesso e algumas informações das seguintes plataformas:

1.  **Conta GitHub**: Onde seu código do GapHunter está hospedado.
2.  **Conta Microsoft Azure**: Onde sua aplicação será deployada e o banco de dados será criado.
    *   Você precisará de permissões para criar e gerenciar recursos (Resource Groups, Container Registries, Container Apps, SQL Servers, SQL Databases).
    *   Uma assinatura ativa com créditos ou um método de pagamento configurado.
3.  **Chave da API OpenRouter**: Para as funcionalidades de IA do GapHunter.

### Ferramentas Necessárias (para obter as credenciais)

Você precisará do **Azure CLI** instalado em seu computador. Ele é uma ferramenta de linha de comando que permite interagir com os serviços do Azure. Se você ainda não o tem, siga as instruções abaixo:

#### Como instalar o Azure CLI

-   **No Ubuntu/Debian (Linux)**:
    ```bash
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    ```

-   **No macOS**:
    ```bash
    brew install azure-cli
    ```

-   **No Windows**:
    *   Baixe o instalador MSI diretamente do site oficial da Microsoft: [Instalar Azure CLI no Windows](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows)

Após a instalação, abra seu terminal ou prompt de comando e execute:

```bash
az login
```

Isso abrirá uma janela do navegador para você fazer login na sua conta Azure. Depois de logado, o terminal mostrará suas informações de assinatura. Se você tiver múltiplas assinaturas, pode ser necessário definir a padrão:

```bash
az account set --subscription "SEU_ID_DA_ASSINATURA"
```

Você pode encontrar o ID da sua assinatura executando `az account show` ou no Portal Azure em `Assinaturas`.

---


## Parte 2: Configurando Credenciais Azure (Service Principal)

Para que o GitHub Actions possa se comunicar com sua conta Azure e criar/gerenciar recursos, ele precisa de uma identidade com permissões. Essa identidade é chamada de **Service Principal** (Entidade de Serviço) no Azure. Vamos criar uma e obter as credenciais necessárias.

Existem duas formas principais de fazer isso:

### Opção A: Usando o Azure CLI (Recomendado e Mais Simples)

Esta é a forma mais rápida e recomendada, pois o Azure CLI já gera o JSON completo que você precisará.

1.  **Abra seu terminal ou prompt de comando** (onde você já instalou e logou no Azure CLI na Parte 1).

2.  **Execute o seguinte comando**: Substitua `SEU_ID_DA_ASSINATURA` pelo ID da sua assinatura Azure. Você pode obter o ID da sua assinatura executando `az account show --query id -o tsv`.

    ```bash
    az ad sp create-for-rbac \
      --name "GapHunter-GitHub-Actions" \
      --role contributor \
      --scopes /subscriptions/SEU_ID_DA_ASSINATURA \
      --sdk-auth
    ```

    -   `--name "GapHunter-GitHub-Actions"`: Define um nome amigável para sua Entidade de Serviço. Você pode usar qualquer nome que ajude a identificar a finalidade.
    -   `--role contributor`: Concede à Entidade de Serviço a função de `Colaborador` na sua assinatura. Isso significa que ela terá permissão para criar e gerenciar a maioria dos recursos (Resource Groups, Container Apps, SQL Databases, etc.). Para um ambiente de produção, você pode querer refinar essas permissões para o mínimo necessário, mas para começar, `contributor` é suficiente.
    -   `--scopes /subscriptions/SEU_ID_DA_ASSINATURA`: Limita o escopo das permissões à sua assinatura específica. Isso é importante para segurança.
    -   `--sdk-auth`: Formata a saída em JSON, que é o formato exato que o GitHub Actions espera.

3.  **Copie a saída JSON completa**: Após executar o comando, você verá uma saída JSON no seu terminal, semelhante a esta:

    ```json
    {
      "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
      "resourceManagerEndpointUrl": "https://management.azure.com/",
      "activeDirectoryGraphResourceId": "https://graph.windows.net/",
      "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
      "galleryEndpointUrl": "https://gallery.azure.com/",
      "managementEndpointUrl": "https://management.core.windows.net/"
    }
    ```

    **Guarde esta saída JSON em um local seguro.** Você precisará dela na Parte 3.

### Opção B: Usando o Portal Azure (Mais Visual)

Se você prefere uma abordagem visual, pode criar a Entidade de Serviço através do Portal Azure. No entanto, você terá que montar o JSON manualmente depois.

1.  **Acesse o Portal Azure**: [portal.azure.com](https://portal.azure.com)

2.  **Vá para Azure Active Directory**: No campo de busca superior, digite "Azure Active Directory" e selecione o serviço.

3.  **Registrar um aplicativo (App registrations)**:
    *   No menu lateral, clique em `App registrations` (Registros de aplicativo).
    *   Clique em `New registration` (Novo registro).
    *   **Nome**: Dê um nome para o aplicativo, por exemplo, `GapHunter-GitHub-Actions`.
    *   Deixe as outras opções como padrão e clique em `Register` (Registrar).

4.  **Anote as informações do aplicativo**: Após o registro, você será redirecionado para a página de visão geral do seu novo aplicativo. Anote os seguintes valores:
    *   `Application (client) ID` (ID do aplicativo cliente)
    *   `Directory (tenant) ID` (ID do diretório locatário)

5.  **Crie um segredo do cliente (Client secret)**:
    *   No menu lateral do seu aplicativo, clique em `Certificates & secrets` (Certificados e segredos).
    *   Na aba `Client secrets`, clique em `New client secret` (Novo segredo do cliente).
    *   Dê uma `Description` (Descrição) (ex: `GitHub Actions Secret`) e defina uma `Expires` (Expira) (recomendado 1 ano ou 2 anos).
    *   Clique em `Add` (Adicionar).
    *   **IMPORTANTE**: O `Value` (Valor) do segredo será exibido **apenas uma vez** após a criação. **Copie-o imediatamente e guarde-o em um local seguro.** Se você perder, terá que criar um novo.

6.  **Conceda permissões (Role Assignment)**:
    *   Vá para a página inicial do Portal Azure.
    *   No campo de busca superior, digite "Subscriptions" e selecione `Subscriptions` (Assinaturas).
    *   Clique na sua assinatura (aquela onde você quer fazer o deploy).
    *   No menu lateral, clique em `Access control (IAM)` (Controle de acesso (IAM)).
    *   Clique em `Add > Add role assignment` (Adicionar > Adicionar atribuição de função).
    *   **Role (Função)**: Selecione `Contributor` (Colaborador).
    *   **Members (Membros)**: Clique em `Select members` (Selecionar membros) e procure pelo nome do seu aplicativo (`GapHunter-GitHub-Actions`). Selecione-o e clique em `Select`.
    *   Clique em `Review + assign` (Revisar + atribuir) e depois em `Review + assign` novamente.

7.  **Monte o JSON `AZURE_CREDENTIALS`**: Agora que você tem todas as partes, monte o JSON no formato esperado pelo GitHub Actions:

    ```json
    {
      "clientId": "<Application (client) ID que você anotou>",
      "clientSecret": "<Valor do Client Secret que você copiou>",
      "subscriptionId": "<Seu ID da Assinatura Azure>",
      "tenantId": "<Directory (tenant) ID que você anotou>"
    }
    ```

    **Onde encontrar o ID da Assinatura Azure**: No Portal Azure, vá para `Subscriptions` (Assinaturas) e copie o `Subscription ID`.

---


## Parte 3: Configurando Secrets do GitHub

Agora que você tem as credenciais do Azure e as chaves da API, é hora de adicioná-las de forma segura ao seu repositório GitHub. O GitHub Secrets permite armazenar informações sensíveis (como senhas e chaves de API) sem expô-las diretamente no seu código.

### Onde adicionar os Secrets

1.  **Acesse seu repositório no GitHub**: Vá para `https://github.com/SEU_USUARIO/SEU_REPOSITORIO` (substitua `SEU_USUARIO` e `SEU_REPOSITORIO` pelos seus dados).
2.  **Vá para as configurações do repositório**: Clique em `Settings` (Configurações) no menu superior.
3.  **Acesse a seção de Secrets**: No menu lateral esquerdo, clique em `Secrets and variables` (Segredos e variáveis) e depois em `Actions` (Ações).
4.  **Adicione um novo repositório secret**: Clique no botão `New repository secret` (Novo segredo do repositório).

### Secrets que você precisa adicionar

Você precisará adicionar os seguintes secrets, um por um:

#### 1. `AZURE_CREDENTIALS`

-   **Name (Nome)**: `AZURE_CREDENTIALS` (digite exatamente assim)
-   **Secret (Segredo)**: Cole aqui o **JSON completo** que você obteve na **Parte 2** (Opção A ou B). Certifique-se de que não há espaços extras ou caracteres inválidos.
-   Clique em `Add secret`.

    *Exemplo do que você deve colar (apenas para referência, use o seu JSON real):*
    ```json
    {
      "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
    ```

#### 2. `DB_ADMIN_PASSWORD`

-   **Name (Nome)**: `DB_ADMIN_PASSWORD`
-   **Secret (Segredo)**: Digite a senha que você deseja usar para o usuário administrador do seu Azure SQL Database. **Escolha uma senha forte e segura!** Esta senha será usada pelo script de deploy para criar o banco de dados.
-   Clique em `Add secret`.

    *Exemplo (apenas para referência, use sua senha real):*
    ```
    MinhaSenhaSuperSeguraParaOBanco123!
    ```

#### 3. `SECRET_KEY`

-   **Name (Nome)**: `SECRET_KEY`
-   **Secret (Segredo)**: Digite uma chave secreta longa e aleatória. Esta chave é usada pelo backend FastAPI para assinar os tokens JWT (autenticação). É crucial que seja uma chave forte e que **nunca seja exposta publicamente**.
-   Clique em `Add secret`.

    *Exemplo (apenas para referência, gere uma chave aleatória):*
    ```
    sua-chave-secreta-longa-e-aleatoria-para-jwt-nao-compartilhe
    ```

#### 4. `OPENROUTER_API_KEY`

-   **Name (Nome)**: `OPENROUTER_API_KEY`
-   **Secret (Segredo)**: Cole aqui a sua chave da API do OpenRouter. Esta chave é usada para as funcionalidades de IA do GapHunter.
-   Clique em `Add secret`.

    *Exemplo (apenas para referência, use sua chave real):*
    ```
    sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

### Verificando os Secrets

Após adicionar todos os secrets, você verá uma lista deles na página `Secrets and variables > Actions`. O valor real dos secrets não será visível, apenas o nome, o que garante a segurança.

---


## Parte 4: Entendendo o Workflow e Testando o Deploy

Agora que você configurou os secrets, vamos entender o arquivo de workflow do GitHub Actions e como disparar o deploy.

### Entendendo o Arquivo de Workflow (`.github/workflows/deploy-azure.yml`)

Este arquivo define as etapas que o GitHub Actions seguirá para fazer o deploy da sua aplicação. Ele está localizado no seu repositório em `.github/workflows/deploy-azure.yml`.

Vamos analisar as seções principais:

```yaml
name: Deploy GapHunter to Azure # Nome do workflow, aparece no GitHub Actions

on:
  push:
    branches: [ master, main ] # Dispara o workflow quando há um push para master ou main
  workflow_dispatch: # Permite disparar o workflow manualmente pela interface do GitHub

env:
  AZURE_RESOURCE_GROUP: gaphunter-rg # Variáveis de ambiente globais para o workflow
  AZURE_LOCATION: eastus
  CONTAINER_REGISTRY: gaphunterregistry
  BACKEND_APP_NAME: gaphunter-backend
  FRONTEND_APP_NAME: gaphunter-frontend
  SQL_SERVER_NAME: gaphunter-sql-server
  DATABASE_NAME: gaphunter

jobs:
  deploy:
    runs-on: ubuntu-latest # O job será executado em uma máquina virtual Ubuntu
    
    steps:
    - name: Checkout code # Baixa o código do seu repositório
      uses: actions/checkout@v4

    - name: Login to Azure # Faz login no Azure usando as credenciais do secret AZURE_CREDENTIALS
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Create Resource Group # Cria o grupo de recursos no Azure (se não existir)
      run: |
        az group create \
          --name ${{ env.AZURE_RESOURCE_GROUP }} \
          --location ${{ env.AZURE_LOCATION }}

    - name: Create Container Registry # Cria o Azure Container Registry (se não existir)
      run: |
        if ! az acr show --name ${{ env.CONTAINER_REGISTRY }} --resource-group ${{ env.AZURE_RESOURCE_GROUP }} &> /dev/null; then
          az acr create \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --name ${{ env.CONTAINER_REGISTRY }} \
            --sku Basic \
            --admin-enabled true
        fi

    - name: Get ACR credentials # Obtém as credenciais do Container Registry para o build e push
      id: acr-creds
      run: |
        ACR_SERVER=$(az acr show --name ${{ env.CONTAINER_REGISTRY }} --resource-group ${{ env.AZURE_RESOURCE_GROUP }} --query "loginServer" --output tsv)
        ACR_USERNAME=$(az acr credential show --name ${{ env.CONTAINER_REGISTRY }} --resource-group ${{ env.AZURE_RESOURCE_GROUP }} --query "username" --output tsv)
        ACR_PASSWORD=$(az acr credential show --name ${{ env.CONTAINER_REGISTRY }} --resource-group ${{ env.AZURE_RESOURCE_GROUP }} --query "passwords[0].value" --output tsv)
        
        echo "acr-server=$ACR_SERVER" >> $GITHUB_OUTPUT
        echo "acr-username=$ACR_USERNAME" >> $GITHUB_OUTPUT
        echo "acr-password=$ACR_PASSWORD" >> $GITHUB_OUTPUT

    - name: Build and push backend image # Constrói a imagem Docker do backend e envia para o ACR
      run: |
        cd backend
        az acr build \
          --registry ${{ env.CONTAINER_REGISTRY }} \
          --image gaphunter-backend:${{ github.sha }} \
          --image gaphunter-backend:latest \
          .

    - name: Build and push frontend image # Constrói a imagem Docker do frontend e envia para o ACR
      run: |
        cd frontend
        az acr build \
          --registry ${{ env.CONTAINER_REGISTRY }} \
          --image gaphunter-frontend:${{ github.sha }} \
          --image gaphunter-frontend:latest \
          .

    - name: Create SQL Server and Database # Cria o Azure SQL Server e o Database (se não existirem)
      run: |
        # Check if SQL Server exists
        if ! az sql server show --name ${{ env.SQL_SERVER_NAME }} --resource-group ${{ env.AZURE_RESOURCE_GROUP }} &> /dev/null; then
          echo "Creating SQL Server..."
          az sql server create \
            --name ${{ env.SQL_SERVER_NAME }} \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --location ${{ env.AZURE_LOCATION }} \
            --admin-user gaphunter \
            --admin-password "${{ secrets.DB_ADMIN_PASSWORD }}"
          
          # Configure firewall
          az sql server firewall-rule create \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --server ${{ env.SQL_SERVER_NAME }} \
            --name AllowAzureServices \
            --start-ip-address 0.0.0.0 \
            --end-ip-address 0.0.0.0
        fi
        
        # Check if database exists
        if ! az sql db show --name ${{ env.DATABASE_NAME }} --server ${{ env.SQL_SERVER_NAME }} --resource-group ${{ env.AZURE_RESOURCE_GROUP }} &> /dev/null; then
          echo "Creating database..."
          az sql db create \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --server ${{ env.SQL_SERVER_NAME }} \
            --name ${{ env.DATABASE_NAME }} \
            --service-objective Basic \
            --max-size 2GB
        fi

    - name: Create Container Apps Environment # Cria o ambiente do Azure Container Apps (se não existir)
      run: |
        if ! az containerapp env show --name gaphunter-env --resource-group ${{ env.AZURE_RESOURCE_GROUP }} &> /dev/null; then
          az containerapp env create \
            --name gaphunter-env \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --location ${{ env.AZURE_LOCATION }}
        fi

    - name: Deploy Backend Container App # Faz o deploy ou atualiza o backend no Container Apps
      run: |
        DATABASE_URL="mssql+pyodbc://gaphunter:${{ secrets.DB_ADMIN_PASSWORD }}@${{ env.SQL_SERVER_NAME }}.database.windows.net:1433/${{ env.DATABASE_NAME }}?driver=ODBC+Driver+18+for+SQL+Server"
        
        if az containerapp show --name ${{ env.BACKEND_APP_NAME }} --resource-group ${{ env.AZURE_RESOURCE_GROUP }} &> /dev/null; then
          # Update existing app
          az containerapp update \
            --name ${{ env.BACKEND_APP_NAME }} \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --image ${{ steps.acr-creds.outputs.acr-server }}/gaphunter-backend:latest
        else
          # Create new app
          az containerapp create \
            --name ${{ env.BACKEND_APP_NAME }} \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --environment gaphunter-env \
            --image ${{ steps.acr-creds.outputs.acr-server }}/gaphunter-backend:latest \
            --registry-server ${{ steps.acr-creds.outputs.acr-server }} \
            --registry-username ${{ steps.acr-creds.outputs.acr-username }} \
            --registry-password ${{ steps.acr-creds.outputs.acr-password }} \
            --target-port 8000 \
            --ingress external \
            --min-replicas 0 \
            --max-replicas 3 \
            --cpu 0.5 \
            --memory 1Gi \
            --secrets database-url="$DATABASE_URL" secret-key="${{ secrets.SECRET_KEY }}" openrouter-api-key="${{ secrets.OPENROUTER_API_KEY }}" \
            --env-vars DATABASE_URL=secretref:database-url SECRET_KEY=secretref:secret-key OPENROUTER_API_KEY=secretref:openrouter-api-key ENVIRONMENT=production
        fi

    - name: Get Backend URL # Obtém a URL do backend deployado
      id: backend-url
      run: |
        BACKEND_URL=$(az containerapp show --name ${{ env.BACKEND_APP_NAME }} --resource-group ${{ env.AZURE_RESOURCE_GROUP }} --query "properties.configuration.ingress.fqdn" --output tsv)
        echo "backend-url=$BACKEND_URL" >> $GITHUB_OUTPUT

    - name: Deploy Frontend Container App # Faz o deploy ou atualiza o frontend no Container Apps
      run: |
        if az containerapp show --name ${{ env.FRONTEND_APP_NAME }} --resource-group ${{ env.AZURE_RESOURCE_GROUP }} &> /dev/null; then
          # Update existing app
          az containerapp update \
            --name ${{ env.FRONTEND_APP_NAME }} \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --image ${{ steps.acr-creds.outputs.acr-server }}/gaphunter-frontend:latest \
            --set-env-vars VITE_API_BASE_URL="https://${{ steps.backend-url.outputs.backend-url }}/api"
        else
          # Create new app
          az containerapp create \
            --name ${{ env.FRONTEND_APP_NAME }} \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --environment gaphunter-env \
            --image ${{ steps.acr-creds.outputs.acr-server }}/gaphunter-frontend:latest \
            --registry-server ${{ steps.acr-creds.outputs.acr-server }} \
            --registry-username ${{ steps.acr-creds.outputs.acr-username }} \
            --registry-password ${{ steps.acr-creds.outputs.acr-password }} \
            --target-port 80 \
            --ingress external \
            --min-replicas 0 \
            --max-replicas 2 \
            --cpu 0.25 \
            --memory 0.5Gi \
            --env-vars VITE_API_BASE_URL="https://${{ steps.backend-url.outputs.backend-url }}/api"
        fi

    - name: Get Frontend URL # Obtém a URL do frontend deployado
      id: frontend-url
      run: |
        FRONTEND_URL=$(az containerapp show --name ${{ env.FRONTEND_APP_NAME }} --resource-group ${{ env.AZURE_RESOURCE_GROUP }} --query "properties.configuration.ingress.fqdn" --output tsv)
        echo "frontend-url=$FRONTEND_URL" >> $GITHUB_OUTPUT

    - name: Run Database Migrations # Executa as migrações do banco de dados
      run: |
        # Wait for backend to be ready
        sleep 60
        
        # Run migrations via container exec
        az containerapp exec \
          --name ${{ env.BACKEND_APP_NAME }} \
          --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
          --command "alembic upgrade head" || true

    - name: Display Deployment Info # Exibe as URLs da aplicação e informações finais
      run: |
        echo "🎉 Deployment completed successfully!"
        echo ""
        echo "🌐 Application URLs:"
        echo "Frontend: https://${{ steps.frontend-url.outputs.frontend-url }}"
        echo "Backend:  https://${{ steps.backend-url.outputs.backend-url }}"
        echo "API Docs: https://${{ steps.backend-url.outputs.backend-url }}/docs"
        echo ""
        echo "💰 Cost-optimized configuration applied:"
        echo "- Azure SQL Database: Basic tier (5 DTU)"
        echo "- Container Apps: Minimal resources with scale-to-zero"
        echo "- Estimated cost: $15-30/month"
```

### Como Disparar o Deploy

Existem duas maneiras de disparar o workflow de deploy:

#### 1. Deploy Automático (Recomendado)

O workflow está configurado para ser executado automaticamente sempre que você fizer um `push` para as branches `master` ou `main` do seu repositório. Isso significa que, após configurar os secrets, basta você continuar desenvolvendo e enviando suas alterações para o GitHub.

```bash
# Certifique-se de que suas alterações estão no stage
git add .

# Faça um commit com uma mensagem descritiva
git commit -m "Minha nova funcionalidade"

# Envie suas alterações para o GitHub (para a branch master ou main)
git push origin master # ou main
```

Após o `git push`, o GitHub detectará a alteração e iniciará o workflow `Deploy GapHunter to Azure` automaticamente.

#### 2. Deploy Manual (via Interface do GitHub)

Você também pode disparar o deploy manualmente, o que é útil para testar a configuração ou fazer um deploy específico sem precisar de um novo commit.

1.  **Acesse seu repositório no GitHub**.
2.  Clique na aba `Actions` (Ações).
3.  No menu lateral esquerdo, clique no workflow `Deploy GapHunter to Azure`.
4.  No lado direito, clique no botão `Run workflow` (Executar workflow).
5.  Clique novamente em `Run workflow` para confirmar.

### Monitorando o Deploy

Após disparar o deploy (seja por push ou manualmente), você pode acompanhar o progresso:

1.  **Acesse seu repositório no GitHub**.
2.  Clique na aba `Actions`.
3.  Você verá uma lista de execuções do workflow. Clique na execução mais recente (ou na que você acabou de disparar).
4.  Dentro da execução, você verá os "jobs" (tarefas) e os "steps" (passos) sendo executados em tempo real. Você pode clicar em cada passo para ver os logs detalhados da execução, o que é extremamente útil para depurar problemas.

### O que esperar após o Deploy

Se o deploy for bem-sucedido, o último passo do workflow (`Display Deployment Info`) exibirá as URLs da sua aplicação (Frontend, Backend e API Docs) no log. Você poderá acessar sua aplicação através dessas URLs.

**Importante**: O primeiro deploy pode demorar um pouco mais (15-20 minutos) porque o Azure precisará criar todos os recursos (Resource Group, Container Registry, SQL Server, Database, Container Apps Environment, Container Apps). Deployes subsequentes serão mais rápidos, pois os recursos já estarão criados e apenas as imagens e as configurações serão atualizadas.

---

