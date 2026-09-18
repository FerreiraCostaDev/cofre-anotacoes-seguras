import re
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from pydantic import BaseModel, EmailStr, field_validator
from config.settings import settings

# Hash Seguro de Senhas (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash_senha(senha_plana: str) -> str:
    return pwd_context.hash(senha_plana)

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hash)

# Gestão de Sessão via Token JWT
def criar_token_acesso(data: dict) -> str:
    para_codificar = data.copy()
    expiracao = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    para_codificar.update({"exp": expiracao})
    return jwt.encode(para_codificar, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Validação e Sanitização de Entradas
class UsuarioRegistroSchema(BaseModel):
    email: EmailStr
    nome: str
    senha: str

    @field_validator('senha')
    def validar_senha(cls, v):
        if len(v) < 8:
            raise ValueError('A senha deve ter pelo menos 8 caracteres.')
        return v

    @field_validator('nome')
    def sanitizar_nome(cls, v):
        nome_limpo = re.sub(r'[<>]', '', v).strip()
        if not nome_limpo:
            raise ValueError('Nome inválido.')
        return nome_limpo