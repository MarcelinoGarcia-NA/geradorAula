# 📌 Protocolo Experimental

## 1. Identificação do estudo

Este protocolo descreve um experimento controlado com abordagem mista (qualitativa e quantitativa), cujo objetivo é comparar o desempenho de dois modelos de linguagem de grande escala (LLMs), GPT-4o-mini (OpenAI) e Claude Opus 4.7 (Anthropic), na geração automática de planos de ensino para disciplinas da área de Ciência da Computação.

---

## 2. Desenho experimental

O estudo adota um desenho intra-sujeitos (within-subject design), no qual ambos os modelos recebem exatamente as mesmas entradas, garantindo controle rigoroso das variáveis externas e permitindo comparação direta entre os resultados gerados.

A única variável independente do experimento é o modelo de linguagem utilizado.

---

## 3. Variáveis do experimento

### 3.1 Variável independente
- Modelo de linguagem (GPT-4o-mini vs Claude Opus 4.7)

### 3.2 Variáveis controladas
- Prompt estruturado  
- Ementa da disciplina  
- Número de aulas  
- Carga horária  
- Contexto adicional fornecido por PDF  
- Estrutura de saída definida  

### 3.3 Variáveis dependentes
- Qualidade dos planos de ensino gerados, avaliada por humanos  

---

## 4. Materiais e ferramentas

- Sistema web desenvolvido em Flask  
- APIs: OpenAI e Anthropic  
- Biblioteca PyPDF2 (extração de texto de PDF)  
- ReportLab (geração de PDF)  
- Formulário web para entrada de dados  
- Escala Likert (0 a 5) para avaliação  
- Sistema de exportação (JSON, CSV e PDF compactados em ZIP)  

---

## 5. Procedimento experimental

1. O usuário insere os dados da disciplina (nome, curso, ementa, carga horária e número de aulas).  
2. Opcionalmente, um arquivo PDF é enviado para fornecer contexto adicional.  
3. O sistema extrai automaticamente o texto do PDF.  
4. Um prompt estruturado é gerado combinando dados da disciplina e contexto extraído.  
5. O mesmo prompt é enviado aos dois modelos de linguagem (GPT e Claude).  
6. Cada modelo gera um plano de ensino completo seguindo formato estruturado.  
7. As respostas são exibidas via streaming em tempo real.  
8. O usuário avalia os planos utilizando escala Likert.  
9. Os dados são armazenados e exportados em JSON, CSV e PDF.  
10. Os resultados são comparados entre os modelos.  

---

## 6. Estratégia de engenharia de prompt

O prompt combina três técnicas principais:

- **Zero-shot prompting:** sem exemplos de saída  
- **Structured output prompting:** formato rígido de aulas estruturadas  
- **Contextual grounding:** uso de ementa e PDF como base obrigatória  

Essa combinação garante consistência estrutural e aderência pedagógica.

---

## 7. Instrumento de avaliação

A avaliação é realizada por humanos utilizando escala Likert (0 a 5), considerando:

- Fluidez textual  
- Capacidade de cobertura do conteúdo  
- Diversidade pedagógica  
- Complexidade conceitual  
- Relevância para a disciplina  

A nota final é calculada a partir da média dos critérios.

---

## 8. Análise dos resultados

A análise é realizada de forma comparativa entre os modelos, considerando:

- Médias das métricas de avaliação  
- Distribuição das notas Likert  
- Consistência estrutural dos planos gerados  
- Diferenças qualitativas entre os modelos  

---

## 9. Critérios de controle experimental

- Mesmo prompt para todos os modelos  
- Mesmas entradas para ambos os LLMs  
- Estrutura de saída padronizada  
- Contexto (PDF) idêntico  
- Número de aulas fixo  

---

## 10. Reprodutibilidade

O experimento é totalmente reprodutível, permitindo que outros pesquisadores repliquem a metodologia utilizando os mesmos inputs, prompt e modelos especificados.
