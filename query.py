"""
Faz perguntas sobre os materiais indexados.
 
Como usar:
 
1. Rode ingest.py primeiro
2. Crie um arquivo .env com:
   GEMINI_API_KEY=sua_chave_aqui
3. Rode:
   python query.py
"""
 
from app.retrieval.vector_search import (
    conectar_colecao,
    buscar_documentos
)
from app.generation.gemini import (
    criar_cliente_gemini,
    gerar_resposta
)
 
 
QTD_CHUNKS_RECUPERADOS = 4
DISTANCIA_MAXIMA = 1.1  # valor referente a distancia de cosseno (quanto menor, mais parecido com a pergunta)
 
def main():
 
    cliente_gemini = criar_cliente_gemini()
 
    # Conecta ao ChromaDB e carrega o modelo de embedding UMA VEZ,
    # antes do loop de perguntas — evita recarregar o modelo
    # (que é caro) a cada pergunta feita pelo usuário.
    colecao = conectar_colecao()
 
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
            colecao,
            pergunta,
            quantidade=QTD_CHUNKS_RECUPERADOS,
            distancia_maxima=DISTANCIA_MAXIMA 
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
 
        distancias_recuperadas = resultado["distances"][0]
 
        for metadata, distancia in zip(
            metadados_recuperados,
            distancias_recuperadas
        ):
 
            fonte = metadata.get("fonte", "desconhecida")
            paragrafo = metadata.get("paragrafo")
 
            print(f"  📄 {fonte}", end="")
 
            if paragrafo:
                print(f" — parágrafo {paragrafo}", end="")
 
            # distância: quanto MENOR, mais parecido com a pergunta.
            # Rode várias perguntas e observe esses valores para
            # decidir depois um bom DISTANCIA_MAXIMA.
            print(f" (distância: {distancia:.3f})", end="")
 
            print()
 
        print()
 
 
if __name__ == "__main__":
    main()