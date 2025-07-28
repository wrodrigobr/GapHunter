# GapHunter - Análise Técnica de Poker com IA

![GapHunter Logo](https://img.shields.io/badge/GapHunter-Poker%20Analysis-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## 📋 Visão Geral

GapHunter é uma plataforma avançada para análise técnica de mãos de poker, focada em jogadores de torneios online (MTTs). Utilizando inteligência artificial e princípios de GTO (Game Theory Optimal), o sistema identifica gaps recorrentes no jogo dos usuários e fornece feedback técnico detalhado para melhoria contínua.

### 🎯 Principais Funcionalidades

- **Análise Automática de Mãos**: Upload de hand histories do PokerStars com análise por IA
- **Identificação de Gaps**: Sistema inteligente que identifica padrões problemáticos recorrentes
- **Feedback Técnico**: Análises detalhadas baseadas em estratégia GTO
- **Histórico Completo**: Armazenamento e consulta de todas as mãos analisadas
- **Interface Moderna**: Dashboard responsivo e intuitivo
- **Autenticação Segura**: Sistema de usuários com JWT

## 🏗️ Arquitetura

### Backend (FastAPI)
- **Framework**: FastAPI 0.104.1
- **Banco de Dados**: SQLite (desenvolvimento) / SQL Server (produção)
- **Autenticação**: JWT com bcrypt
- **IA**: Integração com OpenRouter (Mistral)
- **ORM**: SQLAlchemy 2.0

### Frontend (React)
- **Framework**: React 18 com Vite
- **UI Components**: shadcn/ui + Tailwind CSS
- **Gerenciamento de Estado**: React Hooks + Context API
- **HTTP Client**: Axios
- **Roteamento**: React Router DOM

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.11+
- Node.js 20+
- pnpm (recomendado)

### 1. Configuração do Backend

```bash
cd backend
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Iniciar servidor
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Configuração do Frontend

```bash
cd frontend
pnpm install

# Iniciar servidor de desenvolvimento
pnpm run dev --host
```

### 3. Acessar a Aplicação

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Documentação da API: http://localhost:8000/docs

## 📁 Estrutura do Projeto

```
gaphunter/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── routers/        # Endpoints da API
│   │   ├── services/       # Lógica de negócio
│   │   ├── utils/          # Utilitários
│   │   └── main.py         # Aplicação principal
│   ├── requirements.txt    # Dependências Python
│   └── .env               # Configurações
├── frontend/               # Interface React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── hooks/          # Hooks customizados
│   │   ├── lib/           # Utilitários e API
│   │   └── App.jsx        # Componente principal
│   ├── package.json       # Dependências Node.js
│   └── vite.config.js     # Configuração Vite
└── README.md              # Este arquivo
```

## 🔧 Configuração

### Variáveis de Ambiente (Backend)

```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./gaphunter.db
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### Configuração da IA

Para utilizar as funcionalidades de análise por IA, você precisa:

1. Criar uma conta no [OpenRouter](https://openrouter.ai)
2. Obter uma API key
3. Configurar a variável `OPENROUTER_API_KEY` no arquivo `.env`

## 📖 Como Usar

### 1. Criar Conta
- Acesse a aplicação e clique em "Cadastre-se"
- Preencha os dados e crie sua conta

### 2. Upload de Hand History
- Faça login na aplicação
- Vá para a aba "Upload de Mãos"
- Selecione ou arraste um arquivo .txt com suas mãos do PokerStars
- Clique em "Analisar" para processar

### 3. Visualizar Análises
- Acesse a aba "Histórico" para ver todas as mãos analisadas
- Clique em "Ver Análise" para detalhes completos
- Visualize feedback da IA e sugestões de melhoria

### 4. Identificar Gaps
- O sistema automaticamente identifica padrões problemáticos
- Acesse endpoints `/api/gaps/analyze` para análise detalhada
- Visualize resumo de gaps em `/api/gaps/summary`

## 🎮 Obtendo Hand Histories do PokerStars

1. Abra o PokerStars
2. Vá em "Opções" → "Histórico de Mãos"
3. Selecione o período desejado
4. Clique em "Solicitar Mãos"
5. Baixe o arquivo .txt quando estiver pronto
6. Faça upload no GapHunter

## 🔍 API Endpoints

### Autenticação
- `POST /api/auth/register` - Criar conta
- `POST /api/auth/login` - Fazer login
- `GET /api/auth/me` - Dados do usuário atual

### Mãos
- `POST /api/hands/upload` - Upload de hand history
- `GET /api/hands/history/my-hands` - Listar mãos do usuário
- `GET /api/hands/history/my-hands/{id}` - Detalhes de uma mão
- `DELETE /api/hands/history/my-hands/{id}` - Deletar mão

### Gaps
- `GET /api/gaps/analyze` - Analisar gaps recorrentes
- `GET /api/gaps/summary` - Resumo dos gaps
- `GET /api/gaps/my-gaps` - Listar todos os gaps

### Usuários
- `GET /api/users/profile` - Perfil do usuário
- `GET /api/users/stats` - Estatísticas do usuário

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Para suporte e dúvidas:
- Abra uma [issue](https://github.com/seu-usuario/gaphunter/issues)
- Entre em contato: suporte@gaphunter.com

## 🔮 Roadmap

### Versão 1.1
- [ ] Suporte para outras plataformas (888poker, GGPoker)
- [ ] Análise de ROI e performance
- [ ] Módulo para coaches
- [ ] Sistema de assinatura

### Versão 1.2
- [ ] GapHunter Vision (análise de oponentes)
- [ ] GapHunter Club (programa de afiliados)
- [ ] Modo demonstrativo
- [ ] Análise avançada de ICM

---

**GapHunter** - Desenvolvido com ❤️ para a comunidade de poker

