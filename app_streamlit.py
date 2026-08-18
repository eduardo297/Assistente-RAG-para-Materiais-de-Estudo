import streamlit as st
from app.core.assistente import inicializar, responder_pergunta

st.set_page_config(page_title="Assistente de Estudos", page_icon="📚")
st.title("📚 Assistente de Estudos")

# Carrega cliente Gemini e coleção UMA vez, mantendo em cache
# entre reruns do Streamlit (evita recarregar o modelo a cada pergunta).
@st.cache_resource
def carregar_recursos():
    return inicializar()

cliente_gemini, colecao = carregar_recursos()

if "historico" not in st.session_state:
    st.session_state.historico = []

# Renderiza o histórico da conversa
for mensagem in st.session_state.historico:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])
        if mensagem.get("fontes"):
            with st.expander("📄 Fontes"):
                for f in mensagem["fontes"]:
                    linha = f"**{f['fonte']}**"
                    if f["paragrafo"]:
                        linha += f" — parágrafo {f['paragrafo']}"
                    linha += f" (distância: {f['distancia']:.3f}, score: {f['score']:.3f})"
                    st.markdown(linha)

pergunta = st.chat_input("Faça uma pergunta sobre seus materiais...")

if pergunta:
    st.session_state.historico.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando nos materiais..."):
            resultado = responder_pergunta(cliente_gemini, colecao, pergunta)

        if resultado["resposta"] is None:
            texto = "Nada relevante encontrado nos materiais."
            st.markdown(texto)
            st.session_state.historico.append({"role": "assistant", "content": texto})
        else:
            st.markdown(resultado["resposta"])
            with st.expander("📄 Fontes"):
                for f in resultado["fontes"]:
                    linha = f"**{f['fonte']}**"
                    if f["paragrafo"]:
                        linha += f" — parágrafo {f['paragrafo']}"
                    linha += f" (distância: {f['distancia']:.3f}, score: {f['score']:.3f})"
                    st.markdown(linha)

            st.session_state.historico.append({
                "role": "assistant",
                "content": resultado["resposta"],
                "fontes": resultado["fontes"],
            })