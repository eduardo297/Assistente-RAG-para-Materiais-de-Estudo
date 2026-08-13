# Assistente RAG para Materiais de Estudo

Assistente de perguntas e respostas que usa **RAG (Retrieval-Augmented Generation)**
para responder dúvidas com base em PDFs de materiais de estudo da faculdade.

## Como funciona

1. **Ingestão**: os PDFs são lidos, o texto é quebrado em pedaços menores (chunks)
   e transformado em embeddings (representações numéricas do significado do texto),
   salvos num banco vetorial local (ChromaDB).
2. **Busca**: quando o usuário faz uma pergunta, o sistema busca no banco vetorial
   os trechos de texto mais parecidos semanticamente com a pergunta.
3. **Geração**: os trechos recuperados são enviados junto com a pergunta para o
   modelo gemini (Google), que gera uma resposta baseada apenas nesse contexto.

## Stack

- **Python**
- **ChromaDB** — banco vetorial local
- **sentence-transformers** — geração de embeddings (roda localmente, sem custo)
- **gemini API (Google)** — geração da resposta final

## Como rodar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Colocar os PDFs na pasta materiais/
mkdir materiais
# copie seus PDFs para dentro dela

# 3. Indexar os materiais
python ingest.py

# 4. Criar arquivo .env com sua chave de API
echo "GEMINI_API_KEY=sua_chave_aqui" > .env

# 5. Fazer perguntas
python query.py
```

## Exemplo de uso

```
Sua pergunta: O que é complexidade de tempo O(n log n)?

Resposta: Segundo os materiais, complexidade O(n log n)...
```

## Possíveis melhorias futuras

- Interface web com Streamlit
- Suporte a outros formatos (slides .pptx, anotações .txt)
- Cache de respostas para perguntas repetidas
- Avaliação automática da qualidade das respostas (RAGAS)

## Autor

Eduardo Santiago Bearzi
