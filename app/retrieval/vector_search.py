from app.database.chroma import criar_cliente, obter_colecao
from app.embeddings.embedding_model import criar_funcao_embedding


def buscar_documentos(pergunta: str, quantidade: int = 5):
    """
    Busca no ChromaDB os documentos mais semelhantes
    semanticamente à pergunta.
    """

    # Cria o modelo de embedding
    funcao_embedding = criar_funcao_embedding()

    # Conecta ao ChromaDB
    cliente = criar_cliente()

    # Obtém a coleção
    colecao = obter_colecao(
        cliente,
        funcao_embedding
    )

    # Realiza a busca vetorial
    resultado = colecao.query(
        query_texts=[pergunta],
        n_results=quantidade
    )

    return resultado