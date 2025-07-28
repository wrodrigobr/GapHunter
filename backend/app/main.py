from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from app.routers import auth, hands, users, gaps, performance, coaching
from app.routers import subscription as subscription_router
from app.models.database import engine, Base

# Carregar variáveis de ambiente
load_dotenv()

# Importar todos os modelos para criação das tabelas
from app.models import user, hand, gap, tournament, coach
from app.models import subscription as subscription_model

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
app.include_router(subscription_router.router, prefix="/api/subscription", tags=["subscription"])

@app.get("/")
async def root():
    return {"message": "GapHunter API - Análise Técnica de Poker"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/admin/migrate")
async def run_migrations():
    """Executa migrações do banco de dados"""
    try:
        import subprocess
        import os
        
        # Mudar para diretório do backend se necessário
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        original_dir = os.getcwd()
        
        try:
            os.chdir(backend_dir)
            
            # Executar migrações do Alembic
            result = subprocess.run(
                ["alembic", "upgrade", "head"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            return {
                "status": "success",
                "message": "Migrações executadas com sucesso",
                "output": result.stdout
            }
            
        finally:
            os.chdir(original_dir)
            
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": "Erro ao executar migrações",
            "error": e.stderr,
            "output": e.stdout
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Erro interno",
            "error": str(e)
        }

@app.get("/admin/db-status")
async def check_database_status():
    """Verifica status do banco de dados"""
    try:
        from app.models.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        try:
            # Teste simples de conexão
            db.execute(text("SELECT 1"))
            
            # Verificar se tabelas existem
            tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'dbo'
            """)
            result = db.execute(tables_query)
            tables = [row[0] for row in result.fetchall()]
            
            return {
                "status": "connected",
                "message": "Banco de dados conectado",
                "tables": tables,
                "table_count": len(tables)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        return {
            "status": "error",
            "message": "Erro de conexão com banco",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

