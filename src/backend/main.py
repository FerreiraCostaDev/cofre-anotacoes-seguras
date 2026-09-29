from fastapi import FastAPI, HTTPException, status, Depends, Header
from typing import Optional
from pydantic import BaseModel
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from config.settings import settings
from src.backend.database import engine, Base, get_db
from src.backend.models import UsuarioModel, NotaModel
from src.backend.security import (
    UsuarioRegistroSchema,
    gerar_hash_senha,
    verificar_senha,
    criar_token_acesso
)

# Cria as tabelas no SQLite no startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MVP - Cofre de Anotações Seguras")

class NotaSchema(BaseModel):
    titulo: str
    conteudo: str

def obter_usuario_atual(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente ou inválido.")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido.")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Sessão expirada ou inválida.")

# --- REGISTRO ---
@app.post("/api/registrar", status_code=201)
def registrar(usuario: UsuarioRegistroSchema, db: Session = Depends(get_db)):
    user_existente = db.query(UsuarioModel).filter(UsuarioModel.email == usuario.email).first()
    if user_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")
    
    novo_usuario = UsuarioModel(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=gerar_hash_senha(usuario.senha)
    )
    db.add(novo_usuario)
    db.commit()
    return {"mensagem": "Usuário cadastrado com sucesso!"}

# --- LOGIN ---
@app.post("/api/login")
def login(dados: dict, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.email == dados.get("email")).first()
    if not usuario or not verificar_senha(dados.get("senha", ""), usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    
    token = criar_token_acesso(data={"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}

# --- CRIAR NOTA ---
@app.post("/api/notas", status_code=201)
def criar_nota(
    nota: NotaSchema, 
    usuario_email: str = Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    nova_nota = NotaModel(
        titulo=nota.titulo,
        conteudo=nota.conteudo,
        usuario_email=usuario_email
    )
    db.add(nova_nota)
    db.commit()
    db.refresh(nova_nota)
    return {"mensagem": "Nota salva com sucesso!", "nota": {"id": nova_nota.id, "titulo": nova_nota.titulo, "conteudo": nova_nota.conteudo}}

# --- LISTAR NOTAS ---
@app.get("/api/notas")
def listar_notas(
    usuario_email: str = Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    notas = db.query(NotaModel).filter(NotaModel.usuario_email == usuario_email).all()
    return {"notas": [{"id": n.id, "titulo": n.titulo, "conteudo": n.conteudo} for n in notas]}

# --- ATUALIZAR NOTA ---
@app.put("/api/notas/{nota_id}")
def atualizar_nota(
    nota_id: int, 
    nota_atualizada: NotaSchema, 
    usuario_email: str = Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    nota = db.query(NotaModel).filter(NotaModel.id == nota_id, NotaModel.usuario_email == usuario_email).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota não encontrada.")
    
    nota.titulo = nota_atualizada.titulo
    nota.conteudo = nota_atualizada.conteudo
    db.commit()
    return {"mensagem": "Nota atualizada com sucesso!"}

# --- EXCLUIR NOTA ---
@app.delete("/api/notas/{nota_id}")
def deletar_nota(
    nota_id: int, 
    usuario_email: str = Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    nota = db.query(NotaModel).filter(NotaModel.id == nota_id, NotaModel.usuario_email == usuario_email).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota não encontrada.")
    
    db.delete(nota)
    db.commit()
    return {"mensagem": "Nota excluída com sucesso!"}