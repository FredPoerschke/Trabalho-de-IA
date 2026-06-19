from crewai import Task, Agent


def create_tarefa_leitura(agente: Agent) -> Task:
    return Task(
        description=(
            "Use a ferramenta file_reader para ler o arquivo localizado em: {file_path}\n"
            "Retorne o conteúdo completo do arquivo exatamente como está, sem alterações, "
            "resumos ou interpretações."
        ),
        expected_output=(
            "O conteúdo completo e íntegro do arquivo de código-fonte, "
            "incluindo nome do arquivo, número de linhas e todo o seu texto."
        ),
        agent=agente,
    )
