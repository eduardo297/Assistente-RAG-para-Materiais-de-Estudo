# Assistente RAG para Materiais de Estudo

Assistente de perguntas e respostas que usa **RAG (Retrieval-Augmented Generation)**
para responder dúvidas com base em PDFs de materiais de estudo da faculdade.

## Como funciona

O projeto é dividido em quatro etapas principais:

```text
Materiais
   ↓
Ingestão
   ↓
Chunks + Embeddings
   ↓
ChromaDB
   ↓
Busca semântica
   ↓
Google Gemini
   ↓
Resposta

## Stack

- **Python**
- **ChromaDB** — banco vetorial local
- **sentence-transformers** — geração de embeddings (roda localmente, sem custo)
- **gemini API (Google)** — geração da resposta final

## estrutura atual 

primeiro_rag/
│
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   └── chroma.py
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedding_model.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── pdf_loader.py
│   │   ├── docx_loader.py
│   │   ├── pptx_loader.py
│   │   └── txt_loader.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── vector_search.py
│   │
│   └── generation/
│       ├── __init__.py
│       └── gemini.py
│
├── database/
│   └── chroma/
│
├── materiais/
├── ingest.py
├── query.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md

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



## Autor

Eduardo Santiago Bearzi
