import os
import argparse
from dotenv import load_dotenv
from crewai import Crew, Process

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

    agente_leitor = create_agente_leitor()
    agente_especialista = create_agente_especialista()
    agente_auditor = create_agente_auditor()
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