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


def buscar_documentos(colecao, pergunta: str, quantidade: int = 5):
    """
    Busca no ChromaDB os documentos mais semelhantes
    semanticamente à pergunta.

    'colecao' deve vir de conectar_colecao(), criada uma única vez
    fora do loop de perguntas, para não recarregar o modelo de
    embedding a cada pergunta.
    """

    resultado = colecao.query(
        query_texts=[pergunta],
        n_results=quantidade
    )

    return resultado