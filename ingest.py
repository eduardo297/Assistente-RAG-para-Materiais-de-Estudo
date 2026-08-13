"""
Lê os arquivos da pasta 'materiais/', quebra o texto em pedaços
(chunks), gera embeddings e salva tudo em um banco vetorial local
(ChromaDB).

Como usar:
1. Coloque seus materiais dentro da pasta 'materiais/'
2. Rode: python ingest.py
"""

import os

os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from chromadb.utils import embedding_functions

import ingestion.loader as loader


PASTA_MATERIAIS = "materiais"
PASTA_BANCO = "banco_vetorial"

TAMANHO_CHUNK = 800
SOBREPOSICAO = 100

EXTENSOES_SUPORTADAS = {
    ".pdf",
    ".docx",
    ".txt",
    ".pptx"
}


def quebrar_em_chunks(
    informacoes: list[dict],
    tamanho: int,
    sobreposicao: int
) -> list[dict]:
    """Agrupa parágrafos em chunks mantendo sobreposição e metadados."""

    chunks = []

    chunk_atual = ""
    metadados_atual = []

    for informacao in informacoes:

        texto = informacao["texto"].strip()

        if not texto:
            continue

        candidato = (
            chunk_atual + "\n\n" + texto
            if chunk_atual
            else texto
        )

        if len(candidato) <= tamanho:

            chunk_atual = candidato

            metadados_atual.append(
                informacao["metadados"]
            )

        else:

            if chunk_atual:
                chunks.append({
                    "texto": chunk_atual.strip(),
                    "metadados": metadados_atual.copy()
                })

            overlap = (
                chunk_atual[-sobreposicao:]
                if chunk_atual
                else ""
            )

            chunk_atual = (
                overlap + "\n\n" + texto
                if overlap
                else texto
            )

            metadados_atual = [
                informacao["metadados"]
            ]

    if chunk_atual:
        chunks.append({
            "texto": chunk_atual.strip(),
            "metadados": metadados_atual.copy()
        })

    return chunks


def main():

    if not os.path.isdir(PASTA_MATERIAIS):
        os.makedirs(PASTA_MATERIAIS)

        print(
            f"Criei a pasta '{PASTA_MATERIAIS}/'. "
            "Coloque seus materiais lá e rode o script novamente."
        )

        return

    arquivos = [
        f
        for f in os.listdir(PASTA_MATERIAIS)
        if os.path.splitext(f)[1].lower()
        in EXTENSOES_SUPORTADAS
    ]

    if not arquivos:
        print(
            f"Nenhum material encontrado em "
            f"'{PASTA_MATERIAIS}/'."
        )

        return

    # Cliente do ChromaDB salvando localmente em disco
    cliente = chromadb.PersistentClient(
        path=PASTA_BANCO
    )

    # Embeddings locais
    funcao_embedding = (
        embedding_functions
        .SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    )

    colecao = cliente.get_or_create_collection(
        name="materiais_estudo",
        embedding_function=funcao_embedding,
    )

    total_chunks = 0

    for nome_arquivo in arquivos:

        caminho = os.path.join(
            PASTA_MATERIAIS,
            nome_arquivo
        )

        print(f"Processando: {nome_arquivo}")

        extensao = os.path.splitext(nome_arquivo)[1].lower()

        loader_func = loader.retornar_loader_por_extensao(
            extensao
        )

        if not loader_func:
            print(
                f"  -> Arquivo '{nome_arquivo}' "
                "tem extensão não suportada."
            )
            continue

        # Loader retorna:
        # [
        #     {
        #         "texto": "...",
        #         "metadados": {...}
        #     }
        # ]
        informacoes = loader_func(caminho)

        chunks = quebrar_em_chunks(
            informacoes,
            TAMANHO_CHUNK,
            SOBREPOSICAO
        )

        ids = [
            f"{nome_arquivo}_chunk_{i}"
            for i in range(len(chunks))
        ]

        documentos = [
            chunk["texto"]
            for chunk in chunks
        ]

        metadados = []

        for i, chunk in enumerate(chunks):

            metadata = {
                "fonte": nome_arquivo,
                "chunk_num": i
            }

            # Utiliza os metadados do primeiro
            # elemento que originou o chunk.
            if chunk["metadados"]:

                primeiro_metadata = (
                    chunk["metadados"][0]
                )

                for chave, valor in primeiro_metadata.items():
                    metadata[chave] = valor

            metadados.append(metadata)

        if documentos:

            colecao.upsert(
                documents=documentos,
                ids=ids,
                metadatas=metadados
            )

            total_chunks += len(documentos)

            print(
                f"  -> {len(documentos)} pedaços indexados"
            )

    print(
        f"\nConcluído! {total_chunks} pedaços "
        f"de texto indexados em '{PASTA_BANCO}/'."
    )


if __name__ == "__main__":
    main()