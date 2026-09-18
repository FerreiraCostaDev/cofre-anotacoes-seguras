from fastapi import FastAPI, HTTPException, status, Depends, Header
from typing import Optional
from pydantic import BaseModel
from jose import jwt, JWTError
from config.settings import settings
from src.backend.security import (
    UsuarioRegistroSchema,
    gerar_hash_senha,
    verificar_senha,
    criar_token_acesso
)

app = FastAPI(title="MVP - Cofre de Anotações Seguras")

# Simulação de Banco de Dados
db_usuarios = {}
db_notas = []

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

@app.post("/api/registrar", status_code=201)
def registrar(usuario: UsuarioRegistroSchema):
    if usuario.email in db_usuarios:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")
    
    db_usuarios[usuario.email] = {
        "nome": usuario.nome,
        "email": usuario.email,
        "senha_hash": gerar_hash_senha(usuario.senha)
    }
    return {"mensagem": "Usuário cadastrado com sucesso!"}

@app.post("/api/login")
def login(dados: dict):
    usuario = db_usuarios.get(dados.get("email"))
    if not usuario or not verificar_senha(dados.get("senha", ""), usuario["senha_hash"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    
    token = criar_token_acesso(data={"sub": usuario["email"]})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/notas", status_code=201)
def criar_nota(nota: NotaSchema, usuario_email: str = Depends(obter_usuario_atual)):
    nova_nota = {
        "id": len(db_notas) + 1,
        "usuario": usuario_email,
        "titulo": nota.titulo,
        "conteudo": nota.conteudo
    }
    db_notas.append(nova_nota)
    return {"mensagem": "Nota salva com sucesso!", "nota": nova_nota}

@app.get("/api/notas")
def listar_notas(usuario_email: str = Depends(obter_usuario_atual)):
    notas_usuario = [n for n in db_notas if n["usuario"] == usuario_email]
    return {"notas": notas_usuario}

# --- ROTA DE EDIÇÃO DE NOTA (PUT) ---
@app.put("/api/notas/{nota_id}")
def atualizar_nota(nota_id: int, nota_atualizada: NotaSchema, usuario_email: str = Depends(obter_usuario_atual)):
    for n in db_notas:
        if n["id"] == nota_id and n["usuario"] == usuario_email:
            n["titulo"] = nota_atualizada.titulo
            n["conteudo"] = nota_atualizada.conteudo
            return {"mensagem": "Nota atualizada com sucesso!", "nota": n}
    raise HTTPException(status_code=404, detail="Nota não encontrada.")

# --- ROTA DE EXCLUSÃO DE NOTA (DELETE) ---
@app.delete("/api/notas/{nota_id}")
def deletar_nota(nota_id: int, usuario_email: str = Depends(obter_usuario_atual)):
    global db_notas
    nota_existente = next((n for n in db_notas if n["id"] == nota_id and n["usuario"] == usuario_email), None)
    if not nota_existente:
        raise HTTPException(status_code=404, detail="Nota não encontrada.")
    
    db_notas = [n for n in db_notas if not (n["id"] == nota_id and n["usuario"] == usuario_email)]
    return {"mensagem": "Nota excluída com sucesso!"}