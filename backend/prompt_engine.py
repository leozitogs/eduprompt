"""
Motor de Engenharia de Prompt — Módulo Central do EduPrompt.

Este módulo implementa a construção dinâmica de prompts otimizados
utilizando técnicas avançadas de engenharia de prompt:
  - Persona Prompting
  - Context Setting
  - Chain-of-Thought
  - Output Formatting

Cada tipo de conteúdo possui sua própria função geradora de prompt,
garantindo especialização e qualidade máxima na saída.

Autor: Leonardo Gonçalves Sobral
"""

# ─────────────────────────────────────────────────────────────────
# Mapeamentos de contexto para personalização dos prompts
# ─────────────────────────────────────────────────────────────────

MAPA_NIVEL = {
    "iniciante": {
        "descricao": "iniciante, com pouco ou nenhum conhecimento prévio sobre o assunto",
        "linguagem": "simples, clara e acessível, evitando jargões técnicos",
        "profundidade": "introdutória, com foco em conceitos fundamentais e analogias do cotidiano",
        "exemplos": "concretos e do dia a dia, que o aluno possa facilmente relacionar com sua experiência"
    },
    "intermediario": {
        "descricao": "intermediário, com conhecimento básico já consolidado",
        "linguagem": "moderada, podendo introduzir termos técnicos com explicações breves",
        "profundidade": "moderada, conectando conceitos básicos a aplicações mais complexas",
        "exemplos": "que demonstrem aplicações práticas e conexões entre conceitos"
    },
    "avancado": {
        "descricao": "avançado, com sólida base de conhecimento no tema",
        "linguagem": "técnica e precisa, utilizando terminologia especializada da área",
        "profundidade": "aprofundada, explorando nuances, exceções e fronteiras do conhecimento",
        "exemplos": "sofisticados, incluindo estudos de caso, cenários complexos e análises críticas"
    }
}

MAPA_ESTILO = {
    "visual": {
        "descricao": "visual — aprende melhor com diagramas, esquemas, cores e representações gráficas",
        "instrucao": "Use descrições visuais ricas, sugira diagramas, utilize marcadores visuais como emojis temáticos, crie representações em ASCII art quando possível, e organize informações em tabelas e esquemas visuais.",
        "formato_preferido": "Organize com hierarquia visual clara, use listas com ícones, tabelas comparativas e representações esquemáticas."
    },
    "auditivo": {
        "descricao": "auditivo — absorve melhor conteúdo através de explicações verbais e discussões",
        "instrucao": "Escreva como se estivesse explicando em uma conversa, use ritmo narrativo, inclua perguntas retóricas, crie diálogos ilustrativos e sugira que o aluno leia em voz alta ou explique para alguém.",
        "formato_preferido": "Use tom conversacional, inclua frases de transição naturais e estruture como uma explicação oral fluida."
    },
    "leitura-escrita": {
        "descricao": "leitura-escrita — prefere textos bem estruturados, anotações e resumos escritos",
        "instrucao": "Forneça textos bem estruturados com parágrafos claros, definições precisas, listas organizadas, referências cruzadas e sugira que o aluno faça anotações e resumos próprios.",
        "formato_preferido": "Use estrutura acadêmica com introdução, desenvolvimento e conclusão. Inclua definições formais e vocabulário rico."
    },
    "cinestesico": {
        "descricao": "cinestésico — aprende melhor com atividades práticas, experimentos e interação",
        "instrucao": "Proponha atividades hands-on, experimentos simples, simulações mentais passo a passo, exercícios práticos e convide o aluno a 'fazer' algo concreto com o conhecimento.",
        "formato_preferido": "Estruture como um guia prático com passos numerados, atividades interativas e desafios para executar."
    }
}

MAPA_FAIXA_ETARIA = {
    (5, 10): {
        "tom": "lúdico, divertido e encorajador, como um professor amigável",
        "referencias": "desenhos animados, brincadeiras, jogos, animais e situações do universo infantil",
        "complexidade": "frases curtas e diretas, vocabulário simples, muitas analogias concretas"
    },
    (11, 14): {
        "tom": "engajante e curioso, estimulando a descoberta",
        "referencias": "redes sociais, jogos, esportes, tecnologia e cultura pop adolescente",
        "complexidade": "frases de complexidade moderada, introdução gradual de conceitos abstratos"
    },
    (15, 18): {
        "tom": "respeitoso e instigante, tratando como jovem adulto",
        "referencias": "vestibular, carreira, tecnologia, atualidades e questões sociais",
        "complexidade": "textos mais elaborados, pensamento crítico e conexões interdisciplinares"
    },
    (19, 100): {
        "tom": "profissional e direto, como entre colegas acadêmicos",
        "referencias": "mercado de trabalho, pesquisa, aplicações profissionais e acadêmicas",
        "complexidade": "textos densos, análise crítica, múltiplas perspectivas e profundidade teórica"
    }
}


def _obter_contexto_faixa_etaria(idade: int) -> dict:
    """Retorna o contexto adequado para a faixa etária do aluno."""
    for (min_idade, max_idade), contexto in MAPA_FAIXA_ETARIA.items():
        if min_idade <= idade <= max_idade:
            return contexto
    # Fallback para adultos
    return MAPA_FAIXA_ETARIA[(19, 100)]


# ─────────────────────────────────────────────────────────────────
# Funções geradoras de prompt — uma para cada tipo de conteúdo
# ─────────────────────────────────────────────────────────────────

def gerar_prompt_explicacao_conceitual(perfil: dict, topico: str, versao_prompt: str = "v1") -> str:
    """
    Gera o prompt para EXPLICAÇÃO CONCEITUAL usando Chain-of-Thought.
    
    Técnicas aplicadas:
    - Persona Prompting: Define o papel de professor especialista
    - Context Setting: Injeta dados completos do perfil do aluno
    - Chain-of-Thought: Solicita raciocínio passo a passo
    - Output Formatting: Especifica estrutura exata da resposta
    
    Args:
        perfil: Dicionário com dados do aluno.
        topico: Tópico a ser ensinado.
        versao_prompt: Versão do prompt para comparação (v1 ou v2).
    
    Returns:
        str: Prompt completo e otimizado.
    """
    nivel_ctx = MAPA_NIVEL[perfil["nivel"]]
    estilo_ctx = MAPA_ESTILO[perfil["estilo_aprendizado"]]
    idade_ctx = _obter_contexto_faixa_etaria(perfil["idade"])

    if versao_prompt == "v2":
        # Versão alternativa com abordagem diferente para comparação
        return f"""Você é um renomado educador e pesquisador em Pedagogia com 20 anos de experiência em ensino adaptativo e diferenciação pedagógica. Sua especialidade é transformar conceitos complexos em explicações cristalinas, adaptadas ao perfil cognitivo de cada estudante.

## CONTEXTO DO ALUNO
- **Nome:** {perfil['nome']}
- **Idade:** {perfil['idade']} anos
- **Nível de conhecimento:** {nivel_ctx['descricao']}
- **Estilo de aprendizado:** {estilo_ctx['descricao']}

## TAREFA
Elabore uma explicação conceitual completa e aprofundada sobre **{topico}**.

## PROCESSO DE RACIOCÍNIO (Chain-of-Thought)
Antes de redigir a explicação final, siga este processo mental passo a passo:

1. **Análise do público:** Considere que {perfil['nome']} tem {perfil['idade']} anos e é {nivel_ctx['descricao']}. Que conhecimentos prévios essa pessoa provavelmente possui?
2. **Decomposição do tópico:** Quebre "{topico}" em seus componentes fundamentais. Quais são os pré-requisitos conceituais?
3. **Estratégia pedagógica:** Dado que o aluno é {estilo_ctx['descricao']}, qual a melhor abordagem para apresentar cada componente?
4. **Construção progressiva:** Organize os conceitos do mais simples ao mais complexo, criando uma narrativa lógica.
5. **Verificação de compreensão:** Inclua momentos de verificação para garantir que o aluno acompanha o raciocínio.

## DIRETRIZES DE LINGUAGEM
- Tom: {idade_ctx['tom']}
- Referências culturais: {idade_ctx['referencias']}
- Complexidade textual: {idade_ctx['complexidade']}
- Linguagem: {nivel_ctx['linguagem']}
- {estilo_ctx['instrucao']}

## FORMATO DE SAÍDA OBRIGATÓRIO
Estruture a resposta EXATAMENTE neste formato:

### 📚 Explicação Conceitual: {topico}

**Introdução Contextualizada**
[Parágrafo que conecta o tópico ao universo do aluno, despertando curiosidade]

**Desenvolvimento Passo a Passo**
[Explicação progressiva com raciocínio encadeado, usando analogias adequadas à faixa etária]

**Conceitos-Chave**
[Lista dos conceitos fundamentais com definições claras]

**Conexões e Aplicações**
[Como este tópico se conecta com outros conhecimentos e com o mundo real]

**Resumo**
[Síntese concisa dos pontos principais]

IMPORTANTE: A explicação deve ter profundidade {nivel_ctx['profundidade']}. Use exemplos {nivel_ctx['exemplos']}. {estilo_ctx['formato_preferido']}"""

    # Versão v1 — prompt padrão
    return f"""Você é um professor experiente em Pedagogia, especializado em ensino personalizado e adaptativo. Você domina técnicas de diferenciação pedagógica e sabe adaptar sua comunicação para diferentes perfis de alunos.

## CONTEXTO DO ALUNO
- **Nome:** {perfil['nome']}
- **Idade:** {perfil['idade']} anos
- **Nível de conhecimento:** {nivel_ctx['descricao']}
- **Estilo de aprendizado:** {estilo_ctx['descricao']}

## TAREFA
Crie uma explicação conceitual clara e envolvente sobre **{topico}** para este aluno específico.

## INSTRUÇÕES DE RACIOCÍNIO (Pense passo a passo)
1. Primeiro, considere o que um aluno de {perfil['idade']} anos com nível {perfil['nivel']} já sabe sobre o tema.
2. Identifique os conceitos fundamentais que precisam ser explicados.
3. Escolha analogias e exemplos adequados para a faixa etária e estilo de aprendizado.
4. Construa a explicação de forma progressiva, do simples ao complexo.

## DIRETRIZES
- Tom: {idade_ctx['tom']}
- Linguagem: {nivel_ctx['linguagem']}
- Profundidade: {nivel_ctx['profundidade']}
- Exemplos: {nivel_ctx['exemplos']}
- {estilo_ctx['instrucao']}

## FORMATO DE SAÍDA
Estruture a resposta assim:

### 📚 Explicação Conceitual: {topico}

**Introdução**
[Contextualize o tema de forma atrativa para o aluno]

**Desenvolvimento**
[Explicação passo a passo com analogias e exemplos]

**Conceitos-Chave**
[Liste os conceitos fundamentais]

**Resumo**
[Síntese dos pontos principais]"""


def gerar_prompt_exemplos_praticos(perfil: dict, topico: str, versao_prompt: str = "v1") -> str:
    """
    Gera o prompt para EXEMPLOS PRÁTICOS contextualizados.
    
    Técnicas aplicadas:
    - Persona Prompting: Tutor prático com foco em aplicações reais
    - Context Setting: Adapta exemplos à idade e realidade do aluno
    - Output Formatting: Estrutura com cenários numerados
    """
    nivel_ctx = MAPA_NIVEL[perfil["nivel"]]
    estilo_ctx = MAPA_ESTILO[perfil["estilo_aprendizado"]]
    idade_ctx = _obter_contexto_faixa_etaria(perfil["idade"])

    if versao_prompt == "v2":
        return f"""Você é um tutor criativo e inovador, especialista em aprendizagem baseada em problemas (PBL) e contextualização pedagógica. Sua missão é tornar qualquer conceito tangível e memorável através de exemplos práticos brilhantes.

## PERFIL DO ALUNO
- **Nome:** {perfil['nome']} | **Idade:** {perfil['idade']} anos
- **Nível:** {nivel_ctx['descricao']}
- **Estilo:** {estilo_ctx['descricao']}

## MISSÃO
Crie exemplos práticos extraordinários sobre **{topico}** que façam {perfil['nome']} não apenas entender, mas se empolgar com o conceito.

## PROCESSO CRIATIVO (Pense passo a passo)
1. **Mapeie o universo do aluno:** O que uma pessoa de {perfil['idade']} anos vivencia no dia a dia? Quais são seus interesses prováveis?
2. **Conecte ao tópico:** Como "{topico}" se manifesta nesse universo?
3. **Gradue a complexidade:** Comece com um exemplo intuitivo e avance para aplicações mais sofisticadas.
4. **Diversifique os contextos:** Cubra diferentes áreas (cotidiano, tecnologia, natureza, sociedade).

## DIRETRIZES
- Referências culturais: {idade_ctx['referencias']}
- Complexidade: {idade_ctx['complexidade']}
- Exemplos devem ser: {nivel_ctx['exemplos']}
- {estilo_ctx['instrucao']}

## FORMATO DE SAÍDA OBRIGATÓRIO

### 🔬 Exemplos Práticos: {topico}

**Exemplo 1: [Título Criativo]**
- 📌 **Cenário:** [Descrição vivida da situação]
- 🔍 **Conexão com o conceito:** [Como o exemplo ilustra {topico}]
- 💡 **O que aprendemos:** [Insight principal]

**Exemplo 2: [Título Criativo]**
[Mesmo formato]

**Exemplo 3: [Título Criativo]**
[Mesmo formato]

**Exemplo 4: [Título Criativo — Desafio]**
[Um exemplo mais complexo que desafia o aluno a pensar além]

**🔗 Conexão entre os exemplos**
[Como os exemplos se relacionam e constroem uma compreensão mais completa]"""

    # Versão v1
    return f"""Você é um tutor prático e criativo, especializado em criar exemplos do mundo real que tornam conceitos abstratos em algo tangível e memorável.

## CONTEXTO DO ALUNO
- **Nome:** {perfil['nome']}
- **Idade:** {perfil['idade']} anos
- **Nível:** {nivel_ctx['descricao']}
- **Estilo de aprendizado:** {estilo_ctx['descricao']}

## TAREFA
Crie exemplos práticos e contextualizados sobre **{topico}** adequados para este aluno.

## INSTRUÇÕES
1. Pense em situações do cotidiano de uma pessoa de {perfil['idade']} anos.
2. Relacione essas situações com o conceito de {topico}.
3. Crie exemplos progressivos em complexidade.
4. Use referências que ressoem com: {idade_ctx['referencias']}

## DIRETRIZES
- Tom: {idade_ctx['tom']}
- Os exemplos devem ser: {nivel_ctx['exemplos']}
- {estilo_ctx['instrucao']}

## FORMATO DE SAÍDA

### 🔬 Exemplos Práticos: {topico}

**Exemplo 1: [Título]**
- **Cenário:** [Situação prática]
- **Conexão:** [Como se relaciona com {topico}]
- **Aprendizado:** [O que isso ensina]

**Exemplo 2: [Título]**
[Mesmo formato]

**Exemplo 3: [Título]**
[Mesmo formato]

**Desafio Prático**
[Uma atividade que o aluno pode fazer para aplicar o conhecimento]"""


def gerar_prompt_perguntas_reflexao(perfil: dict, topico: str, versao_prompt: str = "v1") -> str:
    """
    Gera o prompt para PERGUNTAS DE REFLEXÃO que estimulam pensamento crítico.
    
    Técnicas aplicadas:
    - Persona Prompting: Filósofo socrático / educador crítico
    - Context Setting: Calibra profundidade das perguntas ao nível
    - Chain-of-Thought: Guia o raciocínio por trás de cada pergunta
    - Output Formatting: Taxonomia de Bloom como estrutura
    """
    nivel_ctx = MAPA_NIVEL[perfil["nivel"]]
    estilo_ctx = MAPA_ESTILO[perfil["estilo_aprendizado"]]
    idade_ctx = _obter_contexto_faixa_etaria(perfil["idade"])

    if versao_prompt == "v2":
        return f"""Você é um educador socrático com profundo conhecimento em Taxonomia de Bloom e técnicas de pensamento crítico. Sua especialidade é formular perguntas que não apenas testam conhecimento, mas transformam a forma como o aluno pensa.

## PERFIL DO ALUNO
- **Nome:** {perfil['nome']} | **Idade:** {perfil['idade']} anos
- **Nível:** {nivel_ctx['descricao']}
- **Estilo:** {estilo_ctx['descricao']}

## MISSÃO
Crie um conjunto de perguntas de reflexão sobre **{topico}** que guiem {perfil['nome']} em uma jornada de pensamento crítico progressivo.

## PROCESSO DE CONSTRUÇÃO (Chain-of-Thought)
1. **Nível Recordar:** Que perguntas verificam se o aluno lembra dos conceitos básicos?
2. **Nível Compreender:** Que perguntas testam se o aluno realmente entendeu (não apenas memorizou)?
3. **Nível Aplicar:** Como o aluno pode usar este conhecimento em situações novas?
4. **Nível Analisar:** Que perguntas levam o aluno a decompor e examinar o tema criticamente?
5. **Nível Avaliar:** Que perguntas pedem julgamento fundamentado?
6. **Nível Criar:** Que perguntas desafiam o aluno a gerar algo novo a partir do conhecimento?

## DIRETRIZES
- Tom: {idade_ctx['tom']}
- Complexidade: {idade_ctx['complexidade']}
- {estilo_ctx['instrucao']}
- Cada pergunta deve ter uma dica sutil que guie o raciocínio sem entregar a resposta.

## FORMATO DE SAÍDA OBRIGATÓRIO

### 🤔 Perguntas de Reflexão: {topico}

**Nível 1 — Compreensão Fundamental**
1. [Pergunta que verifica entendimento básico]
   💭 *Dica para reflexão:* [Pista sutil]

**Nível 2 — Aplicação e Análise**
2. [Pergunta que exige aplicação do conceito]
   💭 *Dica para reflexão:* [Pista sutil]
3. [Pergunta analítica]
   💭 *Dica para reflexão:* [Pista sutil]

**Nível 3 — Pensamento Crítico**
4. [Pergunta que exige avaliação ou julgamento]
   💭 *Dica para reflexão:* [Pista sutil]
5. [Pergunta que desafia suposições]
   💭 *Dica para reflexão:* [Pista sutil]

**Nível 4 — Criação e Síntese**
6. [Pergunta aberta que convida à criação de algo novo]
   💭 *Dica para reflexão:* [Pista sutil]

**🎯 Pergunta Bônus (Interdisciplinar)**
7. [Pergunta que conecta {topico} com outra área do conhecimento]"""

    # Versão v1
    return f"""Você é um professor que utiliza o método socrático para estimular o pensamento crítico dos alunos. Você formula perguntas que desafiam, provocam reflexão e levam a insights profundos.

## CONTEXTO DO ALUNO
- **Nome:** {perfil['nome']}
- **Idade:** {perfil['idade']} anos
- **Nível:** {nivel_ctx['descricao']}
- **Estilo de aprendizado:** {estilo_ctx['descricao']}

## TAREFA
Crie perguntas de reflexão sobre **{topico}** que estimulem o pensamento crítico deste aluno.

## INSTRUÇÕES
1. Comece com perguntas de compreensão básica.
2. Avance para perguntas de aplicação e análise.
3. Inclua perguntas que desafiem suposições.
4. Finalize com perguntas de síntese e criação.
5. Adapte a complexidade para o nível {perfil['nivel']}.

## DIRETRIZES
- Tom: {idade_ctx['tom']}
- Complexidade: {idade_ctx['complexidade']}
- {estilo_ctx['instrucao']}

## FORMATO DE SAÍDA

### 🤔 Perguntas de Reflexão: {topico}

**Compreensão**
1. [Pergunta básica]

**Aplicação e Análise**
2. [Pergunta de aplicação]
3. [Pergunta analítica]

**Pensamento Crítico**
4. [Pergunta que desafia]
5. [Pergunta provocativa]

**Criação**
6. [Pergunta aberta e criativa]"""


def gerar_prompt_resumo_visual(perfil: dict, topico: str, versao_prompt: str = "v1") -> str:
    """
    Gera o prompt para RESUMO EM FORMATO VISUAL (mapa mental/diagrama ASCII).
    
    Técnicas aplicadas:
    - Persona Prompting: Designer instrucional / especialista em visualização
    - Context Setting: Adapta complexidade visual ao perfil
    - Output Formatting: Solicita explicitamente ASCII art e estrutura visual
    """
    nivel_ctx = MAPA_NIVEL[perfil["nivel"]]
    estilo_ctx = MAPA_ESTILO[perfil["estilo_aprendizado"]]
    idade_ctx = _obter_contexto_faixa_etaria(perfil["idade"])

    if versao_prompt == "v2":
        return f"""Você é um designer instrucional e especialista em visualização de informações, com vasta experiência em criar mapas mentais, diagramas e representações visuais que facilitam a memorização e compreensão de conceitos complexos.

## PERFIL DO ALUNO
- **Nome:** {perfil['nome']} | **Idade:** {perfil['idade']} anos
- **Nível:** {nivel_ctx['descricao']}
- **Estilo:** {estilo_ctx['descricao']}

## MISSÃO
Crie um resumo visual completo e memorável sobre **{topico}** utilizando representações em texto (ASCII art, diagramas de texto, mapas mentais em texto).

## PROCESSO DE DESIGN (Chain-of-Thought)
1. **Identifique o conceito central** de {topico}.
2. **Mapeie os sub-conceitos** e suas relações hierárquicas.
3. **Escolha a melhor representação visual:** mapa mental, fluxograma, diagrama de relações ou tabela comparativa.
4. **Construa a representação** usando caracteres ASCII de forma clara e legível.
5. **Adicione uma legenda** explicando os símbolos utilizados.

## DIRETRIZES
- Profundidade: {nivel_ctx['profundidade']}
- {estilo_ctx['instrucao']}
- Use caracteres como: ─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ► ◄ ▲ ▼ ● ○ ■ □ ★ → ← ↑ ↓
- O diagrama deve ser legível em fonte monoespaçada.

## FORMATO DE SAÍDA OBRIGATÓRIO

### 🗺️ Resumo Visual: {topico}

**Mapa Mental / Diagrama Principal**
```
[Diagrama ASCII art detalhado e bem formatado representando a estrutura do tópico]
```

**Legenda dos Símbolos**
[Explicação dos símbolos utilizados no diagrama]

**Tabela de Conceitos-Chave**
| Conceito | Definição Resumida | Importância |
|----------|-------------------|-------------|
| ... | ... | ... |

**Fluxograma de Relações**
```
[Diagrama mostrando como os conceitos se conectam]
```

**Dica de Memorização**
[Mnemônico ou técnica visual para lembrar os conceitos principais]"""

    # Versão v1
    return f"""Você é um especialista em criar resumos visuais e mapas mentais que facilitam o aprendizado e a memorização.

## CONTEXTO DO ALUNO
- **Nome:** {perfil['nome']}
- **Idade:** {perfil['idade']} anos
- **Nível:** {nivel_ctx['descricao']}
- **Estilo de aprendizado:** {estilo_ctx['descricao']}

## TAREFA
Crie um resumo em formato visual sobre **{topico}** usando diagramas em ASCII art e representações textuais.

## INSTRUÇÕES
1. Identifique os conceitos centrais de {topico}.
2. Organize em uma estrutura hierárquica ou relacional.
3. Crie um mapa mental ou diagrama usando caracteres ASCII.
4. Adicione uma tabela resumo dos conceitos-chave.

## DIRETRIZES
- Profundidade: {nivel_ctx['profundidade']}
- {estilo_ctx['instrucao']}
- Use caracteres como: ─ │ ┌ ┐ └ ┘ ├ ┤ → ● ○ ★

## FORMATO DE SAÍDA

### 🗺️ Resumo Visual: {topico}

**Mapa Mental**
```
[Diagrama ASCII representando a estrutura do tópico]
```

**Conceitos-Chave**
| Conceito | Definição |
|----------|-----------|
| ... | ... |

**Dica de Memorização**
[Técnica para lembrar os conceitos]"""


# ─────────────────────────────────────────────────────────────────
# Função principal de despacho
# ─────────────────────────────────────────────────────────────────

# Mapeamento dos tipos de conteúdo para suas funções geradoras
GERADORES_PROMPT = {
    "explicacao_conceitual": gerar_prompt_explicacao_conceitual,
    "exemplos_praticos": gerar_prompt_exemplos_praticos,
    "perguntas_reflexao": gerar_prompt_perguntas_reflexao,
    "resumo_visual": gerar_prompt_resumo_visual
}

TIPOS_CONTEUDO = list(GERADORES_PROMPT.keys())

NOMES_TIPOS = {
    "explicacao_conceitual": "Explicação Conceitual",
    "exemplos_praticos": "Exemplos Práticos",
    "perguntas_reflexao": "Perguntas de Reflexão",
    "resumo_visual": "Resumo Visual"
}


def gerar_prompt(tipo_conteudo: str, perfil: dict, topico: str, versao_prompt: str = "v1") -> str:
    """
    Função principal que despacha a geração de prompt para a função especializada.
    
    Args:
        tipo_conteudo: Um dos tipos em TIPOS_CONTEUDO.
        perfil: Dicionário com dados do aluno.
        topico: Tópico a ser ensinado.
        versao_prompt: Versão do prompt (v1 ou v2) para comparação.
    
    Returns:
        str: Prompt completo e otimizado.
    
    Raises:
        ValueError: Se o tipo de conteúdo for inválido.
    """
    if tipo_conteudo not in GERADORES_PROMPT:
        raise ValueError(
            f"Tipo de conteúdo inválido: '{tipo_conteudo}'. "
            f"Tipos válidos: {TIPOS_CONTEUDO}"
        )

    gerador = GERADORES_PROMPT[tipo_conteudo]
    return gerador(perfil, topico, versao_prompt)
