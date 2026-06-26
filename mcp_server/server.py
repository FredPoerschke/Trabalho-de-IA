"""
Servidor MCP (Model Context Protocol) do Code Reviewer IA.

Expõe as ferramentas do sistema (leitura de arquivos e busca vetorial/RAG)
através do protocolo MCP, via transporte stdio. Os agentes do CrewAI consomem
essas ferramentas como um cliente MCP (ver main.py), de modo que o acesso a
recursos externos (sistema de arquivos e base vetorial) fica padronizado e
desacoplado dos agentes.

Execução direta (para testes):
    python -m mcp_server.server
"""
from mcp.server.fastmcp import FastMCP

from tools.file_reader import FileReaderTool
from tools.vector_search import VectorSearchTool

mcp = FastMCP("code-reviewer-tools")

# Reaproveita exatamente a lógica já existente das tools do projeto (DRY):
# o servidor MCP é apenas a "casca" que as expõe pelo protocolo.
_file_reader = FileReaderTool()
_vector_search = VectorSearchTool()


@mcp.tool()
def file_reader(file_path: str) -> str:
    """Lê e retorna o conteúdo completo de um arquivo de código-fonte.

    Use para extrair o conteúdo exato de um arquivo antes de analisá-lo.
    Extensões aceitas: .sql, .js, .ts, .py, .java, .c, .cpp, .h, .hpp, .txt
    """
    return _file_reader._run(file_path=file_path)


@mcp.tool()
def vector_search(query: str, n_results: int = 3) -> str:
    """Busca na base vetorial (RAG) os trechos de manuais e boas práticas
    de programação mais relevantes para um trecho de código ou padrão.

    Use antes de emitir qualquer parecer sobre performance, lógica, boas
    práticas ou segurança, para fundamentar a análise em documentação real.
    """
    return _vector_search._run(query=query, n_results=n_results)


if __name__ == "__main__":
    mcp.run(transport="stdio")
