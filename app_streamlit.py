import streamlit as st
from app.core.assistente import inicializar, responder_pergunta
import os
import ingest  # Importa o módulo onde fica a função main()[cite: 3]

st.set_page_config(page_title="Assistente de Estudos", page_icon="📚")
st.title("📚 Assistente de Estudos")

# Carrega cliente Gemini e coleção UMA vez[cite: 1, 2]
@st.cache_resource
def carregar_recursos():
    return inicializar()

cliente_gemini, colecao = carregar_recursos()

# --- BARRA LATERAL (INGEST / UPLOAD) ---
with st.sidebar:
    st.header("⚙️ Gerenciar Materiais")
    
    arquivos_enviados = st.file_uploader(
        "Envie seus documentos",
        type=["pdf", "docx", "txt", "pptx"],
        accept_multiple_files=True
    )
    
    if st.button("📥 Processar Materiais"):
        if arquivos_enviados:
            with st.spinner("Processando e indexando documentos..."):
                os.makedirs("materiais", exist_ok=True)
                for arq in arquivos_enviados:
                    caminho = os.path.join("materiais", arq.name)
                    with open(caminho, "wb") as f:
                        f.write(arq.getbuffer())
                
                # Executa o pipeline de indexação
                ingest.main()
                
            st.success("Documentos processados e atualizados com sucesso!")
        else:
            st.warning("Selecione ao menos um arquivo antes de processar.")

# --- HISTÓRICO E CHAT ---
if "historico" not in st.session_state:
    st.session_state.historico = []

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