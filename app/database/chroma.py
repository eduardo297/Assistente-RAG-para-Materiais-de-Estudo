import chromadb


PASTA_BANCO = "database/chroma"
NOME_COLECAO = "materiais_estudo"


def criar_cliente():
    """Cria o cliente do ChromaDB persistido em disco."""

    cliente = chromadb.PersistentClient(
        path=PASTA_BANCO
    )

    return cliente


def obter_colecao(cliente, funcao_embedding):
    """Obtém ou cria a coleção dos materiais de estudo."""

    colecao = cliente.get_or_create_collection(
        name=NOME_COLECAO,
        embedding_function=funcao_embedding,
    )

    return colecao