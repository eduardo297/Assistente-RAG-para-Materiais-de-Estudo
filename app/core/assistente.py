from app.retrieval.vector_search import conectar_colecao, buscar_documentos
from app.generation.gemini import criar_cliente_gemini, gerar_resposta

QTD_CHUNKS_RECUPERADOS = 8
DISTANCIA_MAXIMA = 0.4


def inicializar():
    """Carrega cliente Gemini e coleção uma única vez."""
    cliente_gemini = criar_cliente_gemini()
    colecao = conectar_colecao()
    return cliente_gemini, colecao


def responder_pergunta(cliente_gemini, colecao, pergunta: str) -> dict:
    """Executa o pipeline RAG completo e retorna resposta + fontes."""

    resultado = buscar_documentos(
        colecao,
        pergunta,
        quantidade=QTD_CHUNKS_RECUPERADOS,
        distancia_maxima=DISTANCIA_MAXIMA
    )

    trechos = resultado["documents"][0]
    metadados = resultado["metadatas"][0]

    if not trechos:
        return {"resposta": None, "fontes": []}

    resposta = gerar_resposta(cliente_gemini, pergunta, trechos)

    distancias = resultado["distances"][0]
    scores = resultado["reranking_scores"][0]

    fontes = [
        {
            "fonte": m.get("fonte", "desconhecida"),
            "paragrafo": m.get("paragrafo"),
            "texto": t,
            "distancia": d,
            "score": s,
        }
        for m,t, d, s in zip(metadados, trechos, distancias, scores)
    ]

    return {"resposta": resposta, "fontes": fontes}