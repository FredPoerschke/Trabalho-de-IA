from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from rag.vector_db import get_collection


class VectorSearchInput(BaseModel):
    query: str = Field(
        description=(
            "Trecho de codigo, padrao ou termo tecnico a ser pesquisado na base "
            "de manuais e boas praticas (ex: 'cursor dentro de loop', "
            "'consulta dentro de for', 'sql injection')."
        )
    )
    n_results: int = Field(
        default=3,
        description="Numero de trechos de manual mais relevantes a retornar.",
    )


class VectorSearchTool(BaseTool):
    name: str = "vector_search"
    description: str = (
        "Busca, no banco de dados vetorial (RAG), os trechos de manuais e boas "
        "praticas de programacao mais relevantes para um trecho de codigo ou "
        "padrao informado. Use esta ferramenta antes de emitir qualquer parecer "
        "sobre performance, logica ou boas praticas, para fundamentar sua analise "
        "em documentacao tecnica real em vez de apenas opiniao."
    )
    args_schema: Type[BaseModel] = VectorSearchInput

    def _run(self, query: str, n_results: int = 3) -> str:
        if not query or not query.strip():
            return "ERRO: A consulta (query) nao pode ser vazia."

        try:
            collection = get_collection()
        except Exception as e:
            return f"ERRO ao conectar com o banco vetorial: {e}"

        try:
            total_documentos = collection.count()
        except Exception as e:
            return f"ERRO ao acessar a colecao vetorial: {e}"

        if total_documentos == 0:
            return (
                "ERRO: A base vetorial esta vazia. Execute o script de ingestao "
                "(python -m rag.ingest) para indexar os manuais em rag/docs_base/."
            )

        try:
            resultados = collection.query(
                query_texts=[query],
                n_results=min(n_results, total_documentos),
            )
        except Exception as e:
            return f"ERRO inesperado ao consultar a base vetorial: {e}"

        documentos = resultados.get("documents", [[]])[0]
        metadados = resultados.get("metadatas", [[]])[0]

        if not documentos:
            return f"Nenhum trecho relevante encontrado para a consulta: '{query}'"

        blocos = []
        for indice, (documento, metadado) in enumerate(zip(documentos, metadados), start=1):
            fonte = metadado.get("fonte", "desconhecida") if metadado else "desconhecida"
            blocos.append(
                f"--- Trecho {indice} (fonte: {fonte}) ---\n{documento}"
            )

        return "\n\n".join(blocos)
