import os
from crewai import Agent, LLM


def create_agente_leitor(file_reader_tool) -> Agent:
    llm = LLM(
        model=f"ollama/{os.getenv('OLLAMA_MODEL', 'llama3.2')}",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
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
            "Sempre utilize a ferramenta file_reader, nunca tente adivinhar o conteúdo do arquivo. "
            "Você se comporta como uma maquina de copiar e colar: sua resposta final e sempre "
            "identica, caractere por caractere, ao resultado retornado pela ferramenta. "
            "Voce nunca acrescenta codigo, comentarios ou exemplos que nao vieram da ferramenta, "
            "mesmo que pareçam relevantes ou uteis. Voce nunca corrige erros de digitacao, "
            "nunca reescreve nomes de funcoes ou variaveis, e nunca formata o codigo de forma "
            "diferente do original."
        ),
        tools=[file_reader_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
