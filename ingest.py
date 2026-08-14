"""
Lê os arquivos da pasta 'materiais/', quebra o texto em pedaços
(chunks), gera embeddings e salva tudo em um banco vetorial local
(ChromaDB).

Como usar:

1. Coloque seus materiais dentro da pasta 'materiais/'
2. Rode: python ingest.py
"""

import os

import app.embeddings.embedding_model as embedding_model
import app.ingestion.loader as loader
from app.database.chroma import criar_cliente_chroma, obter_colecao


PASTA_MATERIAIS = "materiais"

TAMANHO_CHUNK = 800
SOBREPOSICAO = 100

EXTENSOES_SUPORTADAS = {
    ".pdf",
    ".docx",
    ".txt",
    ".pptx"
}

import re


def dividir_texto_grande(
    texto: str,
    tamanho: int
) -> list[str]:
    """
    Divide um texto grande em partes menores,
    tentando respeitar as frases.
    """

    if len(texto) <= tamanho:
        return [texto]

    # Divide o texto em frases.
    frases = re.split(
        r'(?<=[.!?])\s+',
        texto
    )

    partes = []
    parte_atual = ""

    for frase in frases:

        frase = frase.strip()

        if not frase:
            continue

        candidato = (
            parte_atual + " " + frase
            if parte_atual
            else frase
        )

        if len(candidato) <= tamanho:

            parte_atual = candidato

        else:

            if parte_atual:
                partes.append(
                    parte_atual.strip()
                )

            # Caso uma frase sozinha seja maior
            # que o tamanho máximo.
            if len(frase) > tamanho:

                inicio = 0

                while inicio < len(frase):

                    fim = inicio + tamanho

                    partes.append(
                        frase[inicio:fim].strip()
                    )

                    inicio = fim

                parte_atual = ""

            else:

                parte_atual = frase

    if parte_atual:
        partes.append(
            parte_atual.strip()
        )

    return partes



def quebrar_em_chunks(
    informacoes: list[dict],
    tamanho: int,
    sobreposicao: int
) -> list[dict]:
    """Agrupa parágrafos em chunks respeitando limites de frases."""

    chunks = []

    chunk_atual = ""
    metadados_atual = []

    for informacao in informacoes:

        texto = informacao["texto"].strip()

        if not texto:
            continue

        # Se o parágrafo for maior que o tamanho do chunk,
        # divide primeiro em partes menores.
        partes = dividir_texto_grande(
            texto,
            tamanho
        )

        for parte in partes:

            candidato = (
                chunk_atual + "\n\n" + parte
                if chunk_atual
                else parte
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

                # Sobreposição entre chunks.
                overlap = (
                    chunk_atual[-sobreposicao:]
                    if chunk_atual
                    else ""
                )

                chunk_atual = (
                    overlap + "\n\n" + parte
                    if overlap
                    else parte
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

   

    funcao_embedding = (
        embedding_model.criar_funcao_embedding()
    )

    

    cliente = criar_cliente_chroma()

    colecao = obter_colecao(
        cliente,
        funcao_embedding
    )

  

    total_chunks = 0

    for nome_arquivo in arquivos:

        caminho = os.path.join(
            PASTA_MATERIAIS,
            nome_arquivo
        )

        print(
            f"\nProcessando: {nome_arquivo}"
        )

        extensao = os.path.splitext(
            nome_arquivo
        )[1].lower()

       

        loader_func = (
            loader.retornar_loader_por_extensao(
                extensao
            )
        )

        if not loader_func:

            print(
                f"  -> Arquivo '{nome_arquivo}' "
                "tem extensão não suportada."
            )

            continue

        try:
            informacoes = loader_func(caminho)
        except Exception as erro:
            # Um arquivo corrompido ou ilegível não deve travar o
            # processamento dos demais — pula e continua o loop.
            print(
                f"  -> Erro ao ler '{nome_arquivo}': {erro}"
            )
            continue

        if not informacoes:

            print(
                "  -> Nenhum texto encontrado."
            )

            continue

       
        chunks = quebrar_em_chunks(
            informacoes,
            TAMANHO_CHUNK,
            SOBREPOSICAO
        )

        if not chunks:

            print(
                "  -> Nenhum chunk gerado."
            )

            continue

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
                "tipo": extensao.replace(".", ""),
                "chunk_num": i
            }

            if chunk["metadados"]:

                primeiro = chunk["metadados"][0]
                ultimo = chunk["metadados"][-1]

                # Parágrafos
                if "paragrafo" in primeiro:

                    metadata["paragrafo_inicial"] = (
                        primeiro["paragrafo"]
                    )

                    metadata["paragrafo_final"] = (
                        ultimo["paragrafo"]
                    )

                # Páginas
                if "pagina" in primeiro:

                    metadata["pagina_inicial"] = (
                        primeiro["pagina"]
                    )

                    metadata["pagina_final"] = (
                        ultimo["pagina"]
                    )

                # Slides
                if "slide" in primeiro:

                    metadata["slide_inicial"] = (
                        primeiro["slide"]
                    )

                    metadata["slide_final"] = (
                        ultimo["slide"]
                    )

            metadados.append(metadata)

        # Remove chunks antigos desse mesmo arquivo antes de reinserir.
        # Evita "chunks órfãos" quando o novo chunking gera menos
        # pedaços do que da vez anterior (ex: arquivo editado).
        colecao.delete(where={"fonte": nome_arquivo})
    
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
        "de texto indexados no ChromaDB."
    )


if __name__ == "__main__":
    main()