from crewai import Task, Agent


def create_tarefa_especialista(agente: Agent, tarefa_leitura) -> Task:
    return Task(
        description=(
            "Voce recebeu o conteudo completo de um arquivo de codigo-fonte. "
            "Analise-o em busca de:\n"
            "- Gargalos de performance (ex: consultas dentro de loops, cursores ineficientes)\n"
            "- Logicas redundantes ou desnecessariamente complexas\n"
            "- Violacoes de boas praticas de programacao\n"
            "- Oportunidades de refatoracao\n\n"
            "Para CADA problema encontrado, utilize a ferramenta vector_search para "
            "buscar na base de manuais o trecho de documentacao que sustenta sua observacao. "
            "Nao emita pareceres sem fundamentacao na base vetorial.\n\n"
            "IGNORE completamente questoes de seguranca — isso e responsabilidade de outro agente."
        ),
        expected_output=(
            "Um relatorio tecnico estruturado com:\n"
            "1. Lista de problemas encontrados (logica/performance)\n"
            "2. Para cada problema: trecho afetado, impacto, trecho do manual que fundamenta, "
            "e sugestao de correcao concreta.\n"
            "3. Resumo geral da qualidade estrutural do codigo."
        ),
        agent=agente,
        context=[tarefa_leitura],
    )