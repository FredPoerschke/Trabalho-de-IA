import argparse
from dotenv import load_dotenv
from crewai import Crew, Process
from agents.extrator import create_agente_leitor
from tasks.extrator_task import create_tarefa_leitura

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Code Reviewer IA - Agente Leitor")
    parser.add_argument("--file", required=True, help="Caminho do arquivo de código a ser lido")
    args = parser.parse_args()

    agente = create_agente_leitor()
    tarefa = create_tarefa_leitura(agente)

    crew = Crew(
        agents=[agente],
        tasks=[tarefa],
        process=Process.sequential,
        verbose=True,
    )

    resultado = crew.kickoff(inputs={"file_path": args.file})

    print("\n" + "=" * 60)
    print("CONTEUDO EXTRAIDO PELO AGENTE LEITOR")
    print("=" * 60)
    print(resultado)


if __name__ == "__main__":
    main()
