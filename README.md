# Code Reviewer IA — Sistema Multiagente de Revisão de Código

Sistema multiagente de revisão automatizada de código-fonte, construído com **CrewAI**,
**modelos locais via Ollama**, **RAG** sobre uma base de boas práticas e integração de
ferramentas via **MCP (Model Context Protocol)**. Toda a interação acontece pelo terminal.

> Trabalho Final da disciplina de Inteligência Artificial — Implementação prática de uma
> solução com agentes e modelos locais.

---

## Integrantes da equipe

- Lucian Bellini
- Frederico Poerschke
- Gabriel Kobielski
- Erik Rocha

---

## Problema escolhido

Revisão de código é uma tarefa cara, demorada e que depende de revisores experientes. Em
times pequenos, o code review costuma misturar — em uma única leitura — preocupações muito
diferentes: **performance/lógica** e **segurança**. Isso reduz a profundidade da análise e
deixa passar problemas.

A proposta é um **revisor de código automatizado** que recebe um arquivo de código-fonte
(SQL/PL-SQL, Python, JavaScript, C/C++ etc.) e produz um **relatório técnico consolidado**,
separando claramente os achados de performance/lógica dos achados de segurança, sempre
**fundamentados em uma base de manuais e boas práticas** (e não apenas na "opinião" do LLM).

## Objetivo da solução

Entregar, via terminal, um laudo técnico de revisão de um arquivo de código que seja:

- **fundamentado**: cada apontamento é embasado em trechos recuperados de uma base documental (RAG);
- **especializado**: agentes distintos cuidam de performance/lógica e de segurança;
- **consolidado**: um agente relator unifica tudo em um único documento Markdown;
- **local e privado**: roda inteiramente com modelos locais (Ollama), sem enviar o código a APIs pagas.

---

## Arquitetura multiagente

O sistema usa o padrão **sequencial** do CrewAI: a saída de uma etapa vira contexto da
seguinte. A divisão de responsabilidades reflete o fluxo real de um code review.

```
                 ┌─────────────────────────────────────────────┐
                 │           main.py (cliente MCP)             │
                 │   sobe o servidor MCP e injeta as tools     │
                 └───────────────────┬─────────────────────────┘
                                     │  (protocolo MCP / stdio)
                 ┌───────────────────▼─────────────────────────┐
                 │      mcp_server/server.py (servidor MCP)    │
                 │   tools: file_reader  •  vector_search      │
                 └───────────────────┬─────────────────────────┘
                                     │
   ┌─────────────┐   conteúdo   ┌────▼────────┐        ┌──────────────┐
   │  EXTRATOR   │ ───────────► │ ESPECIALISTA │ ─────► │              │
   │  (leitor)   │              │ (perf/lógica)│        │ SINTETIZADOR │ ─► Relatório
   │ file_reader │ ───────────► │   AUDITOR    │ ─────► │   (relator)  │     final
   └─────────────┘              │ (segurança)  │        │              │   (Markdown)
                                └──────────────┘        └──────────────┘
                                 vector_search (RAG)
```

### Papel de cada agente

| Agente | Papel | Entradas | Saídas | Ferramentas |
|--------|-------|----------|--------|-------------|
| **Extrator** (`agents/extrator`) | Lê o arquivo-alvo e devolve o conteúdo íntegro, sem interpretar | caminho do arquivo (`{file_path}`) | conteúdo completo do código | `file_reader` |
| **Especialista** (`agents/especialista`) | Analisa **performance e lógica** (gargalos, redundâncias, cursores, refatorações), fundamentando cada achado no RAG | código extraído | laudo de performance/lógica | `vector_search` |
| **Auditor** (`agents/auditor`) | Analisa **segurança** (SQL injection, falta de sanitização, controle transacional, credenciais), fundamentando no RAG | código extraído | laudo de segurança | `vector_search` |
| **Sintetizador** (`agents/sintetizador`) | Consolida os dois laudos em um único relatório Markdown, eliminando redundâncias | laudos do Especialista e do Auditor | relatório final | — |

**Por que multiagente (e não um agente único)?** Cada agente tem um *backstory* e um
objetivo focados, o que reduz "vazamento" de preocupações (o especialista ignora segurança e
vice-versa) e melhora a qualidade de cada laudo. O sintetizador garante um documento final
coeso. Essa separação também torna o sistema extensível: dá para acrescentar novos
revisores (ex.: estilo, testes) sem alterar os existentes.

---

## Ferramentas (tools) disponíveis

As ferramentas são acionáveis pelos agentes e expostas **via MCP**:

- **`file_reader`** — lê e retorna o conteúdo completo de um arquivo de código-fonte.
  Valida existência, tipo e extensão (`.sql, .js, .ts, .py, .java, .c, .cpp, .h, .hpp, .txt`).
  Implementação: `tools/file_reader.py`.
- **`vector_search`** — faz busca semântica (RAG) na base vetorial de manuais e boas
  práticas, retornando os trechos mais relevantes com a fonte. Implementação:
  `tools/vector_search.py`.

---

## MCP (Model Context Protocol)

O MCP é usado para **padronizar e desacoplar** o acesso dos agentes aos recursos externos
(sistema de arquivos e base vetorial).

- **Servidor MCP** — `mcp_server/server.py`, construído com `FastMCP`, expõe `file_reader` e
  `vector_search` como ferramentas MCP, comunicando-se por **transporte stdio**. Ele
  reaproveita a lógica das tools do projeto (sem duplicação).
- **Cliente MCP** — em `main.py`, o `MCPServerAdapter` (do `crewai-tools`) sobe o servidor
  MCP como subprocesso, descobre as ferramentas pelo protocolo e as adapta para o formato do
  CrewAI. Os agentes recebem essas ferramentas por injeção de dependência.

Ou seja, os agentes **não chamam o código das ferramentas diretamente**: eles invocam tools
descobertas dinamicamente através do protocolo MCP. Isso permitiria, no futuro, substituir o
servidor local por um servidor MCP remoto sem alterar os agentes.

---

## RAG (Retrieval-Augmented Generation)

Antes de emitir qualquer parecer, o Especialista e o Auditor consultam a ferramenta
`vector_search`, que recupera os trechos de manual mais relevantes para o problema observado.
Esses trechos entram no raciocínio do agente como fundamentação — evitando respostas baseadas
apenas no conhecimento paramétrico do LLM e reduzindo alucinações.

**Fluxo:** identificar um possível problema → consultar `vector_search` → citar o trecho do
manual que sustenta o apontamento → sugerir a correção.

### Base de conhecimento

- **Origem/natureza:** manuais de boas práticas de programação escritos para este projeto,
  em `rag/docs_base/`, divididos por tecnologia:
  - `boas_praticas_gerais.txt`, `boas_praticas_sql.txt`, `boas_praticas_plsql.txt`,
    `boas_praticas_python.txt`, `boas_praticas_js.txt`, `boas_praticas_cpp.txt`.
- **Formato:** itens numerados (`1. ...`, `2. ...`). O ingestor quebra cada item em um
  documento independente, preservando a granularidade da recuperação.

### Embeddings e armazenamento vetorial

- **Embeddings:** modelo local **`nomic-embed-text`** servido pelo Ollama.
- **Banco vetorial:** **ChromaDB** (`PersistentClient`), persistido em `rag/chroma_db/`,
  coleção `boas_praticas_codigo`. Configuração em `rag/vector_db.py`; ingestão em
  `rag/ingest.py`.

---

## Modelo local e forma de execução

- **LLM dos agentes:** **`qwen2.5:7b`** (via Ollama), escolhido por equilibrar qualidade de
  raciocínio/seguir instruções e custo de processamento em máquina local.
- **Modelo de embeddings:** **`nomic-embed-text`** (via Ollama).
- **Execução:** os modelos rodam localmente no servidor do Ollama (`http://localhost:11434`);
  nenhum dado do código sai da máquina.

---

## Dependências do projeto

- Python 3.12
- [Ollama](https://ollama.com) instalado e em execução
- Pacotes Python (ver `requirements.txt`):
  - `crewai` — orquestração multiagente
  - `crewai-tools[mcp]` — adaptador de cliente MCP
  - `mcp` — SDK do Model Context Protocol (servidor)
  - `chromadb` — banco vetorial
  - `ollama` — cliente Python do Ollama (usado pelos embeddings)
  - `langchain-community`, `python-dotenv`

---

## Instalação

```bash
git clone <url-do-repositorio>
cd Trabalho-de-IA

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

### Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
```

Baixe os modelos no Ollama (apenas uma vez):

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

### Indexação da base de conhecimento (RAG)

Indexe os manuais de `rag/docs_base/` no banco vetorial. Rode uma vez (ou sempre que
adicionar/alterar documentos):

```bash
python -m rag.ingest
```

---

## Como usar

```bash
python main.py --file <caminho_do_arquivo>
```

O `main.py` sobe automaticamente o servidor MCP, carrega as ferramentas e executa os quatro
agentes em sequência, imprimindo o relatório consolidado final no terminal.

### Exemplo de uso pelo terminal

```bash
python main.py --file scripts_alvo/calcula_pagamento.sql
```

Saída (resumida):

```
=== Inicializando IA Code Reviewer ===
[Processamento] Iniciando a revisão do arquivo: scripts_alvo/calcula_pagamento.sql

[MCP] Iniciando servidor MCP e carregando ferramentas...
[MCP] Ferramentas disponíveis: ['file_reader', 'vector_search']

... (execução dos agentes: Extrator → Especialista / Auditor → Sintetizador) ...

============================================================
RELATÓRIO CONSOLIDADO FINAL (SINTETIZADOR)
============================================================
# Relatório de Revisão de Código
## Problemas de Performance e Lógica
...
## Vulnerabilidades de Segurança
...
```

> Você pode apontar `--file` para qualquer arquivo com extensão suportada. O diretório
> `scripts_alvo/` contém exemplos para teste.

---

## Estrutura do projeto

```
Trabalho-de-IA/
├── main.py                 # Orquestra a Crew e atua como cliente MCP
├── agents/                 # Agentes (extrator, especialista, auditor, sintetizador)
├── tasks/                  # Definição das tarefas de cada agente
├── tools/                  # Lógica das ferramentas (file_reader, vector_search)
├── mcp_server/             # Servidor MCP que expõe as ferramentas
├── rag/
│   ├── docs_base/          # Base de conhecimento (manuais de boas práticas)
│   ├── ingest.py           # Ingestão/indexação no ChromaDB
│   └── vector_db.py        # Cliente Chroma + função de embedding (Ollama)
├── scripts_alvo/           # Arquivos de exemplo para revisão
└── requirements.txt
```
