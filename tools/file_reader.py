from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

ALLOWED_EXTENSIONS = {".sql", ".js", ".ts", ".py", ".java", ".c", ".cpp", ".h", ".hpp", ".txt"}


class FileReaderInput(BaseModel):
    file_path: str = Field(description="Caminho para o arquivo de código-fonte a ser lido.")


class FileReaderTool(BaseTool):
    name: str = "file_reader"
    description: str = (
        "Lê e retorna o conteúdo completo de um arquivo de código-fonte. "
        "Use esta ferramenta sempre que precisar extrair o conteúdo de um arquivo. "
        f"Extensões aceitas: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
    )
    args_schema: Type[BaseModel] = FileReaderInput

    def _run(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            return f"ERRO: Arquivo não encontrado: '{file_path}'"

        if not path.is_file():
            return f"ERRO: O caminho '{file_path}' não é um arquivo."

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
            return f"ERRO: Extensão '{path.suffix}' não permitida. Aceitas: {allowed}"

        try:
            content = path.read_text(encoding="utf-8")
            line_count = len(content.splitlines())
            return (
                f"=== ARQUIVO: {path.name} ===\n"
                f"Caminho: {path.resolve()}\n"
                f"Linhas: {line_count}\n"
                f"{'=' * 40}\n"
                f"{content}"
            )
        except UnicodeDecodeError:
            return f"ERRO: Não foi possível ler '{file_path}' como UTF-8. Verifique a codificação do arquivo."
        except Exception as e:
            return f"ERRO inesperado ao ler arquivo: {e}"
