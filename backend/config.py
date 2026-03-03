"""
Módulo de configuração do EduPrompt.
Carrega variáveis de ambiente e define constantes do sistema.

Autor: Leonardo Gonçalves Sobral
"""

import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv(override=True)

# ─────────────────────────────────────────────
# Configuração da API Gemini
# ─────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")

# ─────────────────────────────────────────────
# Banco de dados PostgreSQL (Neon)
# ─────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:leozinho10@localhost:5432/eduprompt?sslmode=disable")

# ─────────────────────────────────────────────
# Caminhos do projeto
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
PERFIS_PATH = os.path.join(DATA_DIR, "perfis_alunos.json")
HISTORICO_PATH = os.path.join(DATA_DIR, "historico_geracoes.json")

# ─────────────────────────────────────────────
# Configurações de cache
# ─────────────────────────────────────────────
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hora padrão

# ─────────────────────────────────────────────
# Configurações do servidor Flask
# ─────────────────────────────────────────────
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# ─────────────────────────────────────────────
# Validação de configuração
# ─────────────────────────────────────────────
def validar_configuracao():
    """Verifica se as configurações essenciais estão presentes."""
    erros = []
    if not GEMINI_API_KEY:
        erros.append("GEMINI_API_KEY não configurada. Defina no arquivo .env")
    return erros
