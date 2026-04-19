%%writefile Gerador.py
import os
import anthropic
from openai import OpenAI

def gerar_plano(dados, ia="claude"):
    prompt = f"""
Crie um plano de aula:

Disciplina: {dados.get('disciplina')}
Curso: {dados.get('curso')}
Carga: {dados.get('carga')}
Aulas: {dados.get('qtd_aulas')}
Duração: {dados.get('duracao')}
Ementa: {dados.get('ementa')}
Objetivo: {dados.get('objetivo')}

Inclua:
- Objetivos específicos
- Conteúdos por aula
- Metodologia
- Avaliação
"""

    try:
        # 🔥 CLAUDE
        if ia == "claude":
            client = anthropic.Anthropic(
                api_key=os.environ["ANTHROPIC_API_KEY"]
            )

            msg = client.messages.create(  # ✅ alinhado correto
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return msg.content[0].text

        # 🔥 GPT
        elif ia == "gpt":
            client = OpenAI(
                api_key=os.environ["OPENAI_API_KEY"]
            )

            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é professor universitário."},
                    {"role": "user", "content": prompt}
                ]
            )

            return resp.choices[0].message.content

    except Exception as e:
        import traceback
        return "<pre>" + traceback.format_exc() + "</pre>"
