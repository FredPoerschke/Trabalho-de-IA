import os
from crewai import Agent, LLM
from tools.file_reader import FileReaderTool


def create_agente_leitor() -> Agent:
    llm = LLM(
        model=f"ollama/{os.getenv('OLLAMA_MODEL', 'llama3.2')}",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )

    return Agent(
        role="Agente Leitor de Código",
        goal=(
            "Usar a ferramenta file_reader para extrair e retornar o conteúdo "
            "completo de arquivos de código-fonte sem nenhuma modificação."
        ),
        backstory=(
            "Você é um agente especializado em leitura de código-fonte. "
            "Sua única responsabilidade é usar a ferramenta de leitura de arquivos "
            "para extrair o conteúdo exato de qualquer arquivo que lhe for solicitado. "
            "Você não analisa, não critica e não modifica o código — apenas o extrai fielmente. "
            "Sempre utilize a ferramenta file_reader, nunca tente adivinhar o conteúdo do arquivo."
        ),
        tools=[FileReaderTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
