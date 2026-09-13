# =====================================================================
# config/seguranca.py - GERENCIAMENTO CENTRALIZADO DE CREDENCIAIS
# CORRECAO APLICADA:
#   - Removeu senhas e chaves em texto puro do codigo-fonte.
#   - Senhas agora sao hasheadas com PBKDF2-SHA256 (salgado, OWASP).
#   - Chaves HMAC sao aleatorias e residem fora do repositorio.
#   - Comparacao de senha em tempo constante (hmac.compare_digest).
#
# FONTES DE CREDENCIAIS (ordem de precedencia):
#   1) st.secrets (Streamlit - recomendado em deploy)
#   2) Variavel de ambiente CEF10_SECRETS (caminho de um .toml)
#   3) Arquivo local .streamlit/secrets.toml (nao versionado)
# =====================================================================
import hashlib
import hmac
import os
import secrets as _secrets  # gerador criptograficamente seguro

# Parametros de derivacao de senha (recomendacao OWASP)
PBKDF2_ITERACOES = 600_000
ALGORITMO = "sha256"
CAMINHO_SECRETS_PADRAO = os.path.join(".streamlit", "secrets.toml")


def gerar_chave_aleatoria() -> str:
    """Gera uma chave HMAC com 256 bits de entropia (para autoridade gestora)."""
    return _secrets.token_hex(32)


def gerar_hash_senha(senha: str) -> str:
    """Gera hash PBKDF2-SHA256 salgado no formato portavel:
       pbkdf2_sha256$iteracoes$sal_hex$hash_hex"""
    sal = _secrets.token_hex(16)
    hash_hex = hashlib.pbkdf2_hmac(
        ALGORITMO, senha.encode("utf-8"), bytes.fromhex(sal), PBKDF2_ITERACOES
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERACOES}${sal}${hash_hex}"


def verificar_senha(hash_armazenado: str, senha: str) -> bool:
    """Valida a senha contra o hash armazenado.
    Usa hmac.compare_digest para evitar ataques de timing."""
    try:
        _algo, iteracoes, sal_hex, hash_hex = hash_armazenado.split("$")
        candidato = hashlib.pbkdf2_hmac(
            ALGORITMO, senha.encode("utf-8"), bytes.fromhex(sal_hex), int(iteracoes)
        ).hex()
        return hmac.compare_digest(candidato, hash_hex)
    except (ValueError, AttributeError):
        return False


def _ler_toml(caminho: str) -> dict:
    """Le arquivos .toml usando tomllib (stdlib a partir do Python 3.11)."""
    try:
        import tomllib

        with open(caminho, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def _normalizar(users: dict, geral: dict) -> dict:
    """Converte a estrutura do secrets para o formato interno esperado
    pelo motor da ledger: {id: {nome, hash_senha, role, chave}}."""
    resultado = {}
    for id_usuario, dados in users.items():
        resultado[id_usuario] = {
            "nome": dados.get("nome", id_usuario),
            "hash_senha": dados.get("hash_senha", dados.get("senha", "")),
            "role": dados.get("role", "gestor"),
            "chave": dados.get("chave", ""),
        }
    return {"users": resultado, "geral": geral}


def carregar_credenciais() -> dict:
    """Carrega credenciais a partir das fontes em ordem de precedencia.
    Levanta RuntimeError com instrucoes se nada for encontrado."""
    # 1) st.secrets quando executando dentro do Streamlit
    try:
        import streamlit as st

        dados_sb = st.secrets
        if dados_sb.get("users"):
            return _normalizar(dict(dados_sb["users"]), dict(dados_sb.get("geral") or {}))
    except Exception:
        pass  # ambiente sem streamlit/secrets configurada -> tenta arquivo

    # 2) Ambiente customizado via CEF10_SECRETS
    caminho = os.environ.get("CEF10_SECRETS", CAMINHO_SECRETS_PADRAO)
    if os.path.exists(caminho):
        dados = _ler_toml(caminho)
        if dados.get("users"):
            return _normalizar(dados["users"], dados.get("geral", {}))

    # 3) Nenhuma fonte configurada -> instrucoes claras de remediacao
    raise RuntimeError(
        "Credenciais nao configuradas.\n"
        "Gere o arquivo local rodando:  python scripts/gerar_credenciais.py\n"
        "E em producao, use st.secrets ou a variavel de ambiente CEF10_SECRETS."
    )