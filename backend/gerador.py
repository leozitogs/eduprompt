"""
Módulo de geração de conteúdo educacional.
Orquestra o motor de prompts, a chamada à API e a persistência dos resultados.

Autor: Leonardo Gonçalves Sobral
"""

import json
import os
from datetime import datetime
from backend.config import HISTORICO_PATH, SAMPLES_DIR, MAX_HISTORICO_ENTRIES
from backend.prompt_engine import (
    gerar_prompt,
    TIPOS_CONTEUDO,
    NOMES_TIPOS
)
from backend.gemini_client import chamar_gemini
from backend.perfis import obter_perfil_por_id


def gerar_conteudo(
    perfil_id: int,
    topico: str,
    tipo_conteudo: str,
    versao_prompt: str = "v1"
) -> dict:
    """
    Gera conteúdo educacional personalizado para um aluno.
    
    Fluxo:
    1. Carrega o perfil do aluno
    2. Gera o prompt otimizado via motor de engenharia de prompt
    3. Envia para a API Gemini
    4. Estrutura e persiste o resultado
    
    Args:
        perfil_id: ID do perfil do aluno.
        topico: Tópico a ser ensinado.
        tipo_conteudo: Tipo de conteúdo a gerar.
        versao_prompt: Versão do prompt (v1 ou v2).
    
    Returns:
        dict: Resultado estruturado com metadados e conteúdo.
    """
    # 1. Carregar perfil
    perfil = obter_perfil_por_id(perfil_id)
    if not perfil:
        raise ValueError(f"Perfil com ID {perfil_id} não encontrado.")

    # 2. Validar tipo de conteúdo
    if tipo_conteudo not in TIPOS_CONTEUDO:
        raise ValueError(
            f"Tipo de conteúdo inválido: '{tipo_conteudo}'. "
            f"Válidos: {TIPOS_CONTEUDO}"
        )

    # 3. Gerar prompt otimizado
    prompt = gerar_prompt(tipo_conteudo, perfil, topico, versao_prompt)

    # 4. Chamar API Gemini
    resposta_api = chamar_gemini(prompt)

    # 5. Estruturar resultado
    resultado = {
        "timestamp": datetime.now().isoformat(),
        "perfil": {
            "id": perfil["id"],
            "nome": perfil["nome"],
            "idade": perfil["idade"],
            "nivel": perfil["nivel"],
            "estilo_aprendizado": perfil["estilo_aprendizado"]
        },
        "topico": topico,
        "tipo_conteudo": tipo_conteudo,
        "tipo_conteudo_nome": NOMES_TIPOS.get(tipo_conteudo, tipo_conteudo),
        "versao_prompt": versao_prompt,
        "conteudo_gerado": resposta_api["conteudo"],
        "metadados": {
            "modelo": resposta_api["modelo"],
            "tokens_prompt": resposta_api["tokens_prompt"],
            "tokens_resposta": resposta_api["tokens_resposta"],
            "tempo_resposta_ms": resposta_api["tempo_resposta_ms"],
            "cache_hit": resposta_api["cache_hit"]
        },
        "prompt_utilizado": prompt
    }

    # 6. Persistir no histórico (JSON)
    _salvar_no_historico(resultado)

    # 7. Persistir no banco de dados
    try:
        from backend.database import salvar_geracao_db
        salvar_geracao_db(resultado)
    except Exception:
        pass

    return resultado


def gerar_todos_conteudos(
    perfil_id: int,
    topico: str,
    versao_prompt: str = "v1"
) -> list[dict]:
    """
    Gera todos os 4 tipos de conteúdo para um aluno e tópico.
    
    Args:
        perfil_id: ID do perfil do aluno.
        topico: Tópico a ser ensinado.
        versao_prompt: Versão do prompt (v1 ou v2).
    
    Returns:
        list[dict]: Lista com os 4 resultados gerados.
    """
    resultados = []
    for tipo in TIPOS_CONTEUDO:
        resultado = gerar_conteudo(perfil_id, topico, tipo, versao_prompt)
        resultados.append(resultado)
    return resultados


def comparar_versoes_prompt(
    perfil_id: int,
    topico: str,
    tipo_conteudo: str
) -> dict:
    """
    Gera o mesmo conteúdo com duas versões de prompt para comparação.
    
    Args:
        perfil_id: ID do perfil do aluno.
        topico: Tópico a ser ensinado.
        tipo_conteudo: Tipo de conteúdo a gerar.
    
    Returns:
        dict: Comparação entre as duas versões.
    """
    resultado_v1 = gerar_conteudo(perfil_id, topico, tipo_conteudo, "v1")
    resultado_v2 = gerar_conteudo(perfil_id, topico, tipo_conteudo, "v2")

    comparacao = {
        "timestamp": datetime.now().isoformat(),
        "perfil_id": perfil_id,
        "topico": topico,
        "tipo_conteudo": tipo_conteudo,
        "versao_v1": {
            "conteudo": resultado_v1["conteudo_gerado"],
            "tokens_prompt": resultado_v1["metadados"]["tokens_prompt"],
            "tokens_resposta": resultado_v1["metadados"]["tokens_resposta"],
            "tempo_ms": resultado_v1["metadados"]["tempo_resposta_ms"],
            "prompt": resultado_v1["prompt_utilizado"]
        },
        "versao_v2": {
            "conteudo": resultado_v2["conteudo_gerado"],
            "tokens_prompt": resultado_v2["metadados"]["tokens_prompt"],
            "tokens_resposta": resultado_v2["metadados"]["tokens_resposta"],
            "tempo_ms": resultado_v2["metadados"]["tempo_resposta_ms"],
            "prompt": resultado_v2["prompt_utilizado"]
        }
    }

    return comparacao


# ─────────────────────────────────────────────
# Persistência e histórico
# ─────────────────────────────────────────────

def _salvar_no_historico(resultado: dict) -> None:
    """Salva um resultado no arquivo de histórico JSON com limite de entradas."""
    try:
        historico = carregar_historico()
        historico.append(resultado)

        # Limitar tamanho do histórico para evitar crescimento indefinido
        if len(historico) > MAX_HISTORICO_ENTRIES:
            historico = historico[-MAX_HISTORICO_ENTRIES:]

        os.makedirs(os.path.dirname(HISTORICO_PATH), exist_ok=True)
        with open(HISTORICO_PATH, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[Histórico] Erro ao salvar histórico: {e}")


def carregar_historico() -> list[dict]:
    """Carrega o histórico de gerações do arquivo JSON."""
    if not os.path.exists(HISTORICO_PATH):
        return []
    try:
        with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def obter_historico_filtrado(
    perfil_id: int | None = None,
    topico: str | None = None,
    tipo_conteudo: str | None = None
) -> list[dict]:
    try:
        from backend.database import listar_geracoes_db, db_disponivel
        if db_disponivel():
            return listar_geracoes_db(perfil_id, topico, tipo_conteudo)
    except Exception:
        pass

    historico = carregar_historico()

    if perfil_id is not None:
        historico = [h for h in historico if h["perfil"]["id"] == perfil_id]

    if topico is not None:
        historico = [
            h for h in historico
            if topico.lower() in h["topico"].lower()
        ]

    if tipo_conteudo is not None:
        historico = [h for h in historico if h["tipo_conteudo"] == tipo_conteudo]

    return historico


def salvar_como_sample(resultado: dict, nome_arquivo: str | None = None) -> str:
    """
    Salva um resultado como arquivo de exemplo na pasta /samples.
    
    Returns:
        str: Caminho do arquivo salvo.
    """
    os.makedirs(SAMPLES_DIR, exist_ok=True)

    if nome_arquivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        perfil_nome = resultado["perfil"]["nome"].replace(" ", "_").lower()
        tipo = resultado["tipo_conteudo"]
        nome_arquivo = f"sample_{perfil_nome}_{tipo}_{timestamp}.json"

    caminho = os.path.join(SAMPLES_DIR, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return caminho
