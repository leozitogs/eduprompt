# EduPrompt

Plataforma educativa que gera conteúdo personalizado com IA utilizando técnicas avançadas de engenharia de prompt. Desenvolvido como desafio técnico para vaga de estágio em IA.

## ✨ Funcionalidades

- **Geração Personalizada**: Cria conteúdo educacional adaptado ao perfil do aluno (idade, nível, estilo de aprendizado)
- **4 Tipos de Conteúdo**: Explicação Conceitual, Exemplos Práticos, Perguntas de Reflexão, Resumo Visual
- **Comparação de Prompts**: Compare versões v1 (padrão) e v2 (avançado) lado a lado
- **CRUD de Perfis**: Crie e gerencie perfis de alunos customizados
- **Galeria de Samples**: Explore exemplos de conteúdos pré-gerados
- **Banco de Dados PostgreSQL**: Persista perfis e histórico com fallback para JSON
- **Histórico de Gerações**: Todas as gerações são salvas automaticamente
- **Interface Moderna**: Design responsivo com animações e UX polida

## 🏛️ Arquitetura

**Backend**: Flask (Python) com API RESTful  
**Frontend**: HTML5, CSS3, JavaScript Vanilla  
**Banco de Dados**: PostgreSQL (com fallback JSON)  
**IA**: Google Gemini 2.5 Flash  

### Backend

- `app.py` — Servidor Flask com endpoints da API
- `backend/prompt_engine.py` — Motor de engenharia de prompt dinâmico
- `backend/gemini_client.py` — Cliente para API do Gemini com cache
- `backend/database.py` — Camada de persistência (PostgreSQL + JSON fallback)
- `backend/perfis.py` — Gerenciamento de perfis de alunos
- `backend/gerador.py` — Orquestra a geração de conteúdo
- `backend/samples.py` — Carregamento de exemplos pré-gerados
- `backend/cache.py` — Sistema de cache de respostas

### Frontend

- `frontend/index.html` — Estrutura da SPA com 5 seções (Hero, Gerador, Perfis, Samples, Histórico)
- `frontend/js/app.js` — Lógica do cliente, chamadas de API, gerenciamento de estado
- `frontend/js/particles.js` — Animação de partículas do hero
- `frontend/css/style.css` — Estilos com tema escuro, animações e responsividade

## 🚀 Quick Start

### Pré-requisitos

- Python 3.10+
- pip
- (Opcional) PostgreSQL local ou Neon

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/eduprompt.git
cd eduprompt

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua GEMINI_API_KEY
```

### Executar Localmente

```bash
python app.py
```

Acesse [http://localhost:5000](http://localhost:5000) no navegador.

## 📝 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/perfis` | Lista todos os perfis |
| `POST` | `/api/perfis` | Cria novo perfil customizado |
| `DELETE` | `/api/perfis/<id>` | Deleta perfil customizado |
| `POST` | `/api/gerar` | Gera um tipo de conteúdo |
| `POST` | `/api/gerar-todos` | Gera todos os 4 tipos |
| `POST` | `/api/comparar` | Compara v1 vs v2 |
| `GET` | `/api/historico` | Retorna histórico de gerações |
| `GET` | `/api/samples` | Lista samples disponíveis |
| `GET` | `/api/samples/<arquivo>` | Obtém um sample específico |
| `GET` | `/api/status` | Status do sistema (DB, cache, API) |

## 🔧 Configuração

### Variáveis de Ambiente

```ini
# .env
GEMINI_API_KEY=sua_chave_aqui
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require  # Opcional
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600
FLASK_DEBUG=false
```

Se `DATABASE_URL` não for configurada, o sistema usa JSON local em `/data`.

## 📂 Estrutura

```
eduprompt/
├── backend/
│   ├── cache.py
│   ├── config.py
│   ├── database.py
│   ├── gemini_client.py
│   ├── gerador.py
│   ├── perfis.py
│   ├── prompt_engine.py
│   └── samples.py
├── frontend/
│   ├── css/style.css
│   ├── js/app.js
│   ├── js/particles.js
│   └── index.html
├── data/
│   └── perfis_alunos.json
├── samples/
│   └── *.json (exemplos pré-gerados)
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── GUIA_DEPLOY.md
└── PROMPT_ENGINEERING_NOTES.md
```

## 🎯 Engenharia de Prompt

O sistema utiliza um motor dinâmico que constrói prompts otimizados para cada combinação de aluno, tópico e tipo de conteúdo. Técnicas aplicadas:

- **Persona Prompting**: A IA assume papel de especialista
- **Context Setting**: Injeta dados do aluno (idade, nível, estilo)
- **Chain-of-Thought**: Instrui o modelo a "pensar passo a passo"
- **Output Formatting**: Especifica estrutura exata da resposta

Veja `PROMPT_ENGINEERING_NOTES.md` para análise detalhada das versões v1 e v2.

## 🗄️ Banco de Dados

### Tabelas

**perfis_alunos**
```sql
id SERIAL PRIMARY KEY
nome VARCHAR(100)
idade INTEGER (5-100)
nivel VARCHAR(20) ('iniciante', 'intermediario', 'avancado')
estilo_aprendizado VARCHAR(20) ('visual', 'auditivo', 'leitura-escrita', 'cinestesico')
descricao TEXT
customizado BOOLEAN
criado_em TIMESTAMP
```

**geracoes**
```sql
id SERIAL PRIMARY KEY
perfil_id INTEGER (FK)
topico VARCHAR(255)
tipo_conteudo VARCHAR(50)
versao_prompt VARCHAR(5)
conteudo_gerado TEXT
prompt_utilizado TEXT
modelo VARCHAR(50)
tokens_prompt INTEGER
tokens_resposta INTEGER
tempo_resposta_ms INTEGER
cache_hit BOOLEAN
criado_em TIMESTAMP
```

## 🎨 Interface

- **Hero Section**: Apresentação com animação de partículas
- **Gerador**: Painel lateral com formulário + área de resultados
- **Perfis**: Grid de perfis com CRUD e badges (Padrão/Customizado)
- **Samples**: Galeria de exemplos com modal de visualização
- **Histórico**: Lista de gerações anteriores com filtros
- **Modal**: Visualização de conteúdo completo com Markdown renderizado

## 📦 Dependências

```
flask==3.1.0
flask-cors==5.0.1
python-dotenv==1.1.0
openai==1.68.2
requests==2.32.3
psycopg2-binary==2.9.10
gunicorn==23.0.0
```

## 🚀 Deploy

Veja `GUIA_DEPLOY.md` para instruções de deploy em Render (backend), Vercel (frontend) e Neon (database).

## 📄 Licença

Este projeto foi desenvolvido como desafio técnico. Sinta-se livre para usar como referência.

---

**Autor**: Leonardo Gonçalves Sobral  
**Desafio**: Estágio em IA e Engenharia de Prompt
