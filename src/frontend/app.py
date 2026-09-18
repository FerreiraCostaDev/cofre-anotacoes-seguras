import streamlit as st
import requests

API_URL = "https://cofre-anotacoes-seguras.onrender.com/api"

st.set_page_config(page_title="Cofre de Notas Seguras", page_icon="🔐")
st.title("🔐 Cofre de Anotações Seguras")

if "token" not in st.session_state:
    st.session_state["token"] = None

# --- BARRA LATERAL & LOGOFF ---
st.sidebar.title("Navegação")
menu = st.sidebar.selectbox("Opções", ["Login", "Cadastro", "Minhas Anotações"])

if st.session_state["token"]:
    st.sidebar.divider()
    st.sidebar.success("🔒 Sessão Ativa")
    if st.sidebar.button("🚪 Sair (Logoff)", use_container_width=True):
        st.session_state["token"] = None
        st.success("Sessão encerrada com sucesso!")
        st.rerun()

# --- CADASTRO ---
if menu == "Cadastro":
    st.subheader("Criar Nova Conta")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Cadastrar"):
            try:
                res = requests.post(
                    f"{API_URL}/registrar", 
                    json={"nome": nome, "email": email, "senha": senha},
                    timeout=10
                )
                
                if res.status_code in [200, 201]:
                    st.success("Cadastro realizado com sucesso! Faça login para continuar.")
                else:
                    try:
                        dados_erro = res.json()
                        st.error(dados_erro.get("detail", "Erro no cadastro"))
                    except ValueError:
                        st.error(f"Erro no servidor ({res.status_code}): {res.text}")

            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao servidor backend (FastAPI).")

# --- LOGIN ---
elif menu == "Login":
    st.subheader("Acesso ao Sistema")
    with st.form("form_login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            try:
                res = requests.post(
                    f"{API_URL}/login", 
                    json={"email": email, "senha": senha},
                    timeout=10
                )
                
                if res.status_code == 200:
                    try:
                        st.session_state["token"] = res.json().get("access_token")
                        st.success("Login efetuado com sucesso!")
                        st.rerun()
                    except ValueError:
                        st.error("Resposta inválida do servidor.")
                else:
                    try:
                        dados_erro = res.json()
                        st.error(dados_erro.get("detail", "Credenciais inválidas."))
                    except ValueError:
                        st.error(f"Erro no servidor ({res.status_code}): {res.text}")

            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao servidor backend (FastAPI).")

# --- MINHAS ANOTAÇÕES ---
elif menu == "Minhas Anotações":
    st.subheader("📝 Suas Anotações Privadas")
    if not st.session_state["token"]:
        st.warning("Você precisa fazer login para acessar esta área.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        
        with st.expander("➕ Nova Anotação"):
            with st.form("form_nota"):
                titulo = st.text_input("Título")
                conteudo = st.text_area("Conteúdo Sigiloso")
                if st.form_submit_button("Salvar Anotação"):
                    try:
                        res = requests.post(
                            f"{API_URL}/notas", 
                            json={"titulo": titulo, "conteudo": conteudo}, 
                            headers=headers,
                            timeout=10
                        )
                        if res.status_code in [200, 201]:
                            st.success("Anotação salva!")
                            st.rerun()
                        else:
                            st.error("Erro ao salvar anotação.")
                    except requests.exceptions.ConnectionError:
                        st.error("Erro de conexão ao salvar anotação.")

        try:
            res = requests.get(f"{API_URL}/notas", headers=headers, timeout=10)
            if res.status_code == 200:
                try:
                    notas = res.json().get("notas", [])
                    if not notas:
                        st.info("Nenhuma anotação cadastrada até o momento.")
                    for n in notas:
                        st.write(f"### {n['titulo']}")
                        st.code(n['conteudo'])
                        
                        col1, col2 = st.columns([1, 4])
                        
                        # Excluir
                        with col1:
                            if st.button("🗑️ Excluir", key=f"del_{n['id']}"):
                                del_res = requests.delete(f"{API_URL}/notas/{n['id']}", headers=headers)
                                if del_res.status_code == 200:
                                    st.success("Nota excluída!")
                                    st.rerun()
                                else:
                                    st.error("Erro ao excluir nota.")

                        # Editar
                        with col2:
                            with st.popover("✏️ Editar"):
                                novo_t = st.text_input("Título", value=n['titulo'], key=f"t_{n['id']}")
                                novo_c = st.text_area("Conteúdo", value=n['conteudo'], key=f"c_{n['id']}")
                                if st.button("Salvar", key=f"btn_edit_{n['id']}"):
                                    edit_res = requests.put(
                                        f"{API_URL}/notas/{n['id']}", 
                                        json={"titulo": novo_t, "conteudo": novo_c}, 
                                        headers=headers
                                    )
                                    if edit_res.status_code == 200:
                                        st.success("Nota atualizada!")
                                        st.rerun()
                                    else:
                                        st.error("Erro ao atualizar nota.")
                                        
                        st.divider()
                except ValueError:
                    st.error("Erro ao ler as anotações do servidor.")
            else:
                st.error("Sessão expirada ou não autorizada. Faça login novamente.")
        except requests.exceptions.ConnectionError:
            st.error("Não foi possível carregar as anotações. Backend inacessível.")