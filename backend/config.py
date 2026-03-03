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
DATABASE_URL = os.getenv("DATABASE_URL", "")

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
try:
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
except (ValueError, TypeError):
    CACHE_TTL_SECONDS = 3600

# ─────────────────────────────────────────────
# Configurações do servidor Flask
# ─────────────────────────────────────────────
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
try:
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
except (ValueError, TypeError):
    FLASK_PORT = 5000
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# ─────────────────────────────────────────────
# Limites de segurança
# ─────────────────────────────────────────────
MAX_TOPICO_LENGTH = 200
MAX_NOME_LENGTH = 100
MAX_DESCRICAO_LENGTH = 500
MAX_PERFIS_CUSTOMIZADOS = 20
MAX_HISTORICO_ENTRIES = 500

# ─────────────────────────────────────────────
# Validação de configuração
# ─────────────────────────────────────────────
def validar_configuracao():
    """Verifica se as configurações essenciais estão presentes."""
    erros = []
    if not GEMINI_API_KEY:
        erros.append("GEMINI_API_KEY não configurada. Defina no arquivo .env")
    if FLASK_PORT < 1 or FLASK_PORT > 65535:
        erros.append(f"FLASK_PORT inválida: {FLASK_PORT}. Deve estar entre 1 e 65535")
    if CACHE_TTL_SECONDS < 0:
        erros.append(f"CACHE_TTL_SECONDS inválido: {CACHE_TTL_SECONDS}. Deve ser >= 0")
    return erros
