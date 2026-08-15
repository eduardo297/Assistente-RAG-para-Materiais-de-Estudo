from chromadb.utils import embedding_functions


def criar_funcao_embedding():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="intfloat/multilingual-e5-small"
    )