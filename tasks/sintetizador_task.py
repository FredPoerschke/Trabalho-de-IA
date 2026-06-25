from crewai import Task

def create_tarefa_sintetizador(agente_sintetizador, tarefas_contexto: list) -> Task:
    return Task(
        description=(
            "Leia e analise cuidadosamente os relatórios técnicos produzidos pelas tarefas anteriores "
            "(o laudo do Especialista em Performance/Lógica e o laudo do Auditor de Segurança).\n"
            "Sintetize todas as descobertas em um único relatório consolidado. "
            "Se ambos os agentes apontarem problemas no mesmo bloco do código (por exemplo, na mesma "
            "trigger ou procedure de pagamento), unifique as observações de forma coesa.\n"
            "Estruture o documento final rigorosamente em Markdown, criando seções claras para 'Problemas de "
            "Performance e Lógica' e 'Vulnerabilidades de Segurança'."
        ),
        expected_output="Um relatório técnico final em formato Markdown, unificando as descobertas de forma limpa e profissional, pronto para entrega.",
        agent=agente_sintetizador,
        context=tarefas_contexto 
    )