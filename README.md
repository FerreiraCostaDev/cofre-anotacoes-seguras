# 🔒 MVP - Cofre de Anotações Seguras

Sistema de Cofre de Anotações desenvolvido em Python aplicando o checklist de funções obrigatórias de Segurança da Informação.

## 🏗️ Estrutura do Projeto
- `src/backend/`: API REST em FastAPI com autenticação JWT e Hash Bcrypt.
- `src/frontend/`: Interface visual interativa desenvolvida em Streamlit.
- `config/`: Configurações e variáveis de ambiente.
- `tests/`: Testes automatizados de segurança.
- `docs/`: Documentação e checklist de SI.

## 🚀 Como Executar
1. Instalar dependências: `pip install -r requirements.txt`
2. Rodar Backend: `python -m uvicorn src.backend.main:app --reload --port 8000`
3. Rodar Frontend: `streamlit run src/frontend/app.py`