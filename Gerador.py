import os
import anthropic
from openai import OpenAI

def gerar_plano_stream(dados, quantidade, ia="gpt"):

    base = f"""
Disciplina: {dados.get('disciplina')}
Curso: {dados.get('curso')}
Carga: {dados.get('carga')}
Aulas: {dados.get('qtd_aulas')}
Duração: {dados.get('duracao')}
Ementa: {dados.get('ementa')}
Objetivo: {dados.get('objetivo')}
"""

    contexto_extra = dados.get("texto_arquivo", "")

    prompt = (
        "Você é um professor universitário.\n"
        "Seja objetivo, técnico e siga exatamente o formato.\n\n"

        f"A partir do texto abaixo, gere exatamente {quantidade} planos de aula. "
        "Cada plano deve conter obrigatoriamente:\n"
        "- Objetivo Geral\n"
        "- Objetivos Específicos\n"
        "- Conteúdo por Aula\n"
        "- Metodologia\n"
        "- Avaliação\n\n"

        "Formato obrigatório:\n"
        "1. Plano de Aula\n"
        "Objetivo Geral: ...\n"
        "Objetivos Específicos:\n"
        "- ...\n"
        "Conteúdo por Aula:\n"
        "Aula 1: ...\n"
        "Metodologia: ...\n"
        "Avaliação: ...\n\n"

        f"Dados principais:\n{base}\n\n"
        f"Contexto adicional do arquivo:\n{contexto_extra[:1500]}"
    )

    # ================= GPT =================
    if ia == "gpt":
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1,
            stream=True
        )

        for chunk in stream:
            yield chunk.choices[0].delta.content or ""

    # ================= CLAUDE =================
    elif ia == "claude":
        try:
            client = anthropic.Anthropic(
                api_key=os.environ["ANTHROPIC_API_KEY"]
            )

            with client.messages.stream(
                model="claude-opus-4-7",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            import traceback
            yield "\n===== ERRO CLAUDE =====\n"
            yield traceback.format_exc()
