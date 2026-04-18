%%writefile Gerador.py
from groq import Groq

def gerar_plano(dados):
    try:
        client = Groq(api_key="")  # 🔥 coloque sua chave aqui

        prompt = f"""
        Você é um especialista em educação superior.

        Crie um plano de aula:

        Disciplina: {dados['disciplina']}
        Curso: {dados['curso']}
        Carga horária: {dados['carga']}
        Quantidade de aulas: {dados['qtd_aulas']}
        Duração: {dados['duracao']}
        Ementa: {dados['ementa']}
        Objetivo geral: {dados['objetivo']}

        Estruture com:
        - Objetivos específicos
        - Conteúdos por aula
        - Metodologia
        - Avaliação
        """

        resposta = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        return resposta.choices[0].message.content

    except Exception as e:
        return f"ERRO: {str(e)}"
