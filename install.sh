#!/bin/bash

# GapHunter - Script de Instalação
# Este script automatiza a instalação e configuração do GapHunter

set -e

echo "🎯 GapHunter - Instalação Automática"
echo "======================================"

# Verificar pré-requisitos
echo "📋 Verificando pré-requisitos..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.11+"
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Por favor, instale Node.js 20+"
    exit 1
fi

# Verificar pnpm
if ! command -v pnpm &> /dev/null; then
    echo "📦 Instalando pnpm..."
    npm install -g pnpm
fi

echo "✅ Pré-requisitos verificados!"

# Configurar Backend
echo ""
echo "🔧 Configurando Backend..."
cd backend

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual Python..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Configurar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "⚙️ Criando arquivo de configuração..."
    cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./gaphunter.db
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
EOF
    echo "📝 Arquivo .env criado. Configure sua OPENROUTER_API_KEY!"
fi

cd ..

# Configurar Frontend
echo ""
echo "🎨 Configurando Frontend..."
cd frontend

# Instalar dependências
echo "📦 Instalando dependências Node.js..."
pnpm install

cd ..

# Criar scripts de execução
echo ""
echo "📜 Criando scripts de execução..."

# Script para iniciar backend
cat > start-backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
EOF

# Script para iniciar frontend
cat > start-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
pnpm run dev --host
EOF

# Script para iniciar ambos
cat > start-all.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando GapHunter..."

# Iniciar backend em background
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Aguardar backend iniciar
sleep 5

# Iniciar frontend
cd ../frontend
pnpm run dev --host &
FRONTEND_PID=$!

echo "✅ GapHunter iniciado!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Para parar os serviços, pressione Ctrl+C"

# Aguardar interrupção
trap "echo '🛑 Parando serviços...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

# Tornar scripts executáveis
chmod +x start-backend.sh start-frontend.sh start-all.sh

# Criar arquivo de exemplo de hand history
if [ ! -f "sample_hand.txt" ]; then
    echo "📄 Criando arquivo de exemplo..."
    cat > sample_hand.txt << 'EOF'
PokerStars Hand #123456789: Tournament #987654321, $5.00+$0.50 USD Hold'em No Limit - Level III (25/50) - 2025/07/28 10:30:00 ET
Table '987654321 1' 9-max Seat #3 is the button
Seat 1: Player1 (1500 in chips)
Seat 2: Player2 (1450 in chips)
Seat 3: Hero (1600 in chips)
Seat 4: Player4 (1400 in chips)
Seat 5: Player5 (1550 in chips)
Player4: posts small blind 25
Player5: posts big blind 50
*** HOLE CARDS ***
Dealt to Hero [As Kh]
Player1: folds
Player2: raises 100 to 150
Hero: calls 150
Player4: folds
Player5: folds
*** FLOP *** [Ah 7c 2d]
Player2: bets 200
Hero: raises 400 to 600
Player2: calls 400
*** TURN *** [Ah 7c 2d] [Kc]
Player2: checks
Hero: bets 850 and is all-in
Player2: folds
Uncalled bet (850) returned to Hero
Hero collected 1575 from pot
Hero: doesn't show hand
*** SUMMARY ***
Total pot 1575 | Rake 0
Board [Ah 7c 2d Kc]
Seat 1: Player1 folded before Flop (didn't bet)
Seat 2: Player2 folded on the Turn
Seat 3: Hero (button) collected (1575)
Seat 4: Player4 (small blind) folded before Flop
Seat 5: Player5 (big blind) folded before Flop
EOF
fi

echo ""
echo "🎉 Instalação concluída com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure sua OPENROUTER_API_KEY no arquivo backend/.env"
echo "2. Execute './start-all.sh' para iniciar a aplicação"
echo "3. Acesse http://localhost:5173 para usar o GapHunter"
echo ""
echo "📚 Documentação completa disponível no README.md"
echo ""
echo "🆘 Suporte: https://github.com/seu-usuario/gaphunter/issues"

