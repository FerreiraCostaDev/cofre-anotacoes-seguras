import re
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt
from pydantic import BaseModel, EmailStr, field_validator
from config.settings import settings

# Hash Seguro de Senhas usando bcrypt nativo
def gerar_hash_senha(senha_plana: str) -> str:
    # Converte para bytes e trunca em 72 bytes por limitação do algoritmo bcrypt
    senha_bytes = senha_plana.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(senha_bytes, salt)
    return hash_bytes.decode('utf-8')

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    senha_bytes = senha_plana.encode('utf-8')[:72]
    hash_bytes = senha_hash.encode('utf-8')
    return bcrypt.checkpw(senha_bytes, hash_bytes)

# Gestão de Sessão via Token JWT
def criar_token_acesso(data: dict) -> str:
    para_codificar = data.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
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