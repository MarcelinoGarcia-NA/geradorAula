import os
from openai import OpenAI
import anthropic
import re

def gerar_plano_stream(dados, quantidade, ia="gpt"):

    # ================= LIVRO (CORRIGIDO) =================
    texto_pdf = dados.get("texto_arquivo", "")

    livro_nome = None
    capitulos = []

    if texto_pdf:
        linhas = texto_pdf.split("\n")

        for linha in linhas[:80]:
            linha = linha.strip()

            # tenta pegar algo que pareça título de livro/capítulo
            if 10 < len(linha) < 120:
                if (
                    "capítulo" in linha.lower()
                    or re.match(r"^\d+[\.\-]", linha)
                    or "introdução" in linha.lower()
                ):
                    capitulos.append(linha)

        # tenta inferir "nome do livro" como primeira linha relevante
        for linha in linhas[:50]:
            linha = linha.strip()
            if 10 < len(linha) < 120 and not linha.lower().startswith("plano"):
                livro_nome = linha
                break

    capitulos_texto = "\n".join(capitulos[:50]) if capitulos else "NÃO IDENTIFICADO"

    contexto_extra = texto_pdf[:6000]


    # ================= PROMPT =================
    prompt = f"""
  Você é um especialista em design instrucional para ensino superior em Ciência da Computação.

Sua tarefa é gerar um plano de ensino completo para a disciplina de {dados.get('disciplina')} do curso {dados.get('curso')}.

---

## CONTEXTO DA DISCIPLINA
- Disciplina: {dados.get('disciplina')}
- Curso: {dados.get('curso')}
- Carga horária: {dados.get('carga')}
- Número de aulas: {dados.get('qtd_aulas')}
- Ementa: {dados.get('ementa')}
- Objetivo: {dados.get('objetivo')}

---

## LIVRO BASE (OBRIGATÓRIO E CRÍTICO)

O texto abaixo é o conteúdo REAL do livro enviado pelo usuário.

VOCÊ DEVE:
- Ler o conteúdo do PDF
- Identificar títulos de capítulos REAIS (quando existirem)
- NÃO inventar capítulos
- NÃO usar "Capítulo 1" genérico se não existir no texto
- NÃO repetir o mesmo capítulo para todas as aulas

REGRAS IMPORTANTES:
1. Extraia os capítulos diretamente do texto do PDF
2. Use trechos que pareçam títulos (ex: linhas curtas, iniciando com "Capítulo", números, headings)
3. Cada aula deve obrigatoriamente referenciar UM capítulo real do PDF
4. Os capítulos devem ser distribuídos de forma coerente com o conteúdo da aula
5. Se não encontrar capítulos claros, agrupe por seções temáticas reais do texto (NUNCA invente)

FORMATO OBRIGATÓRIO:
Livro: {dados.get("texto_arquivo","Livro enviado pelo usuário")}
Capítulo: [TÍTULO REAL EXTRAÍDO DO TEXTO DO PDF]

---

## CONTEXTO DO LIVRO (TEXTO BRUTO)
{dados.get("texto_arquivo","")}

---

## INSTRUÇÃO PRINCIPAL

Gere EXATAMENTE {dados.get('qtd_aulas')} aulas.

Cada aula deve conter:

- Conteúdo (baseado na ementa + livro)
- Recursos didáticos
- Livro
- Capítulo (OBRIGATORIAMENTE relacionado ao conteúdo da aula)
- Metodologia
- Atividade
- Avaliação formativa

---

## FORMATO OBRIGATÓRIO DE SAÍDA

PLANO DE ENSINO

=== AULA 1 ===
Conteúdo:
Recursos didáticos:
Livro:
Capítulo:
Metodologia:
Atividade:
Avaliação:

(repita exatamente até a última aula)

---

## AVALIAÇÕES

Avaliação 1:
Tipo:
Descrição:
Critérios:
Peso:

Avaliação 2:
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

## REGRA FINAL (CRÍTICA)
- Não usar markdown
- Não inventar capítulos
- Não repetir capítulos sem necessidade
- Não quebrar o formato
- Cada aula deve ter conexão lógica com um capítulo real do texto do PDF
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
