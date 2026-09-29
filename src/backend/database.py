from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Cria o arquivo sqlite local "cofre.db" na raiz do projeto
SQLALCHEMY_DATABASE_URL = "sqlite:///./cofre.db"

# connect_args={"check_same_thread": False} é necessário apenas para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency do FastAPI para abrir e fechar conexões com o banco por requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()