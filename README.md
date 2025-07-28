# 🎯 GapHunter - Plataforma de Análise de Poker com IA

> **Identifique gaps recorrentes no seu jogo e evolua com análises técnicas personalizadas**

## 🚀 **Visão Geral**

O GapHunter é uma plataforma completa para análise de poker que utiliza Inteligência Artificial para identificar padrões problemáticos (gaps) no jogo dos usuários, oferecendo feedback técnico personalizado e acompanhamento de evolução.

## ✨ **Funcionalidades Principais**

### 🔍 **GapHunter Core**
- **Análise automática** de hand histories do PokerStars
- **Identificação de gaps recorrentes** com IA especializada
- **Feedback técnico detalhado** baseado em GTO
- **Sistema de severidade** para priorização de melhorias

### 📊 **Performance Tracker**
- **ROI e estatísticas** completas por período
- **Gráficos de evolução** temporal
- **Análise de ITM%** e volume de jogo
- **Tracking de buy-ins e premiações**

### 👨‍🏫 **Módulo para Coaches**
- **Acompanhamento de alunos** com progresso detalhado
- **Sistema de notas** categorizadas por prioridade
- **Análise de gaps por aluno** com histórico
- **Gestão de sessões** de coaching

### 👁️‍🗨️ **GapHunter Vision**
- **Análise de outros jogadores** (modo justo com reciprocidade)
- **Configurações de privacidade** granulares
- **Sistema de análises mútuas** entre jogadores

### 💳 **Sistema de Assinatura**
- **5 planos disponíveis**: Free, Basic, Pro, Coach, Premium
- **Controle de acesso** por funcionalidade
- **Gestão de upgrades** e downgrades

### 🎯 **GapHunter Club**
- **Programa de afiliados** com comissionamento
- **Sistema de níveis** (Bronze, Silver, Gold, Diamond)
- **Descontos progressivos** e benefícios exclusivos

## 🛠️ **Tecnologias Utilizadas**

### **Backend**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL** - Banco de dados principal
- **Alembic** - Migrações de banco
- **OpenRouter/Mistral** - IA para análise técnica

### **Frontend**
- **React** - Interface de usuário moderna
- **Vite** - Build tool otimizado
- **CSS Modules** - Estilização componentizada

### **Deploy**
- **Azure App Service** - Hospedagem do backend
- **Azure Static Web Apps** - Hospedagem do frontend (GRATUITO)
- **Azure Database for PostgreSQL** - Banco de dados gerenciado
- **GitHub Actions** - CI/CD automático

## 💰 **Custos de Infraestrutura**

### **Configuração Otimizada**
- **PostgreSQL Flexible Server**: B1ms (~$12/mês)
- **App Service Plan**: B1 Basic (~$13/mês)
- **Static Web App**: GRATUITO
- **Total estimado**: ~$25/mês

## 🚀 **Deploy Rápido**

### **Opção 1: Deploy Automático (Recomendado)**
1. Configure os secrets no GitHub:
   - `AZURE_CREDENTIALS`
   - `DB_ADMIN_PASSWORD`
   - `SECRET_KEY`
   - `OPENROUTER_API_KEY`
2. Faça push no repositório
3. Acompanhe o deploy nas GitHub Actions

### **Opção 2: Deploy Manual**
```bash
# Configure as variáveis
export DB_ADMIN_PASSWORD="SuaSenhaSegura123!"
export SECRET_KEY="$(openssl rand -base64 32)"
export OPENROUTER_API_KEY="sk-or-v1-xxxxx"

# Execute o deploy
chmod +x deploy-azure.sh
./deploy-azure.sh
```

## 📚 **Documentação**

- **[Guia de Deploy](DEPLOY_GUIDE.md)** - Deploy completo no Azure
- **[GitHub Actions Setup](GITHUB_ACTIONS_DETAILED_GUIDE.md)** - Configuração de CI/CD
- **[Comparação de Deploy](AZURE_DEPLOYMENT_COMPARISON.md)** - Container Apps vs App Service

## 🔧 **Desenvolvimento Local**

### **Pré-requisitos**
- Python 3.11+
- Node.js 18+
- PostgreSQL (ou SQLite para desenvolvimento)

### **Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configure suas variáveis
python startup.py
```

### **Frontend**
```bash
cd frontend
npm install
npm run dev
```

## 🎯 **Como Usar**

1. **Registre-se** na plataforma
2. **Configure sua API key** da OpenRouter
3. **Faça upload** de hand histories do PokerStars
4. **Analise os gaps** identificados pela IA
5. **Acompanhe sua evolução** com estatísticas detalhadas

## 🤝 **Contribuição**

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📄 **Licença**

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 **Suporte**

- **Issues**: Reporte bugs ou solicite features
- **Documentação**: Consulte os guias na pasta docs/
- **Deploy**: Siga o [Guia de Deploy](DEPLOY_GUIDE.md)

---

**🎉 Desenvolvido com ❤️ para a comunidade de poker**

### **Links Úteis**
- 🌐 **Demo**: [Em breve]
- 📖 **Docs**: [Guias de Deploy](DEPLOY_GUIDE.md)
- 🐛 **Issues**: [GitHub Issues](../../issues)
- 💬 **Discussões**: [GitHub Discussions](../../discussions)

