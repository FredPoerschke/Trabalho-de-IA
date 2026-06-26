import os
import sys
import argparse
from dotenv import load_dotenv
from crewai import Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

from agents.extrator import create_agente_leitor
from agents.especialista import create_agente_especialista
from agents.auditor import create_agente_auditor
from agents.sintetizador import create_agente_sintetizador

from tasks.extrator_task import create_tarefa_leitura
from tasks.especialista_task import create_tarefa_especialista
from tasks.auditor_task import create_tarefa_auditor
from tasks.sintetizador_task import create_tarefa_sintetizador

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Code Reviewer IA Multiagente")
    parser.add_argument("--file", required=True, help="Caminho do arquivo de código a ser revisado")
    args = parser.parse_args()

    print(f"=== Inicializando IA Code Reviewer ===")
    print(f"[Processamento] Iniciando a revisão do arquivo: {args.file}\n")

    # Sobe o servidor MCP local (mcp_server/server.py) via stdio e obtém as
    # ferramentas (file_reader e vector_search) já adaptadas para o CrewAI.
    # O subprocesso herda as variáveis de ambiente (OLLAMA_*, CHROMA_PATH).
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
        env=os.environ.copy(),
    )

    print("[MCP] Iniciando servidor MCP e carregando ferramentas...")
    with MCPServerAdapter(server_params) as mcp_tools:
        print(f"[MCP] Ferramentas disponíveis: {[t.name for t in mcp_tools]}\n")

        file_reader_tool = mcp_tools["file_reader"]
        vector_search_tool = mcp_tools["vector_search"]

        # O agente leitor deve devolver o conteúdo do arquivo exatamente como veio
        # da ferramenta, sem reinterpretação do LLM.
        file_reader_tool.result_as_answer = True

        agente_leitor = create_agente_leitor(file_reader_tool)
        agente_especialista = create_agente_especialista(vector_search_tool)
        agente_auditor = create_agente_auditor(vector_search_tool)
        agente_sintetizador = create_agente_sintetizador()

        tarefa_leitura = create_tarefa_leitura(agente_leitor)

        tarefa_especialista = create_tarefa_especialista(agente_especialista, tarefa_leitura)
        tarefa_auditor = create_tarefa_auditor(agente_auditor, tarefa_leitura)

        tarefa_sintese = create_tarefa_sintetizador(agente_sintetizador, [tarefa_especialista, tarefa_auditor])

        crew = Crew(
            agents=[agente_leitor, agente_especialista, agente_auditor, agente_sintetizador],
            tasks=[tarefa_leitura, tarefa_especialista, tarefa_auditor, tarefa_sintese],
            process=Process.sequential,
            verbose=True,
        )

        resultado = crew.kickoff(inputs={"file_path": args.file})

    print("\n" + "=" * 60)
    print("RELATÓRIO CONSOLIDADO FINAL (SINTETIZADOR)")
    print("=" * 60)
    print(resultado)


if __name__ == "__main__":
    os.environ["CHROMA_PATH"] = "rag/chroma_db"
    main()
