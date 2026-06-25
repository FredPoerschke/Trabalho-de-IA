# Code Reviewer IA

Sistema multi-agente de revisão de código usando CrewAI e modelos locais via Ollama.

---

## Pré-requisitos

- Python 3.12
- [Ollama](https://ollama.com) instalado e rodando

---

## Instalação

Clone o repositório e crie o ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

---

## Configuração

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
```

Baixe os modelos necessários no Ollama:

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

---

## Base de conhecimento (RAG)

Coloque arquivos `.txt` com boas práticas e manuais técnicos na pasta `rag/docs_base/`. Os itens devem ser numerados no formato `1. texto`, `2. texto`, etc.

Depois, execute o script de ingestão para indexar os documentos:

```bash
python -m rag.ingest
```

Só precisa rodar uma vez, ou sempre que adicionar novos documentos.

---

## Como usar

```bash
python main.py --file <caminho_do_arquivo>
```

Exemplo:

```bash
python main.py --file scripts_alvo/calcula_pagamento.sql
```

O sistema vai ler o arquivo, analisar a lógica e performance do código e exibir um relatório técnico no terminal.