"""
Módulo de banco de dados PostgreSQL do EduPrompt.
Gerencia conexão, criação de tabelas e operações CRUD.
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from backend.config import DATABASE_URL


def _get_connection():
    if not DATABASE_URL:
        return None
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


@contextmanager
def get_db():
    conn = _get_connection()
    if conn is None:
        yield None
        return
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def db_disponivel() -> bool:
    try:
        with get_db() as conn:
            if conn is None:
                return False
            cur = conn.cursor()
            cur.execute("SELECT 1")
            return True
    except Exception:
        return False


def criar_tabelas():
    sql = """
    CREATE TABLE IF NOT EXISTS perfis_alunos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        idade INTEGER NOT NULL CHECK (idade >= 5 AND idade <= 100),
        nivel VARCHAR(20) NOT NULL CHECK (nivel IN ('iniciante', 'intermediario', 'avancado')),
        estilo_aprendizado VARCHAR(20) NOT NULL CHECK (estilo_aprendizado IN ('visual', 'auditivo', 'leitura-escrita', 'cinestesico')),
        descricao TEXT,
        customizado BOOLEAN DEFAULT FALSE,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS geracoes (
        id SERIAL PRIMARY KEY,
        perfil_id INTEGER REFERENCES perfis_alunos(id) ON DELETE SET NULL,
        perfil_nome VARCHAR(100),
        perfil_idade INTEGER,
        perfil_nivel VARCHAR(20),
        perfil_estilo VARCHAR(20),
        topico VARCHAR(255) NOT NULL,
        tipo_conteudo VARCHAR(50) NOT NULL,
        versao_prompt VARCHAR(5) NOT NULL,
        conteudo_gerado TEXT NOT NULL,
        prompt_utilizado TEXT,
        modelo VARCHAR(50),
        tokens_prompt INTEGER DEFAULT 0,
        tokens_resposta INTEGER DEFAULT 0,
        tempo_resposta_ms INTEGER DEFAULT 0,
        cache_hit BOOLEAN DEFAULT FALSE,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_db() as conn:
        if conn is None:
            return False
        cur = conn.cursor()
        cur.execute(sql)
        return True


def seed_perfis_iniciais(perfis_json: list):
    with get_db() as conn:
        if conn is None:
            return
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as total FROM perfis_alunos")
        row = cur.fetchone()
        if row["total"] > 0:
            return

        for p in perfis_json:
            cur.execute(
                """INSERT INTO perfis_alunos (nome, idade, nivel, estilo_aprendizado, descricao, customizado)
                   VALUES (%s, %s, %s, %s, %s, FALSE)""",
                (p["nome"], p["idade"], p["nivel"], p["estilo_aprendizado"], p.get("descricao", ""))
            )


# --- CRUD Perfis ---

def listar_perfis_db() -> list:
    with get_db() as conn:
        if conn is None:
            return []
        cur = conn.cursor()
        cur.execute("SELECT id, nome, idade, nivel, estilo_aprendizado, descricao, customizado FROM perfis_alunos ORDER BY id")
        return [dict(row) for row in cur.fetchall()]


def obter_perfil_db(perfil_id: int) -> dict | None:
    with get_db() as conn:
        if conn is None:
            return None
        cur = conn.cursor()
        cur.execute("SELECT * FROM perfis_alunos WHERE id = %s", (perfil_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def criar_perfil_db(dados: dict) -> dict:
    with get_db() as conn:
        if conn is None:
            raise ConnectionError("Banco de dados não disponível")
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO perfis_alunos (nome, idade, nivel, estilo_aprendizado, descricao, customizado)
               VALUES (%s, %s, %s, %s, %s, TRUE) RETURNING *""",
            (dados["nome"], dados["idade"], dados["nivel"], dados["estilo_aprendizado"], dados.get("descricao", ""))
        )
        return dict(cur.fetchone())


def deletar_perfil_db(perfil_id: int) -> bool:
    with get_db() as conn:
        if conn is None:
            return False
        cur = conn.cursor()
        cur.execute("SELECT customizado FROM perfis_alunos WHERE id = %s", (perfil_id,))
        row = cur.fetchone()
        if not row or not row["customizado"]:
            return False
        cur.execute("DELETE FROM perfis_alunos WHERE id = %s AND customizado = TRUE", (perfil_id,))
        return cur.rowcount > 0


# --- CRUD Gerações ---

def salvar_geracao_db(resultado: dict) -> int | None:
    with get_db() as conn:
        if conn is None:
            return None
        cur = conn.cursor()
        perfil = resultado.get("perfil", {})
        meta = resultado.get("metadados", {})
        cur.execute(
            """INSERT INTO geracoes
               (perfil_id, perfil_nome, perfil_idade, perfil_nivel, perfil_estilo,
                topico, tipo_conteudo, versao_prompt, conteudo_gerado, prompt_utilizado,
                modelo, tokens_prompt, tokens_resposta, tempo_resposta_ms, cache_hit)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (
                perfil.get("id"), perfil.get("nome"), perfil.get("idade"),
                perfil.get("nivel"), perfil.get("estilo_aprendizado"),
                resultado.get("topico"), resultado.get("tipo_conteudo"),
                resultado.get("versao_prompt"), resultado.get("conteudo_gerado"),
                resultado.get("prompt_utilizado"),
                meta.get("modelo"), meta.get("tokens_prompt", 0),
                meta.get("tokens_resposta", 0), meta.get("tempo_resposta_ms", 0),
                meta.get("cache_hit", False)
            )
        )
        row = cur.fetchone()
        return row["id"] if row else None


def listar_geracoes_db(perfil_id=None, topico=None, tipo_conteudo=None, limite=50) -> list:
    with get_db() as conn:
        if conn is None:
            return []
        cur = conn.cursor()
        query = "SELECT * FROM geracoes WHERE 1=1"
        params = []

        if perfil_id is not None:
            query += " AND perfil_id = %s"
            params.append(perfil_id)
        if topico:
            query += " AND LOWER(topico) LIKE %s"
            params.append(f"%{topico.lower()}%")
        if tipo_conteudo:
            query += " AND tipo_conteudo = %s"
            params.append(tipo_conteudo)

        query += " ORDER BY criado_em DESC LIMIT %s"
        params.append(limite)

        cur.execute(query, params)
        rows = cur.fetchall()

        resultados = []
        for row in rows:
            r = dict(row)
            r["timestamp"] = r.pop("criado_em").isoformat() if r.get("criado_em") else ""
            r["perfil"] = {
                "id": r.pop("perfil_id", None),
                "nome": r.pop("perfil_nome", ""),
                "idade": r.pop("perfil_idade", 0),
                "nivel": r.pop("perfil_nivel", ""),
                "estilo_aprendizado": r.pop("perfil_estilo", "")
            }
            r["metadados"] = {
                "modelo": r.pop("modelo", ""),
                "tokens_prompt": r.pop("tokens_prompt", 0),
                "tokens_resposta": r.pop("tokens_resposta", 0),
                "tempo_resposta_ms": r.pop("tempo_resposta_ms", 0),
                "cache_hit": r.pop("cache_hit", False)
            }
            r.pop("id", None)
            resultados.append(r)

        return resultados
