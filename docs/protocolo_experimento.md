# 📌 Protocolo Experimental

## 1. Visão geral

Este protocolo descreve um experimento controlado para comparar dois modelos de linguagem de grande escala (LLMs): GPT-4o-mini (OpenAI) e Claude Opus 4.7 (Anthropic), aplicados à geração automática de planos de ensino para disciplinas de Ciência da Computação.

O objetivo é avaliar diferenças de qualidade pedagógica entre os modelos sob condições controladas.

---

## 2. Desenho experimental

- Tipo: Experimento controlado
- Abordagem: Mista (qualitativa + quantitativa)
- Design: Intra-sujeitos (mesmas entradas para ambos os modelos)

---

## 3. Variáveis

### Variável independente
- Modelo de linguagem (GPT-4o-mini vs Claude Opus 4.7)

### Variáveis controladas
- Prompt estruturado
- Ementa da disciplina
- Número de aulas
- Carga horária
- Contexto adicional (PDF)
- Formato de saída

### Variáveis dependentes
- Qualidade dos planos de ensino (avaliação humana)

---

## 4. Ferramentas utilizadas

- Flask (backend e API)
- OpenAI API
- Anthropic API
- PyPDF2 (extração de texto)
- ReportLab (geração de PDF)
- HTML/JavaScript (frontend)
- JSON / CSV / ZIP (exportação de dados)

---

## 5. Procedimento experimental

1. O usuário insere dados da disciplina (curso, ementa, carga horária e número de aulas).
2. Opcionalmente, um arquivo PDF é enviado como contexto adicional.
3. O sistema extrai o texto do PDF automaticamente.
4. Um prompt estruturado é gerado com base nas entradas.
5. O mesmo prompt é enviado para dois modelos:
   - GPT-4o-mini
   - Claude Opus 4.7
6. Cada modelo gera um plano de ensino completo.
7. As respostas são exibidas via streaming na interface.
8. O usuário avalia os resultados.
9. Os dados são exportados em JSON, CSV e PDF (ZIP).

---

## 6. Estratégia de prompt engineering

O prompt combina:

- Zero-shot prompting (sem exemplos explícitos)
- Structured output prompting (formato fixo de aulas)
- Contextual grounding (uso de ementa + PDF como base)

---

## 7. Instrumento de avaliação

Avaliação humana com escala Likert (0–5):

- Fluidez textual
- Capacidade de cobertura
- Diversidade pedagógica
- Complexidade conceitual
- Relevância

---

## 8. Critérios de controle

- Mesma entrada para ambos os modelos
- Mesmo prompt estruturado
- Mesmo contexto (PDF)
- Mesmo formato de saída
- Mesmo número de aulas

---

## 9. Reprodutibilidade

O experimento é totalmente reprodutível, desde que sejam mantidos os mesmos inputs, prompt e modelos utilizados.

---

## 10. Link da aplicação

https://geradoraula.onrender.com/
