"""
Faz perguntas sobre os materiais indexados.

Como usar:

1. Rode ingest.py primeiro
2. Crie um arquivo .env com:
   GEMINI_API_KEY=sua_chave_aqui
3. Rode:
   python query.py
"""

from app.retrieval.vector_search import buscar_documentos
from app.generation.gemini import (
    criar_cliente,
    gerar_resposta
)


QTD_CHUNKS_RECUPERADOS = 4


def main():

    cliente_gemini = criar_cliente()

    print(
        "Assistente de estudos pronto. "
        "Digite 'sair' para encerrar.\n"
    )

    while True:

        pergunta = input(
            "Sua pergunta: "
        ).strip()

        if pergunta.lower() in (
            "sair",
            "exit",
            "quit"
        ):
            break

        if not pergunta:
            continue


        resultado = buscar_documentos(
            pergunta,
            quantidade=QTD_CHUNKS_RECUPERADOS
        )

        trechos_recuperados = resultado["documents"][0]     
        metadados_recuperados = resultado["metadatas"][0]

        if not trechos_recuperados:

            print(
                "Nada relevante encontrado "
                "nos materiais.\n"
            )

            continue


        resposta = gerar_resposta(
            cliente_gemini,
            pergunta,
            trechos_recuperados
        )

        print(
            f"\nResposta: {resposta}\n"
        )

        print("Fontes:")

        for metadata in metadados_recuperados:

            fonte = metadata.get("fonte", "desconhecida")
            paragrafo = metadata.get("paragrafo")

            print(f"  📄 {fonte}", end="")

            if paragrafo:
                print(f" — parágrafo {paragrafo}", end="")

        print()


if __name__ == "__main__":
    main()