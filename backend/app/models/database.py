from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import urllib.parse

# Carregar variáveis de ambiente
load_dotenv()

# URL do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gaphunter.db")

# Configurações específicas para diferentes bancos
if DATABASE_URL.startswith("mssql") or DATABASE_URL.startswith("sqlserver"):
    # Azure SQL Database - Configuração otimizada para custo
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=5,  # Reduzido para economizar conexões
        max_overflow=10,  # Reduzido para economizar recursos
        echo=os.getenv("DEBUG", "False").lower() == "true",
        connect_args={
            "driver": "ODBC Driver 18 for SQL Server",
            "TrustServerCertificate": "yes",
            "Connection Timeout": 30,
            "Command Timeout": 30
        }
    )
elif DATABASE_URL.startswith("postgresql"):
    # PostgreSQL (fallback)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
        echo=os.getenv("DEBUG", "False").lower() == "true"
    )
elif DATABASE_URL.startswith("mysql"):
    # MySQL (fallback)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=5,
        max_overflow=10,
        echo=os.getenv("DEBUG", "False").lower() == "true"
    )
else:
    # SQLite (desenvolvimento)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DEBUG", "False").lower() == "true"
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

