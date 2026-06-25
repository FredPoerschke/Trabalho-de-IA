from crewai import Task

def create_tarefa_auditor(agente_auditor, tarefa_leitura) -> Task:
    return Task(
        description=(
            "Analise criticamente o código-fonte extraído na tarefa de leitura.\n"
            "Seu objetivo é caçar falhas de segurança, injeções de SQL, uso de credenciais "
            "hardcoded, falta de sanitização de inputs e falhas de controle transacional "
            "em operações de banco de dados.\n"
            "Utilize sua ferramenta de busca vetorial (vector_search) para consultar as regras "
            "e diretrizes de segurança da empresa antes de emitir qualquer parecer."
        ),
        expected_output="Um laudo técnico de segurança contendo as vulnerabilidades encontradas, sua gravidade e a recomendação de correção.",
        agent=agente_auditor,
        context=[tarefa_leitura]  
    )