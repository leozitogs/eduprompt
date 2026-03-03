# EduPrompt — Notas sobre Engenharia de Prompt

**Autor:** Leonardo Gonçalves Sobral

## 1. Filosofia e Estratégia Geral

A engenharia de prompt no EduPrompt foi projetada com uma filosofia de **especialização e adaptabilidade máxima**. Em vez de um único prompt genérico, o sistema utiliza um **motor de engenharia de prompt (`prompt_engine.py`)** que constrói dinamicamente um prompt único para cada combinação de aluno, tópico e tipo de conteúdo. Isso garante que a IA receba um conjunto de instruções altamente otimizado, resultando em um conteúdo pedagógico de qualidade superior.

A estratégia se baseia em quatro técnicas avançadas de engenharia de prompt, aplicadas em camadas:

1.  **Persona Prompting:** A IA assume o papel de um especialista específico (ex: "professor experiente em Pedagogia", "educador socrático", "designer instrucional"). Isso ativa o conhecimento latente do modelo relacionado àquela área, melhorando a qualidade e o tom da resposta.

2.  **Context Setting:** O prompt injeta informações detalhadas sobre o aluno (idade, nível de conhecimento, estilo de aprendizado) e o tópico. O sistema utiliza mapeamentos (`MAPA_NIVEL`, `MAPA_ESTILO`, `MAPA_FAIXA_ETARIA`) para traduzir dados brutos em instruções contextuais ricas (ex: "linguagem simples e clara", "exemplos concretos do dia a dia", "tom lúdico e encorajador").

3.  **Chain-of-Thought (CoT):** Para tarefas complexas como a explicação conceitual, o prompt instrui a IA a "pensar passo a passo" antes de gerar a resposta final. A versão `v2` dos prompts formaliza isso em uma seção `## PROCESSO DE RACIOCÍNIO`, forçando o modelo a seguir uma estrutura lógica de análise, decomposição e estratégia pedagógica.

4.  **Output Formatting:** Todos os prompts contêm uma seção `## FORMATO DE SAÍDA` que especifica, de forma inequívoca, a estrutura exata da resposta desejada, incluindo o uso de Markdown, títulos, listas e blocos de código. Isso garante consistência e facilita a renderização no frontend.

## 2. Análise das Versões de Prompt (v1 vs. v2)

O sistema implementa duas versões de prompt para cada tipo de conteúdo, permitindo uma comparação direta da eficácia das estratégias. A versão `v2` é consistentemente mais detalhada e prescritiva, representando uma abordagem mais avançada.

| Característica | Versão v1 (Padrão) | Versão v2 (Avançado) |
| :--- | :--- | :--- |
| **Persona** | Persona simples e direta (ex: "professor experiente"). | Persona ultra-especializada com anos de experiência e credenciais (ex: "renomado educador e pesquisador com 20 anos de experiência"). |
| **Chain-of-Thought** | Instrução simples para "pensar passo a passo". | Seção formal `## PROCESSO DE RACIOCÍNIO` com etapas numeradas e específicas para a tarefa. |
| **Contexto** | Injeta o contexto do aluno de forma direta. | Reforça o contexto do aluno dentro das etapas do CoT, forçando uma análise mais profunda. |
| **Formato de Saída** | Estrutura básica com os elementos principais. | Estrutura mais rica e detalhada, com subseções adicionais (ex: "Conexões e Aplicações", "Legenda dos Símbolos", "Pergunta Bônus"). |
| **Tamanho** | Mais curto e conciso. | Significativamente mais longo e detalhado, fornecendo mais "tokens de exemplo" para o modelo. |

### Exemplo Prático: `gerar_prompt_explicacao_conceitual`

-   **Prompt v1:** Pede à IA para ser um "professor experiente" e "pensar passo a passo" de forma genérica. O formato de saída é simples.
-   **Prompt v2:** Define a persona como um "renomado educador e pesquisador em Pedagogia". O CoT é uma seção explícita com 5 passos, desde a análise do público até a verificação da compreensão. O formato de saída é mais robusto, incluindo seções como "Introdução Contextualizada" e "Conexões e Aplicações".

**Resultado esperado:** A versão `v2` tende a produzir respostas mais estruturadas, profundas e alinhadas com a intenção pedagógica, pois o processo de raciocínio guiado e a persona mais forte limitam a "margem de erro" criativa do modelo, focando-o na tarefa específica.

## 3. Estratégias por Tipo de Conteúdo

Cada tipo de conteúdo possui um prompt otimizado para sua finalidade específica:

-   **Explicação Conceitual:** Foco em **Chain-of-Thought** para garantir uma construção lógica e progressiva do conhecimento.
-   **Exemplos Práticos:** Foco em **Context Setting**, utilizando as referências culturais da faixa etária para criar exemplos que ressoem com o aluno.
-   **Perguntas de Reflexão:** Utiliza a **Taxonomia de Bloom** como estrutura no prompt `v2`, guiando a IA a criar perguntas que progridem de compreensão básica para análise, avaliação e criação.
-   **Resumo Visual:** Foco em **Output Formatting**, instruindo a IA a usar caracteres de `ASCII art` e a estruturar a informação em mapas mentais e diagramas dentro de blocos de código, garantindo a formatação correta.

## 4. Conclusão

A arquitetura de engenharia de prompt do EduPrompt é o núcleo da aplicação. Ao combinar múltiplas técnicas avançadas e especializar os prompts por tarefa, o sistema demonstra uma abordagem madura e eficaz para a geração de conteúdo de IA, alinhada com os critérios de avaliação do desafio. A capacidade de comparar as versões `v1` e `v2` serve como uma ferramenta poderosa para analisar e quantificar o impacto de diferentes estratégias de prompt engineering.
