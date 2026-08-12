"""
query.py
--------
Faz uma pergunta, busca os trechos mais relevantes nos PDFs indexados
e usa um LLM (Claude, via API da Anthropic) para responder com base
nesses trechos.

Como usar:
    1. Rode ingest.py primeiro
    2. Crie um arquivo .env com: ANTHROPIC_API_KEY=sua_chave_aqui
    3. Rode: python query.py
"""

import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import anthropic

load_dotenv()

PASTA_BANCO = "banco_vetorial"
QTD_CHUNKS_RECUPERADOS = 4


def montar_prompt(pergunta: str, trechos: list[str]) -> str:
    """Monta o prompt que vai para o LLM, incluindo o contexto recuperado."""
    contexto = "\n\n---\n\n".join(trechos)
    return f"""Você é um assistente de estudos. Responda a pergunta do aluno
usando APENAS as informações do contexto abaixo. Se a resposta não estiver
no contexto, diga claramente que não encontrou essa informação nos materiais.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}
"""


def main():
    if not os.path.isdir(PASTA_BANCO):
        print("Banco vetorial não encontrado. Rode 'python ingest.py' primeiro.")
        return

    cliente_chroma = chromadb.PersistentClient(path=PASTA_BANCO)
    funcao_embedding = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    colecao = cliente_chroma.get_or_create_collection(
        name="materiais_estudo",
        embedding_function=funcao_embedding,
    )

    cliente_anthropic = anthropic.Anthropic()  # lê ANTHROPIC_API_KEY do .env automaticamente

    print("Assistente de estudos pronto. Digite 'sair' para encerrar.\n")

    while True:
        pergunta = input("Sua pergunta: ").strip()
        if pergunta.lower() in ("sair", "exit", "quit"):
            break
        if not pergunta:
            continue

        resultado = colecao.query(query_texts=[pergunta], n_results=QTD_CHUNKS_RECUPERADOS)
        trechos_recuperados = resultado["documents"][0]

        if not trechos_recuperados:
            print("Nada relevante encontrado nos materiais.\n")
            continue

        prompt = montar_prompt(pergunta, trechos_recuperados)

        resposta = cliente_anthropic.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )

        print(f"\nResposta: {resposta.content[0].text}\n")


if __name__ == "__main__":
    main()
