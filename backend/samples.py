"""
Módulo de gerenciamento dos samples pré-gerados.
Permite listar, visualizar e carregar exemplos de output do diretório /samples.

Autor: Leonardo Gonçalves Sobral
"""

import json
import os
from backend.config import SAMPLES_DIR


def listar_samples() -> list[dict]:
    if not os.path.exists(SAMPLES_DIR):
        return []

    samples = []
    for arquivo in sorted(os.listdir(SAMPLES_DIR)):
        if not arquivo.endswith(".json"):
            continue
        caminho = os.path.join(SAMPLES_DIR, arquivo)
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            samples.append({
                "arquivo": arquivo,
                "perfil_nome": dados.get("perfil", {}).get("nome", ""),
                "topico": dados.get("topico", ""),
                "tipo_conteudo": dados.get("tipo_conteudo", ""),
                "tipo_conteudo_nome": dados.get("tipo_conteudo_nome", ""),
                "versao_prompt": dados.get("versao_prompt", ""),
                "timestamp": dados.get("timestamp", "")
            })
        except (json.JSONDecodeError, OSError):
            continue

    return samples


def obter_sample(nome_arquivo: str) -> dict | None:
    caminho = os.path.join(SAMPLES_DIR, nome_arquivo)
    if not os.path.exists(caminho) or not nome_arquivo.endswith(".json"):
        return None
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
