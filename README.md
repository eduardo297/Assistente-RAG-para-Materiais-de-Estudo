# 📚 Assistente de Estudos com RAG

## 📌 Visão Geral

O objetivo principal deste projeto é atuar como um assistente inteligente capaz de responder a dúvidas sobre materiais de estudo utilizando **exclusivamente informações extraídas e validadas dos documentos fornecidos**.

Diferente de consultas diretas a Large Language Models (LLMs), este sistema garante respostas *grounded* (ancoradas no texto original), minimizando alucinações e oferecendo controle total sobre o contexto recuperado.

---

## 🛠️ Conceitos e Técnicas Exploradas

Este repositório foi construído para testar e validar diversas etapas cruciais na construção de pipelines RAG modernos:

- **Ingestão e Processamento de Documentos:** carregamento e sanitização de dados textuais (PDF, DOCX, PPTX, TXT).
- **Estratégias de Chunking:** divisão de documentos em blocos semanticamente relevantes, respeitando limites de frases.
- **Embeddings:** vetorização de texto para representação em espaço vetorial (via `sentence-transformers`, local e sem custo).
- **Busca Vetorial & Banco de Dados Vetorial:** armazenamento e consulta de alta performance com **ChromaDB**.
- **Threshold de Relevância / Distância:** filtragem inicial por métricas de similaridade vetorial.
- **Reranking:** reordenação dos candidatos recuperados usando Cross-Encoder (`intfloat/multilingual-e5-small`).
- **Filtro de Relevância por Score:** aplicação de *score cutoff* para descartar trechos irrelevantes antes do envio à LLM.
- **Engenharia de Contexto:** formatação e estruturação otimizada dos prompts.
- **Integração com LLM:** geração de respostas via **Google GenAI (Gemini)**.
- **Controle de Alucinações:** restrição estrita de resposta baseada estritamente no contexto fornecido.
- **Rastreabilidade e Metadados:** preservação da origem e fonte dos trechos recuperados (arquivo, página/parágrafo/slide).
- **Cache de Ingestão:** controle via hash de arquivo para evitar reprocessamento desnecessário em execuções repetidas.

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
```

---

## 💻 Interface Web (Streamlit)

Além do modo terminal, o projeto conta com uma **interface web interativa via Streamlit**, que permite:

- Fazer perguntas em um formato de chat, com histórico de conversa mantido durante a sessão.
- Visualizar as **fontes** de cada resposta (arquivo, página/parágrafo, distância e score de reranking).
- **Fazer upload de novos materiais diretamente pela interface**, sem precisar mexer manualmente na pasta `materiais/` ou rodar o script de ingestão pelo terminal — o próprio app cuida de salvar o arquivo e reindexá-lo.

---

## 🧱 Stack

- **Python**
- **ChromaDB** — banco vetorial local
- **sentence-transformers** — geração de embeddings (roda localmente, sem custo)
- **Streamlit** — interface web
- **Gemini API (Google)** — geração da resposta final

---

## 📂 Estrutura do Repositório

```
primeiro_rag/
│
├── app/
│   ├── core/
│   │   └── assistente.py
│   │
│   ├── database/
│   │   └── chroma.py
│   │
│   ├── embeddings/
│   │   └── embedding_model.py
│   │
│   ├── ingestion/
│   │   ├── loader.py
│   │   ├── pdf_loader.py
│   │   ├── docx_loader.py
│   │   ├── pptx_loader.py
│   │   └── txt_loader.py
│   │
│   ├── retrieval/
│   │   ├── vector_search.py
│   │   └── reranking.py
│   │
│   └── generation/
│       └── gemini.py
│
├── database/
│   ├── chroma/
│   └── processed_files.json
│
├── eval/
│   ├── dataset_avaliacao.json
│   ├── ragas_evaluate.py
│   └── requirements-eval.txt
│
├── materiais/
├── ingest.py
├── query.py
├── app_streamlit.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## ✅ Requisitos

- Python 3.10+
- Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 🚀 Uso Rápido

### 1. Configure sua chave da API Gemini

```bash
echo "GEMINI_API_KEY=sua_chave_aqui" > .env
```

### 2. Adicione seus materiais

Coloque arquivos `.pdf`, `.docx`, `.pptx` ou `.txt` na pasta `materiais/` — ou envie-os diretamente pela interface Streamlit (veja abaixo).

### 3. Indexe os documentos

```bash
python ingest.py
```

O script gera embeddings, quebra os documentos em chunks e popula o ChromaDB. Arquivos já processados (identificados por hash de conteúdo) são pulados automaticamente em execuções futuras, tornando reindexações incrementais rápidas.

### 4. Converse com o assistente

**Via terminal:**

```bash
python query.py
```

**Via interface web:**

```bash
streamlit run app_streamlit.py
```

Na interface, é possível fazer upload de novos materiais e perguntar diretamente sobre eles, sem sair do navegador.

---

## 📊 Avaliação com RAGAS

O projeto inclui um script de avaliação automatizada usando **[RAGAS](https://github.com/explodinggradients/ragas)**, que mede a qualidade das respostas do pipeline com métricas como *faithfulness* (fidelidade ao contexto), *answer relevancy* e *context precision*.

Como o RAGAS depende de uma árvore de pacotes (LangChain) que pode conflitar com as dependências do app principal, ele roda em um **venv separado**:

```bash
python -m venv venv_eval
venv_eval\Scripts\activate
pip install -r eval\requirements-eval.txt
```

Depois, com o venv de avaliação ativo e a partir da raiz do projeto:

```bash
python eval\ragas_evaluate.py
```

O script usa o **Gemini** como LLM juiz (em vez do padrão OpenAI do RAGAS), reaproveitando a mesma `GEMINI_API_KEY` do `.env`. As perguntas e respostas esperadas ficam em `eval/dataset_avaliacao.json` — vale montar um conjunto pequeno (10-20 perguntas) cobrindo bem os materiais indexados.

---

## 📝 Notas e Boas Práticas

- Ao adicionar novos documentos manualmente na pasta `materiais/`, rode `python ingest.py` para atualizar o índice.
- Se trocar o modelo de embeddings, reindexe todos os documentos do zero.
- Para reindexar do zero, remova `database/chroma/` e `database/processed_files.json` antes de rodar `ingest.py` novamente.
- Ajuste parâmetros de busca, threshold de distância e reranking em `app/retrieval/` conforme necessário.

---

## 🔭 Próximos Passos

- [ ] Dockerfile para facilitar execução local
- [ ] Testes automatizados com pytest
- [ ] CI básico via GitHub Actions
