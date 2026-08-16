from sentence_transformers import CrossEncoder


modelo_reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

TOP_K = 3
LIMITADOR_DE_SCORE = -2


def reranking(documentos, pergunta: str):
    textos = documentos["documents"][0]

    if not textos:
        return documentos

    metadados = documentos["metadatas"][0]
    distancias = documentos["distances"][0]

    pares = [
        (pergunta, texto)
        for texto in textos
    ]

    pontuacoes = modelo_reranker.predict(pares)

    resultados = list(
        zip(
            textos,
            metadados,
            distancias,
            pontuacoes
        )
    )
    
    
    resultados.sort(
        key=lambda x: x[3],
        reverse=True
    )
    
    # Aplica o filtro de score mínimo e limita ao TOP_K
    melhores_resultados = [
        resultado for resultado in resultados 
        if resultado[3] >= LIMITADOR_DE_SCORE
    ][:TOP_K]

    documentos["documents"][0] = [
        resultado[0]
        for resultado in melhores_resultados
    ]

    documentos["metadatas"][0] = [
        resultado[1]
        for resultado in melhores_resultados
    ]

    documentos["distances"][0] = [
        resultado[2]
        for resultado in melhores_resultados
    ]

    documentos["reranking_scores"] = [[
        resultado[3]
        for resultado in melhores_resultados
    ]]

    return documentos