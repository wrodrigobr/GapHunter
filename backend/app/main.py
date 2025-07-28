from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from app.routers import auth, hands, users, gaps, performance, coaching, subscription
from app.models.database import engine, Base

# Carregar variáveis de ambiente
load_dotenv()

# Importar todos os modelos para criação das tabelas
from app.models import user, hand, gap, tournament, coach, subscription

# Criar tabelas do banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GapHunter API",
    description="API para análise técnica de mãos de poker",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar diretório para uploads se não existir
os.makedirs("uploads", exist_ok=True)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(hands.router, prefix="/api/hands", tags=["hands"])
app.include_router(gaps.router, prefix="/api/gaps", tags=["gaps"])
app.include_router(performance.router, prefix="/api/performance", tags=["performance"])
app.include_router(coaching.router, prefix="/api/coaching", tags=["coaching"])
app.include_router(subscription.router, prefix="/api/subscription", tags=["subscription"])

@app.get("/")
async def root():
    return {"message": "GapHunter API - Análise Técnica de Poker"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

