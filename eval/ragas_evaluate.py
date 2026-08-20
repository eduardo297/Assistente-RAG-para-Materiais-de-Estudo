import os
os.environ["RAGAS_DO_NOT_TRACK"] = "true"

from dotenv import load_dotenv
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from datasets import Dataset
import json
import sys



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


load_dotenv()

def carregar_dataset():
    with open("eval/dataset_avaliacao.json", "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    from app.core.assistente import inicializar, responder_pergunta

    cliente_gemini, colecao = inicializar()
    perguntas_teste = carregar_dataset()

    registros = []
    for item in perguntas_teste:
        try:
            resultado = responder_pergunta(cliente_gemini, colecao, item["pergunta"])
        except Exception as erro:
            print(f"  -> Erro ao processar '{item['pergunta']}': {erro}")
            continue
        registros.append({
            "question": item["pergunta"],
            "answer": resultado["resposta"],
            "contexts": [f["texto"] for f in resultado["fontes"]],
            "ground_truth": item["resposta_esperada"],
        })

    dataset = Dataset.from_list(registros)

    # Configura o Gemini como LLM juiz e como modelo de embeddings do RAGAS
    llm_ragas = LangchainLLMWrapper(
        ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )
    )
    embeddings_ragas = LangchainEmbeddingsWrapper(
        GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )
    )

    resultado_ragas = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=llm_ragas,
        embeddings=embeddings_ragas,
    )
    print(resultado_ragas)

if __name__ == "__main__":
    main()