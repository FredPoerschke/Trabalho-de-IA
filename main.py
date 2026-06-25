import argparse
from dotenv import load_dotenv
from crewai import Crew, Process
from agents.extrator import create_agente_leitor
from agents.especialista import create_agente_especialista
from tasks.extrator_task import create_tarefa_leitura
from tasks.especialista_task import create_tarefa_especialista

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Code Reviewer IA")
    parser.add_argument("--file", required=True, help="Caminho do arquivo de código a ser revisado")
    args = parser.parse_args()

    agente_leitor = create_agente_leitor()
    agente_especialista = create_agente_especialista()

    tarefa_leitura = create_tarefa_leitura(agente_leitor)
    tarefa_especialista = create_tarefa_especialista(agente_especialista, tarefa_leitura)

    crew = Crew(
        agents=[agente_leitor, agente_especialista],
        tasks=[tarefa_leitura, tarefa_especialista],
        process=Process.sequential,
        verbose=True,
    )

    resultado = crew.kickoff(inputs={"file_path": args.file})

    print("\n" + "=" * 60)
    print("RELATORIO FINAL DO AGENTE ESPECIALISTA")
    print("=" * 60)
    print(resultado)


if __name__ == "__main__":
    main()