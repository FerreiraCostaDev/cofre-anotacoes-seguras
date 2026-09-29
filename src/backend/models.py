from sqlalchemy import Column, Integer, String, ForeignKey
from src.backend.database import Base

class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)

class NotaModel(Base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    conteudo = Column(String, nullable=False)
    usuario_email = Column(String, ForeignKey("usuarios.email"), nullable=False)