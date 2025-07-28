# 🎯 GapHunter - Plataforma de Análise de Poker

Uma plataforma completa para análise de hand histories de poker com IA, identificação automática de gaps e sistema de coaching.

## 🚀 Deploy Rápido no Azure

### Opção 1: GitHub Actions (Recomendado)
```bash
# 1. Configure os secrets no GitHub (ver GITHUB_ACTIONS_SETUP.md)
# 2. Faça push no repositório
git push origin master
# 3. Deploy automático será executado
```

### Opção 2: Script Manual
```bash
# Deploy econômico ($15-30/mês)
chmod +x deploy-azure-budget.sh
export OPENROUTER_API_KEY="sua-chave"
./deploy-azure-budget.sh
```

## 💰 Custos Otimizados

| Recurso | Configuração | Custo/mês |
|---------|--------------|-----------|
| Azure SQL Database | Basic (5 DTU) | ~$5 |
| Container Apps Backend | 0.5 CPU, 1GB RAM | ~$8-12 |
| Container Apps Frontend | 0.25 CPU, 0.5GB RAM | ~$2-5 |
| Container Registry | Basic SKU | ~$5 |
| **Total** | **Scale-to-zero ativo** | **$15-30** |

## 🎯 Funcionalidades

### ✅ Core Features
- **GapHunter Core**: Identificação automática de gaps recorrentes
- **Upload de Hand History**: Parser completo do PokerStars
- **Análise de IA**: Integração com OpenRouter/Mistral
- **Sistema de Usuários**: Autenticação JWT completa

### ✅ ROI & Performance Tracker
- **Análise Financeira**: Buy-ins, premiações, ROI
- **Gráficos Temporais**: Evolução de performance
- **Estatísticas ITM**: In-the-money percentage
- **Adição Manual**: Resultados de torneios

### ✅ Módulo para Coaches
- **Perfis de Coach**: Especialidades e avaliações
- **Gestão de Alunos**: Acompanhamento de progresso
- **Sistema de Notas**: Categorizadas por prioridade
- **Análise de Gaps**: Por aluno individual

### ✅ GapHunter Vision (Modo Justo)
- **Configurações de Privacidade**: Controle granular
- **Análises Mútuas**: Sistema de reciprocidade
- **Jogadores Públicos**: Lista com estatísticas
- **Análise de Adversários**: Conhecidos de mesas regulares

### ✅ Sistema de Assinatura
- **5 Planos**: Free, Basic, Pro, Coach, Premium
- **Controle de Acesso**: Por funcionalidade
- **Pagamentos**: Sistema integrado
- **Upgrades**: Automáticos por plano

### ✅ GapHunter Club & Afiliados
- **Sistema de Afiliados**: 30% regular, 50% influenciador
- **4 Níveis**: Bronze, Silver, Gold, Diamond
- **Sistema de Pontos**: Progressão automática
- **Leaderboard**: Ranking dos membros
- **Comissionamento**: Automático por indicação

## 🏗️ Arquitetura

### Backend (FastAPI)
- **Framework**: FastAPI + SQLAlchemy
- **Banco**: Azure SQL Database (Basic)
- **IA**: OpenRouter/Mistral integration
- **Auth**: JWT com refresh tokens

### Frontend (React)
- **Framework**: React + Vite
- **UI**: Tailwind CSS + shadcn/ui
- **State**: Context API
- **Build**: Otimizado para produção

### Infraestrutura
- **Hosting**: Azure Container Apps
- **Database**: Azure SQL Database
- **Registry**: Azure Container Registry
- **CI/CD**: GitHub Actions

## 📚 Documentação

- **[DEPLOY_BUDGET_GUIDE.md](DEPLOY_BUDGET_GUIDE.md)**: Guia completo de deploy econômico
- **[GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)**: Configuração de CI/CD
- **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)**: Guia de deploy padrão
- **[AZURE_DEPLOYMENT_SUMMARY.md](AZURE_DEPLOYMENT_SUMMARY.md)**: Resumo técnico

## 🛠️ Desenvolvimento Local

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
pnpm install
pnpm dev
```

### Banco de Dados
```bash
# Migrações
cd backend
alembic upgrade head
```

## 🔧 Configuração

### Variáveis de Ambiente
```bash
# Backend (.env)
DATABASE_URL=sqlite:///./gaphunter.db
SECRET_KEY=sua-chave-secreta
OPENROUTER_API_KEY=sua-chave-openrouter

# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000/api
```

## 📊 Monitoramento

### Logs
```bash
# Backend logs
az containerapp logs show --name gaphunter-backend --resource-group gaphunter-rg --follow

# Frontend logs
az containerapp logs show --name gaphunter-frontend --resource-group gaphunter-rg --follow
```

### Custos
```bash
# Verificar gastos
az consumption usage list --top 10

# Configurar alertas
az consumption budget create --budget-name "GapHunter-Budget" --amount 50
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🎯 Roadmap

### Próximas Funcionalidades
- [ ] Importação de outras plataformas (888poker, GGPoker)
- [ ] IA ajustável por perfil de jogador
- [ ] Modo demonstrativo público
- [ ] Análise de evolução temporal
- [ ] Sistema de notificações

### Melhorias Técnicas
- [ ] Testes automatizados
- [ ] Monitoramento avançado
- [ ] Cache Redis
- [ ] CDN para assets
- [ ] Backup automático

---

**🎉 GapHunter - Transformando dados em vitórias!**

Para suporte ou dúvidas, abra uma issue no GitHub ou consulte a documentação completa.

