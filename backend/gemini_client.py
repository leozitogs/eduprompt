"""
Cliente de integração com a API Google Gemini 2.5 Flash.
Utiliza a biblioteca OpenAI com endpoint compatível do Gemini.

Autor: Leonardo Gonçalves Sobral
"""

import time
from openai import OpenAI
from backend.config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_BASE_URL
from backend.cache import buscar_cache, salvar_cache


# ─────────────────────────────────────────────
# Inicialização do cliente
# ─────────────────────────────────────────────

def _criar_cliente() -> OpenAI:
    """
    Cria e retorna uma instância do cliente OpenAI configurada
    para o endpoint compatível do Google Gemini.
    """
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY não configurada. "
            "Defina a variável no arquivo .env"
        )

    return OpenAI(
        api_key=GEMINI_API_KEY,
        base_url=GEMINI_BASE_URL
    )


def chamar_gemini(prompt: str, temperatura: float = 0.7, max_tokens: int = 4096) -> dict:
    """
    Envia um prompt para a API Gemini e retorna a resposta.
    
    Implementa:
    - Sistema de cache para evitar chamadas duplicadas
    - Tratamento robusto de erros com mensagens claras
    - Medição de tempo de resposta
    
    Args:
        prompt: O prompt completo a ser enviado.
        temperatura: Controle de criatividade (0.0 a 1.0).
        max_tokens: Número máximo de tokens na resposta.
    
    Returns:
        dict: {
            "conteudo": str,        # Texto da resposta
            "modelo": str,          # Modelo utilizado
            "tokens_prompt": int,   # Tokens do prompt
            "tokens_resposta": int, # Tokens da resposta
            "tempo_resposta_ms": int, # Tempo em milissegundos
            "cache_hit": bool       # Se veio do cache
        }
    """
    # Verificar cache primeiro
    resposta_cache = buscar_cache(prompt, GEMINI_MODEL)
    if resposta_cache is not None:
        return {
            "conteudo": resposta_cache,
            "modelo": GEMINI_MODEL,
            "tokens_prompt": 0,
            "tokens_resposta": 0,
            "tempo_resposta_ms": 0,
            "cache_hit": True
        }

    # Chamada à API
    cliente = _criar_cliente()
    inicio = time.time()

    try:
        resposta = cliente.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente educacional especializado em criar "
                        "conteúdo pedagógico personalizado de alta qualidade. "
                        "Sempre responda em português brasileiro."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperatura,
            max_tokens=max_tokens
        )

        tempo_ms = int((time.time() - inicio) * 1000)
        conteudo = resposta.choices[0].message.content

        # Salvar no cache
        salvar_cache(prompt, GEMINI_MODEL, conteudo)

        return {
            "conteudo": conteudo,
            "modelo": GEMINI_MODEL,
            "tokens_prompt": getattr(resposta.usage, "prompt_tokens", 0) if resposta.usage else 0,
            "tokens_resposta": getattr(resposta.usage, "completion_tokens", 0) if resposta.usage else 0,
            "tempo_resposta_ms": tempo_ms,
            "cache_hit": False
        }

    except Exception as e:
        tempo_ms = int((time.time() - inicio) * 1000)
        erro_tipo = type(e).__name__
        erro_msg = str(e)

        # Tratamento específico de erros comuns
        if "401" in erro_msg or "Unauthorized" in erro_msg:
            raise ConnectionError(
                "Falha de autenticação com a API Gemini. "
                "Verifique se a GEMINI_API_KEY está correta no arquivo .env"
            ) from e
        elif "429" in erro_msg or "rate" in erro_msg.lower():
            raise ConnectionError(
                "Limite de requisições da API Gemini atingido. "
                "Aguarde alguns segundos e tente novamente."
            ) from e
        elif "timeout" in erro_msg.lower():
            raise ConnectionError(
                f"Timeout na comunicação com a API Gemini ({tempo_ms}ms). "
                "Verifique sua conexão com a internet."
            ) from e
        else:
            raise ConnectionError(
                f"Erro ao comunicar com a API Gemini ({erro_tipo}): {erro_msg}"
            ) from e
