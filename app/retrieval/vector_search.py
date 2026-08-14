from app.database.chroma import criar_cliente_chroma, obter_colecao
from app.embeddings.embedding_model import criar_funcao_embedding


def conectar_colecao():
    """
    Cria o modelo de embedding, conecta ao ChromaDB e retorna a coleção
    pronta para uso. Chame isso UMA VEZ (fora do loop de perguntas) e
    reutilize a coleção retornada em cada chamada de buscar_documentos.
    """

    funcao_embedding = criar_funcao_embedding()
    cliente = criar_cliente_chroma()

    colecao = obter_colecao(
        cliente,
        funcao_embedding
    )

    return colecao


def buscar_documentos(colecao, pergunta: str, quantidade: int = 5, distancia_maxima: float | None = None):
    """
    Busca no ChromaDB os documentos mais semelhantes
    semanticamente à pergunta.

    'colecao' deve vir de conectar_colecao(), criada uma única vez
    fora do loop de perguntas, para não recarregar o modelo de
    embedding a cada pergunta.

    'distancia_maxima': se informado, descarta da resposta os chunks
    cuja distância for MAIOR que esse valor (ou seja, pouco similares
    à pergunta).
    """

    resultado = colecao.query(
        query_texts=[pergunta],
        n_results=quantidade,
        include=["documents", "metadatas", "distances"]
    )

    if distancia_maxima is None:
        return resultado

    documentos = resultado["documents"][0]
    metadados = resultado["metadatas"][0]
    distancias = resultado["distances"][0]

    documentos_filtrados = []
    metadados_filtrados = []
    distancias_filtradas = []

    for doc, meta, dist in zip(documentos, metadados, distancias):
        if dist <= distancia_maxima:
            documentos_filtrados.append(doc)
            metadados_filtrados.append(meta)
            distancias_filtradas.append(dist)

    resultado["documents"][0] = documentos_filtrados
    resultado["metadatas"][0] = metadados_filtrados
    resultado["distances"][0] = distancias_filtradas

    return resultado