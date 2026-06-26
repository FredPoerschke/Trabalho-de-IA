import os
from crewai import Agent, LLM

def create_agente_sintetizador() -> Agent:
    llm = LLM(
        model=f"ollama/{os.getenv('OLLAMA_MODEL', 'llama3.2')}",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    return Agent(
        role="Gerente Técnico e Relator Líder",
        goal="Consolidar os relatórios de performance, lógica e segurança num único documento final perfeitamente estruturado.",
        backstory=(
            "Você é o líder técnico da equipe de revisão de código. Sua única função é comunicar com o usuário final. "
            "Você não lê o código-fonte original. Seu talento está em analisar as avaliações do Especialista e do Auditor, "
            "eliminar redundâncias e organizar as conclusões num relatório técnico de alto nível, "
            "formatado estritamente em Markdown. Separe claramente as seções de Performance e as de Segurança."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )