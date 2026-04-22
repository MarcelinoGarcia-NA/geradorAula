import os
from openai import OpenAI
import anthropic

def gerar_plano_stream(dados, quantidade, ia="gpt"):

    # ================= LIVRO (CORRIGIDO) =================
    texto_pdf = dados.get("texto_arquivo", "")

    livro_nome = "Livro enviado pelo usuário (PDF)"

    if texto_pdf:
        linhas = texto_pdf.split("\n")
        for linha in linhas[:30]:
            linha = linha.strip()
            if 10 < len(linha) < 120:
                livro_nome = linha
                break

    contexto_extra = texto_pdf[:2000]

    # ================= PROMPT =================
    prompt = f"""
Você é um especialista em design instrucional para ensino superior em Ciência da Computação.

Sua tarefa é gerar um plano de ensino completo para a disciplina de Programação Orientada a Objetos em C#.

---

## CONTEXTO DA DISCIPLINA (GROUNDING CONTEXTUAL)
- Disciplina: {dados.get('disciplina')}
- Curso: {dados.get('curso')}
- Carga horária: {dados.get('carga')}
- Número de aulas: {dados.get('qtd_aulas')}
- Ementa: {dados.get('ementa')}
- Livro base: {livro_nome}

---

## USO DO LIVRO (OBRIGATÓRIO)

- Utilize o conteúdo do livro fornecido como referência principal
- Relacione cada aula a capítulos do livro
- Distribua os conteúdos progressivamente

---

## INSTRUÇÕES

Gere EXATAMENTE {dados.get('qtd_aulas')} aulas.

Cada aula deve conter:
- Conteúdo
- Recursos didáticos
- Metodologia
- Atividade
- Avaliação formativa

---

## FORMATO OBRIGATÓRIO

PLANO DE ENSINO

=== AULA 1 ===
Conteúdo:
Recursos didáticos:
Livro: {livro_nome}
Capítulo:
Metodologia:
Atividade:
Avaliação:

(repita até a última aula)

---

## AVALIAÇÕES

Avaliação 1 (1–8):
Tipo:
Descrição:
Critérios:
Peso:

Avaliação 2 (1–{dados.get('qtd_aulas')}):
Tipo:
Descrição:
Critérios:
Peso:

Avaliação opcional:
Tipo:
Descrição:
Critérios:
Peso:

---

## CONTEXTO DO LIVRO
{contexto_extra}

---

## REGRA FINAL
Não quebrar formato. Não usar markdown. Manter padrão consistente.
"""

    # ================= GPT =================
    if ia == "gpt":
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_completion_tokens=3000,
            stream=True
        )

        for chunk in stream:
            yield chunk.choices[0].delta.content or ""

    # ================= CLAUDE =================
    elif ia == "claude":
        client = anthropic.Anthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"]
        )

        with client.messages.stream(
            model="claude-opus-4-7",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text
