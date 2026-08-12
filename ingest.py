"""
ingest.py
---------
Lê todos os PDFs da pasta 'materiais/', quebra o texto em pedaços
(chunks), gera embeddings e salva tudo num banco vetorial local (ChromaDB).

Como usar:
    1. Coloque seus PDFs dentro da pasta 'materiais/'
    2. Rode: python ingest.py
"""

import os
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions

PASTA_MATERIAIS = "materiais"
PASTA_BANCO = "banco_vetorial"
TAMANHO_CHUNK = 800        # caracteres por pedaço de texto
SOBREPOSICAO = 100         # sobreposição entre pedaços, ajuda a não cortar frases no meio


def extrair_texto_pdf(caminho_pdf: str) -> str:
    """Extrai todo o texto de um arquivo PDF."""
    leitor = PdfReader(caminho_pdf)
    texto_completo = ""
    for pagina in leitor.pages:
        texto_pagina = pagina.extract_text() or ""
        texto_completo += texto_pagina + "\n"
    return texto_completo


def quebrar_em_chunks(texto: str, tamanho: int, sobreposicao: int) -> list[str]:
    """Quebra um texto longo em pedaços menores, com sobreposição entre eles."""
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        chunk = texto[inicio:fim].strip()
        if chunk:
            chunks.append(chunk)
        inicio += tamanho - sobreposicao
    return chunks


def main():
    if not os.path.isdir(PASTA_MATERIAIS):
        os.makedirs(PASTA_MATERIAIS)
        print(f"Criei a pasta '{PASTA_MATERIAIS}/'. Coloque seus PDFs lá e rode o script de novo.")
        return

    arquivos_pdf = [f for f in os.listdir(PASTA_MATERIAIS) if f.lower().endswith(".pdf")]
    if not arquivos_pdf:
        print(f"Nenhum PDF encontrado em '{PASTA_MATERIAIS}/'. Adicione arquivos e rode novamente.")
        return

    # Cliente do ChromaDB salvando localmente em disco
    cliente = chromadb.PersistentClient(path=PASTA_BANCO)

    # Função de embedding local e gratuita (roda no seu computador, sem API)
    funcao_embedding = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    colecao = cliente.get_or_create_collection(
        name="materiais_estudo",
        embedding_function=funcao_embedding,
    )

    total_chunks = 0
    for nome_arquivo in arquivos_pdf:
        caminho = os.path.join(PASTA_MATERIAIS, nome_arquivo)
        print(f"Processando: {nome_arquivo}")

        texto = extrair_texto_pdf(caminho)
        chunks = quebrar_em_chunks(texto, TAMANHO_CHUNK, SOBREPOSICAO)

        ids = [f"{nome_arquivo}_chunk_{i}" for i in range(len(chunks))]
        metadados = [{"fonte": nome_arquivo, "chunk_num": i} for i in range(len(chunks))]

        if chunks:
            colecao.upsert(documents=chunks, ids=ids, metadatas=metadados)
            total_chunks += len(chunks)
            print(f"  -> {len(chunks)} pedaços indexados")

    print(f"\nConcluído! {total_chunks} pedaços de texto indexados em '{PASTA_BANCO}/'.")


if __name__ == "__main__":
    main()
