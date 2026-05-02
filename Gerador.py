import os
from openai import OpenAI
import anthropic


# =========================
# 🔍 MINI-RAG (RELEVÂNCIA SIMPLES)
# =========================
def extrair_trechos_relevantes(texto, topico, limite=10):
    paragrafos = texto.split("\n")
    relevantes = []

    for p in paragrafos:
        if topico.lower() in p.lower():
            relevantes.append(p.strip())

    # fallback: pega primeiros parágrafos se não achar nada
    if not relevantes:
        relevantes = paragrafos[:limite]

    return "\n".join(relevantes[:limite])


# =========================
# 🚀 GERADOR COM STREAM
# =========================
def gerar_plano_stream(dados, topico, ia="gpt", texto_pdf=""):

    disciplina = dados.get("disciplina", "")
    curso      = dados.get("curso", "")
    carga      = dados.get("carga", "")
    objetivo   = dados.get("objetivo", "")
    ementa     = dados.get("ementa", "")

    # =========================
    # 🔥 CONTEXTO INTELIGENTE
    # =========================
    contexto = ""

    if texto_pdf and texto_pdf.strip():
        texto_relevante = extrair_trechos_relevantes(texto_pdf, topico)
        contexto = f"""
=== MATERIAL DE REFERÊNCIA (USO OBRIGATÓRIO) ===
{texto_relevante}
=== FIM DO MATERIAL ===
"""

    # =========================
    # 🧠 PROMPT FORTE (GROUNDING REAL)
    # =========================
    prompt = f"""
You are a highly experienced university professor in Computer Science.

Your task is to generate a BEGINNER-level teaching plan.

This is a controlled experiment with EXACTLY 3 lessons.

Each lesson MUST correspond to ONE fixed topic:

1. {topico}
2. {topico}
3. {topico}

==================================================
STRICT CONTENT RULES
==================================================

- Generate EXACTLY 3 lessons
- Each lesson uses ONLY the given topic
- Do NOT introduce new topics
- Do NOT mix topics
- Keep content beginner-level

==================================================
CRITICAL STRUCTURE RULES (HARD CONSTRAINTS)
==================================================

You MUST follow the structure EXACTLY.

Each lesson MUST contain EXACTLY these fields:

Conteúdo:
Recursos didáticos:
Metodologia:
Atividade:
Avaliação:

--------------------------------------------------

🚫 FORBIDDEN BEHAVIOR:

- NEVER include "Recursos didáticos:" inside "Conteúdo"
- NEVER include "Metodologia:" inside "Conteúdo"
- NEVER include "Atividade:" inside "Conteúdo"
- NEVER include "Avaliação:" inside "Conteúdo"

- NEVER repeat any section
- NEVER merge sections
- NEVER embed one section inside another

If ANY section appears inside another → OUTPUT IS INVALID

--------------------------------------------------

✅ REQUIRED BEHAVIOR:

- Each section must contain ONLY its own content
- Each section must appear ONLY ONCE per lesson
- Keep sections clearly separated

==================================================
CONTEXT (USE WHEN AVAILABLE)
==================================================

Disciplina: {disciplina}
Curso: {curso}
Carga horária: {carga}
Objetivo: {objetivo}
Ementa: {ementa}

{contexto}

==================================================
OUTPUT LANGUAGE
==================================================

Brazilian Portuguese (pt-BR)

==================================================
OUTPUT FORMAT (STRICT)
==================================================

PLANO DE ENSINO

=== AULA 1 ===
Conteúdo:
Recursos didáticos:
Metodologia:
Atividade:
Avaliação:

=== AULA 2 ===
Conteúdo:
Recursos didáticos:
Metodologia:
Atividade:
Avaliação:

=== AULA 3 ===
Conteúdo:
Recursos didáticos:
Metodologia:
Atividade:
Avaliação:

==================================================
FINAL RULE
==================================================

If you do not follow ALL rules above EXACTLY, your answer is INVALID.
"""

    # =====================
    # 🤖 GPT
    # =====================
    if ia == "gpt":
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    # =====================
    # 🤖 CLAUDE
    # =====================
    else:
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

        with client.messages.stream(
            model="claude-opus-4-5",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:

            for event in stream:
                if event.type == "content_block_delta":
                    yield event.delta.text or ""
