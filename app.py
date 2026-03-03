"""
EduPrompt — Servidor Flask
Plataforma educativa que gera conteúdo personalizado com IA.

Rotas da API:
  GET  /api/perfis              — Lista todos os perfis de alunos
  GET  /api/perfis/<id>         — Obtém um perfil específico
  POST /api/perfis              — Cria um novo perfil customizado
  DELETE /api/perfis/<id>       — Remove um perfil customizado
  POST /api/gerar               — Gera conteúdo educacional
  POST /api/gerar-todos         — Gera todos os 4 tipos de conteúdo
  POST /api/comparar            — Compara versões v1 e v2 de prompts
  GET  /api/historico           — Consulta histórico de gerações
  GET  /api/cache/stats         — Estatísticas do cache
  POST /api/cache/limpar        — Limpa o cache
  GET  /api/tipos-conteudo      — Lista tipos de conteúdo disponíveis
  GET  /api/samples             — Lista samples pré-gerados
  GET  /api/samples/<arquivo>   — Obtém um sample específico
  GET  /api/status              — Status do sistema (DB, cache, etc.)

Autor: Leonardo Gonçalves Sobral
"""

import json
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from backend.config import (
    FLASK_HOST, FLASK_PORT, FLASK_DEBUG, validar_configuracao, DATABASE_URL,
    MAX_TOPICO_LENGTH, MAX_PERFIS_CUSTOMIZADOS
)
from backend.perfis import (
    carregar_perfis, obter_perfil_por_id, listar_perfis_resumo,
    adicionar_perfil, deletar_perfil, validar_perfil
)
from backend.gerador import (
    gerar_conteudo,
    gerar_todos_conteudos,
    comparar_versoes_prompt,
    carregar_historico,
    obter_historico_filtrado
)
from backend.cache import limpar_cache, estatisticas_cache
from backend.prompt_engine import TIPOS_CONTEUDO, NOMES_TIPOS
from backend.samples import listar_samples, obter_sample

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)
CORS(app)

# Limite de tamanho do body JSON (1 MB)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024


# ─── Tratamento global de erros ───

@app.errorhandler(404)
def not_found(e):
    return jsonify({"sucesso": False, "erro": "Recurso não encontrado"}), 404


@app.errorhandler(413)
def payload_too_large(e):
    return jsonify({"sucesso": False, "erro": "Payload muito grande. Máximo: 1 MB"}), 413


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"sucesso": False, "erro": "Método HTTP não permitido"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"sucesso": False, "erro": "Erro interno do servidor"}), 500


def _sanitizar_texto(texto, max_length=200):
    """Remove espaços extras e limita o comprimento do texto."""
    if not isinstance(texto, str):
        return ""
    return texto.strip()[:max_length]


# ─── Rota principal ───

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


# ─── API — Perfis de Alunos ───

@app.route("/api/perfis", methods=["GET"])
def api_listar_perfis():
    try:
        perfis = listar_perfis_resumo()
        return jsonify({"sucesso": True, "dados": perfis})
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route("/api/perfis/<int:perfil_id>", methods=["GET"])
def api_obter_perfil(perfil_id):
    perfil = obter_perfil_por_id(perfil_id)
    if perfil:
        return jsonify({"sucesso": True, "dados": perfil})
    return jsonify({"sucesso": False, "erro": "Perfil não encontrado"}), 404


@app.route("/api/perfis", methods=["POST"])
def api_criar_perfil():
    dados = request.get_json()
    if not dados:
        return jsonify({"sucesso": False, "erro": "Body JSON é obrigatório"}), 400

    erros = validar_perfil(dados)
    if erros:
        return jsonify({"sucesso": False, "erro": "; ".join(erros)}), 400

    try:
        novo_perfil = adicionar_perfil(dados)
        return jsonify({"sucesso": True, "dados": novo_perfil}), 201
    except ValueError as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 400
    except Exception as e:
        return jsonify({"sucesso": False, "erro": f"Erro interno: {str(e)}"}), 500


@app.route("/api/perfis/<int:perfil_id>", methods=["DELETE"])
def api_deletar_perfil(perfil_id):
    try:
        removido = deletar_perfil(perfil_id)
        if removido:
            return jsonify({"sucesso": True, "mensagem": "Perfil removido"})
        return jsonify({"sucesso": False, "erro": "Perfil não encontrado ou não pode ser removido (apenas perfis customizados)"}), 400
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


# ─── API — Geração de Conteúdo ───

@app.route("/api/gerar", methods=["POST"])
def api_gerar_conteudo():
    dados = request.get_json()
    if not dados:
        return jsonify({"sucesso": False, "erro": "Body JSON é obrigatório"}), 400

    campos_obrigatorios = ["perfil_id", "topico", "tipo_conteudo"]
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({"sucesso": False, "erro": f"Campo obrigatório ausente: {campo}"}), 400

    perfil_id = dados["perfil_id"]
    topico = _sanitizar_texto(dados.get("topico", ""), MAX_TOPICO_LENGTH)
    tipo_conteudo = dados["tipo_conteudo"]
    versao_prompt = dados.get("versao_prompt", "v1")

    if not topico:
        return jsonify({"sucesso": False, "erro": "Tópico não pode ser vazio"}), 400
    if tipo_conteudo not in TIPOS_CONTEUDO:
        return jsonify({"sucesso": False, "erro": f"Tipo de conteúdo inválido. Válidos: {TIPOS_CONTEUDO}"}), 400
    if versao_prompt not in ("v1", "v2"):
        return jsonify({"sucesso": False, "erro": "Versão de prompt inválida. Use 'v1' ou 'v2'"}), 400

    try:
        resultado = gerar_conteudo(perfil_id, topico, tipo_conteudo, versao_prompt)
        return jsonify({"sucesso": True, "dados": resultado})
    except ValueError as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 400
    except ConnectionError as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 503
    except Exception as e:
        return jsonify({"sucesso": False, "erro": f"Erro interno: {str(e)}"}), 500


@app.route("/api/gerar-todos", methods=["POST"])
def api_gerar_todos():
    dados = request.get_json()
    if not dados:
        return jsonify({"sucesso": False, "erro": "Body JSON é obrigatório"}), 400

    perfil_id = dados.get("perfil_id")
    topico = _sanitizar_texto(dados.get("topico", ""), MAX_TOPICO_LENGTH)
    versao_prompt = dados.get("versao_prompt", "v1")

    if not perfil_id or not topico:
        return jsonify({"sucesso": False, "erro": "Campos obrigatórios: perfil_id, topico"}), 400

    if versao_prompt not in ("v1", "v2"):
        return jsonify({"sucesso": False, "erro": "Versão de prompt inválida. Use 'v1' ou 'v2'"}), 400

    try:
        resultados = gerar_todos_conteudos(perfil_id, topico, versao_prompt)
        return jsonify({"sucesso": True, "dados": resultados})
    except ValueError as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 400
    except ConnectionError as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 503
    except Exception as e:
        return jsonify({"sucesso": False, "erro": f"Erro interno: {str(e)}"}), 500


@app.route("/api/comparar", methods=["POST"])
def api_comparar_versoes():
    dados = request.get_json()
    if not dados:
        return jsonify({"sucesso": False, "erro": "Body JSON é obrigatório"}), 400

    perfil_id = dados.get("perfil_id")
    topico = _sanitizar_texto(dados.get("topico", ""), MAX_TOPICO_LENGTH)
    tipo_conteudo = dados.get("tipo_conteudo")

    if not all([perfil_id, topico, tipo_conteudo]):
        return jsonify({"sucesso": False, "erro": "Campos obrigatórios: perfil_id, topico, tipo_conteudo"}), 400

    try:
        comparacao = comparar_versoes_prompt(perfil_id, topico, tipo_conteudo)
        return jsonify({"sucesso": True, "dados": comparacao})
    except ValueError as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 400
    except ConnectionError as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 503
    except Exception as e:
        return jsonify({"sucesso": False, "erro": f"Erro interno: {str(e)}"}), 500


# ─── API — Histórico ───

@app.route("/api/historico", methods=["GET"])
def api_historico():
    perfil_id = request.args.get("perfil_id", type=int)
    topico = request.args.get("topico")
    tipo_conteudo = request.args.get("tipo_conteudo")

    try:
        historico = obter_historico_filtrado(perfil_id, topico, tipo_conteudo)
        return jsonify({"sucesso": True, "dados": historico, "total": len(historico)})
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


# ─── API — Cache ───

@app.route("/api/cache/stats", methods=["GET"])
def api_cache_stats():
    try:
        stats = estatisticas_cache()
        return jsonify({"sucesso": True, "dados": stats})
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route("/api/cache/limpar", methods=["POST"])
def api_cache_limpar():
    try:
        removidos = limpar_cache()
        return jsonify({"sucesso": True, "mensagem": f"{removidos} entradas de cache removidas"})
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


# ─── API — Samples ───

@app.route("/api/samples", methods=["GET"])
def api_listar_samples():
    try:
        samples = listar_samples()
        return jsonify({"sucesso": True, "dados": samples})
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route("/api/samples/<nome_arquivo>", methods=["GET"])
def api_obter_sample(nome_arquivo):
    # Sanitizar nome do arquivo para evitar path traversal
    nome_arquivo = os.path.basename(nome_arquivo)
    if not nome_arquivo.endswith(".json") or ".." in nome_arquivo:
        return jsonify({"sucesso": False, "erro": "Nome de arquivo inválido"}), 400

    sample = obter_sample(nome_arquivo)
    if sample:
        return jsonify({"sucesso": True, "dados": sample})
    return jsonify({"sucesso": False, "erro": "Sample não encontrado"}), 404


# ─── API — Informações do Sistema ───

@app.route("/api/tipos-conteudo", methods=["GET"])
def api_tipos_conteudo():
    tipos = [{"id": tipo, "nome": NOMES_TIPOS[tipo]} for tipo in TIPOS_CONTEUDO]
    return jsonify({"sucesso": True, "dados": tipos})


@app.route("/api/status", methods=["GET"])
def api_status():
    db_ok = False
    try:
        from backend.database import db_disponivel
        db_ok = db_disponivel()
    except Exception:
        pass

    cache_stats = estatisticas_cache()
    return jsonify({
        "sucesso": True,
        "dados": {
            "banco_de_dados": db_ok,
            "cache": cache_stats,
            "api_configurada": bool(os.getenv("GEMINI_API_KEY", ""))
        }
    })


# ─── Inicialização ───

def _inicializar_banco():
    if not DATABASE_URL:
        return
    try:
        from backend.database import criar_tabelas, seed_perfis_iniciais
        criar_tabelas()
        perfis_path = os.path.join(os.path.dirname(__file__), "data", "perfis_alunos.json")
        if os.path.exists(perfis_path):
            with open(perfis_path, "r", encoding="utf-8") as f:
                perfis = json.load(f)
            seed_perfis_iniciais(perfis)
        print("  [DB] PostgreSQL conectado e tabelas criadas.")
    except Exception as e:
        print(f"  [DB] Aviso: Banco de dados não disponível ({e}). Usando JSON como fallback.")


if __name__ == "__main__":
    erros = validar_configuracao()
    if erros:
        print("  Avisos de configuração:")
        for erro in erros:
            print(f"   - {erro}")
        print("   O servidor iniciará, mas chamadas à API podem falhar.\n")

    _inicializar_banco()

    print("=" * 55)
    print("  EduPrompt — Plataforma Educativa com IA")
    print("  Autor: Leonardo Gonçalves Sobral")
    print(f"  Servidor: http://localhost:{FLASK_PORT}")
    print("=" * 55)

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
