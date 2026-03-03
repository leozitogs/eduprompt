"""
Módulo de gerenciamento de perfis de alunos.
Suporta PostgreSQL como fonte primária e JSON como fallback.

Autor: Leonardo Gonçalves Sobral
"""

import json
import os
from backend.config import PERFIS_PATH

NIVEIS_VALIDOS = ["iniciante", "intermediario", "avancado"]
ESTILOS_VALIDOS = ["visual", "auditivo", "leitura-escrita", "cinestesico"]

_usar_db = None


def _check_db():
    global _usar_db
    if _usar_db is None:
        try:
            from backend.database import db_disponivel
            _usar_db = db_disponivel()
        except Exception:
            _usar_db = False
    return _usar_db


def carregar_perfis() -> list[dict]:
    if _check_db():
        from backend.database import listar_perfis_db
        perfis = listar_perfis_db()
        if perfis:
            return perfis

    if not os.path.exists(PERFIS_PATH):
        raise FileNotFoundError(f"Arquivo de perfis não encontrado: {PERFIS_PATH}")
    with open(PERFIS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def obter_perfil_por_id(perfil_id: int) -> dict | None:
    if _check_db():
        from backend.database import obter_perfil_db
        perfil = obter_perfil_db(perfil_id)
        if perfil:
            return perfil

    try:
        perfis = carregar_perfis()
    except FileNotFoundError:
        return None
    for perfil in perfis:
        if perfil.get("id") == perfil_id:
            return perfil
    return None


def listar_perfis_resumo() -> list[dict]:
    perfis = carregar_perfis()
    return [
        {
            "id": p["id"],
            "nome": p["nome"],
            "idade": p["idade"],
            "nivel": p["nivel"],
            "estilo_aprendizado": p["estilo_aprendizado"],
            "customizado": p.get("customizado", False)
        }
        for p in perfis
    ]


def validar_perfil(perfil: dict) -> list[str]:
    erros = []
    campos_obrigatorios = ["nome", "idade", "nivel", "estilo_aprendizado"]
    for campo in campos_obrigatorios:
        if campo not in perfil or not perfil[campo]:
            erros.append(f"Campo obrigatório ausente: {campo}")

    if "idade" in perfil:
        idade = perfil["idade"]
        if not isinstance(idade, int) or idade < 5 or idade > 100:
            erros.append("Idade deve ser um número inteiro entre 5 e 100")

    if "nivel" in perfil and perfil["nivel"] not in NIVEIS_VALIDOS:
        erros.append(f"Nível inválido: {perfil['nivel']}. Válidos: {NIVEIS_VALIDOS}")

    if "estilo_aprendizado" in perfil and perfil["estilo_aprendizado"] not in ESTILOS_VALIDOS:
        erros.append(f"Estilo inválido: {perfil['estilo_aprendizado']}. Válidos: {ESTILOS_VALIDOS}")

    return erros


def adicionar_perfil(perfil: dict) -> dict:
    erros = validar_perfil(perfil)
    if erros:
        raise ValueError(f"Perfil inválido: {'; '.join(erros)}")

    if _check_db():
        from backend.database import criar_perfil_db
        return criar_perfil_db(perfil)

    perfis = carregar_perfis()
    max_id = max((p.get("id", 0) for p in perfis), default=0)
    perfil["id"] = max_id + 1
    perfil["customizado"] = True
    perfis.append(perfil)

    with open(PERFIS_PATH, "w", encoding="utf-8") as f:
        json.dump(perfis, f, ensure_ascii=False, indent=2)

    return perfil


def deletar_perfil(perfil_id: int) -> bool:
    if _check_db():
        from backend.database import deletar_perfil_db
        return deletar_perfil_db(perfil_id)

    try:
        perfis = carregar_perfis()
    except FileNotFoundError:
        return False

    perfil = next((p for p in perfis if p.get("id") == perfil_id), None)
    if not perfil or not perfil.get("customizado", False):
        return False

    perfis = [p for p in perfis if p.get("id") != perfil_id]
    with open(PERFIS_PATH, "w", encoding="utf-8") as f:
        json.dump(perfis, f, ensure_ascii=False, indent=2)
    return True
