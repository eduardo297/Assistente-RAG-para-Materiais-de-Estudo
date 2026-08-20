from app.core.assistente import inicializar, responder_pergunta
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset
import json

def carregar_dataset():
    with open("eval/dataset_avaliacao.json", "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    cliente_gemini, colecao = inicializar()
    perguntas_teste = carregar_dataset()

    registros = []
    for item in perguntas_teste:
        resultado = responder_pergunta(cliente_gemini, colecao, item["pergunta"])
        registros.append({
            "question": item["pergunta"],
            "answer": resultado["resposta"],
            "contexts": [f["fonte"] for f in resultado["fontes"]],
            "ground_truth": item["resposta_esperada"],
        })

    dataset = Dataset.from_list(registros)
    resultado_ragas = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
    )
    print(resultado_ragas)

if __name__ == "__main__":
    main()