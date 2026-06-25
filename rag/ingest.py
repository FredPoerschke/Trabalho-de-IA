"""
Uso:
    python -m rag.ingest
"""
import re
from pathlib import Path
from rag.vector_db import get_collection

DOCS_BASE_DIR = Path(__file__).parent / "docs_base"
ITEM_PATTERN = re.compile(r"(?=^\d+\.\s)", flags=re.MULTILINE)


def _split_em_itens(texto: str) -> list[str]:
    partes = ITEM_PATTERN.split(texto)
    return [p.strip() for p in partes if p.strip() and p.strip()[0].isdigit()]


def ingest_docs_base() -> int:
    if not DOCS_BASE_DIR.exists():
        raise FileNotFoundError(f"Diretorio nao encontrado: {DOCS_BASE_DIR}")

    arquivos = sorted(DOCS_BASE_DIR.glob("*.txt"))
    if not arquivos:
        print(f"Nenhum arquivo .txt encontrado em {DOCS_BASE_DIR}")
        return 0

    collection = get_collection()

    documentos: list[str] = []
    ids: list[str] = []
    metadatas: list[dict] = []

    for arquivo in arquivos:
        conteudo = arquivo.read_text(encoding="utf-8")
        itens = _split_em_itens(conteudo)

        for indice, item in enumerate(itens):
            documentos.append(item)
            ids.append(f"{arquivo.stem}_{indice}")
            metadatas.append({"fonte": arquivo.name})

    if not documentos:
        print("Nenhum item numerado foi extraido dos documentos.")
        return 0

    collection.upsert(documents=documentos, ids=ids, metadatas=metadatas)
    print(f"{len(documentos)} itens indexados na colecao '{collection.name}'.")
    return len(documentos)


if __name__ == "__main__":
    ingest_docs_base()
