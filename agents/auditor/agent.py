import os
from crewai import Agent, LLM

def create_agente_auditor(vector_search_tool) -> Agent:
    llm = LLM(
        model=f"ollama/{os.getenv('OLLAMA_MODEL', 'llama3.2')}",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    return Agent(
        role="Auditor Sênior de Segurança de Código (AppSec)",
        goal="Analisar o código extraído, identificar vulnerabilidades criticamente e emitir um laudo de segurança rigoroso.",
        backstory=(
            "Você é um engenheiro de segurança de software focado em AppSec e segurança de banco de dados. "
            "Sua única preocupação é caçar vulnerabilidades implacavelmente. Ao analisar rotinas financeiras, "
            "como cálculos de pagamentos, geração de cobranças ou atualizações de status, "
            "você foca em encontrar injeções de SQL, falta de validação de inputs e lógica transacional insegura em blocos dinâmicos. "
            "Sempre utilize sua ferramenta de busca vetorial para embasar seu julgamento nos manuais e nas diretrizes oficiais da empresa."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[vector_search_tool],
        llm=llm,
    )