## 📌 Visão Geral

O objetivo principal deste projeto é atuar como um assistente inteligente capaz de responder a dúvidas sobre materiais de estudo utilizando **exclusivamente informações extraídas e validadas dos documentos fornecidos**. 

Diferente de consultas diretas a Large Language Models (LLMs), este sistema garante respostas grounded (ancoradas no texto original), minimizando alucinações e oferecendo controle sobre o contexto recuperado.

---

## 🛠️ Conceitos e Técnicas Exploradas

Este repositório foi construído para testar e validar diversas etapas cruciais na construção de pipelines RAG modernos:

- **Ingestão e Processamento de Documentos:** Carregamento e sanitização de dados textuais.
- **Estratégias de Chunking:** Divisão de documentos em blocos semanticamente relevantes.
- **Embeddings:** Vetorização de texto para representação em espaço vetorial.
- **Busca Vetorial & Banco de Dados Vetorial:** Armazenamento e consulta de alta performance com **ChromaDB**.
- **Threshold de Relevância / Distância:** Filtragem inicial por métricas de similaridade vetorial.
- **Reranking:** Reordenação dos candidatos recuperados usando Cross-Encoder (`intfloat/multilingual-e5-small`).
- **Filtro de Relevância por Score:** Aplicação de *score cutoff* para descartar trechos irrelevantes antes do envio à LLM.
- **Engenharia de Contexto:** Formatação e estruturação otimizada dos prompts.
- **Integração com LLM:** Geração de respostas via **Google GenAI (Gemini)**.
- **Controle de Alucinações:** Restrição estrita de resposta baseada estritamente no contexto fornecido.
- **Rastreabilidade e Metadados:** Preservação da origem e fonte dos trechos recuperados.

---

## 🧠 Arquitetura e Fluxo do RAG

O pipeline de recuperação e geração segue o fluxo detalhado abaixo:

```text
                     [ PERGUNTA ]
                          │
                          ▼
                Modelo de Embedding
                          │
                          ▼
                 Busca no ChromaDB
                          │
                          ▼
               Threshold de Distância
                          │
                          ▼
                     Candidatos
                          │
                          ▼
            Reranking (Cross-Encoder)
                          │
                          ▼
               Filtro de Score Mínimo
                          │
                          ▼
                   Contexto Final
                          │
                          ▼
             Google Gemini API (LLM)
                          │
                          ▼
                     [ RESPOSTA ]

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
│   │   └── reranking.py
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
