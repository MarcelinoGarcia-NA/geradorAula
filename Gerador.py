%%writefile Gerador.py
from groq import Groq
import os

def gerar_plano(dados):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    prompt = f"""
    Você é um especialista em educação superior.

    Crie um plano de aula com base nos dados:

    Disciplina: {dados['disciplina']}
    Curso: {dados['curso']}
    Carga horária: {dados['carga']}
    Quantidade de aulas: {dados['qtd_aulas']}
    Duração: {dados['duracao']}
    Ementa: {dados['ementa']}
    Objetivo geral: {dados['objetivo']}

    Estruture com:
    - objetivos específicos
    - conteúdos por aula
    - metodologia
    - avaliação
    """

    resposta = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return resposta.choices[0].message.content
