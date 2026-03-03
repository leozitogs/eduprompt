"""
Sistema de cache para evitar chamadas desnecessárias à API.
Utiliza armazenamento em arquivo JSON com TTL configurável.

Autor: Leonardo Gonçalves Sobral
"""

import os
import json
import hashlib
import time
from backend.config import CACHE_DIR, CACHE_ENABLED, CACHE_TTL_SECONDS


def _gerar_chave_cache(prompt: str, modelo: str) -> str:
    """
    Gera uma chave de cache única baseada no conteúdo do prompt e modelo.
    Utiliza SHA-256 para criar um hash determinístico.
    """
    conteudo = f"{modelo}:{prompt}"
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()


def _caminho_cache(chave: str) -> str:
    """Retorna o caminho completo do arquivo de cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{chave}.json")


def buscar_cache(prompt: str, modelo: str) -> str | None:
    """
    Busca uma resposta em cache para o prompt e modelo fornecidos.
    
    Retorna:
        str: Resposta em cache se encontrada e válida (dentro do TTL).
        None: Se não houver cache ou se estiver expirado.
    """
    if not CACHE_ENABLED:
        return None

    chave = _gerar_chave_cache(prompt, modelo)
    caminho = _caminho_cache(chave)

    if not os.path.exists(caminho):
        return None

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)

        # Verificar TTL
        timestamp_cache = dados.get("timestamp", 0)
        if time.time() - timestamp_cache > CACHE_TTL_SECONDS:
            os.remove(caminho)  # Remove cache expirado
            return None

        return dados.get("resposta")
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def salvar_cache(prompt: str, modelo: str, resposta: str) -> None:
    """
    Salva uma resposta no cache.
    
    Args:
        prompt: O prompt enviado à API.
        modelo: O modelo utilizado.
        resposta: A resposta recebida da API.
    """
    if not CACHE_ENABLED:
        return

    chave = _gerar_chave_cache(prompt, modelo)
    caminho = _caminho_cache(chave)

    dados = {
        "timestamp": time.time(),
        "modelo": modelo,
        "prompt_hash": chave,
        "resposta": resposta
    }

    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[Cache] Erro ao salvar cache: {e}")


def limpar_cache() -> int:
    """
    Remove todos os arquivos de cache.
    
    Retorna:
        int: Número de arquivos removidos.
    """
    removidos = 0
    if os.path.exists(CACHE_DIR):
        for arquivo in os.listdir(CACHE_DIR):
            if arquivo.endswith(".json"):
                try:
                    os.remove(os.path.join(CACHE_DIR, arquivo))
                    removidos += 1
                except OSError:
                    pass
    return removidos


def estatisticas_cache() -> dict:
    """
    Retorna estatísticas do cache atual.
    
    Retorna:
        dict: Informações sobre o estado do cache.
    """
    total = 0
    validos = 0
    expirados = 0
    tamanho_total = 0

    if os.path.exists(CACHE_DIR):
        for arquivo in os.listdir(CACHE_DIR):
            if arquivo.endswith(".json"):
                total += 1
                caminho = os.path.join(CACHE_DIR, arquivo)
                tamanho_total += os.path.getsize(caminho)
                try:
                    with open(caminho, "r", encoding="utf-8") as f:
                        dados = json.load(f)
                    if time.time() - dados.get("timestamp", 0) <= CACHE_TTL_SECONDS:
                        validos += 1
                    else:
                        expirados += 1
                except (json.JSONDecodeError, OSError):
                    expirados += 1

    return {
        "habilitado": CACHE_ENABLED,
        "total_entradas": total,
        "entradas_validas": validos,
        "entradas_expiradas": expirados,
        "tamanho_total_kb": round(tamanho_total / 1024, 2),
        "ttl_segundos": CACHE_TTL_SECONDS
    }
