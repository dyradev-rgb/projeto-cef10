# =====================================================================
# scripts/gerar_credenciais.py - GERADOR DE CREDENCIAIS LOCAIS
# SUGESTAO APLICADA:
#   Cria .streamlit/secrets.toml (NAO versionado) com:
#     - senhas hasheadas via PBKDF2-SHA256
#     - chaves HMAC aleatorias por gestor (256 bits)
# Uso:  python scripts/gerar_credenciais.py
# ATENCAO: o arquivo gerado fica fora do git (ver .gitignore).
# Nao regenere no meio de uma base migrada sem rodar scripts/migrar_ledger.py.
# =====================================================================
import os
import sys

# garante que o pacote config seja importavel a partir da raiz do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.seguranca import gerar_chave_aleatoria, gerar_hash_senha

ALVO = os.path.join(".streamlit", "secrets.toml")

# Senhas padrao apenas para demonstracao local / atividade academica.
# Troque antes de qualquer uso real.
USUARIOS_DEMO = {
    "admin": {
        "nome": "Administrador do Sistema (Root)",
        "senha": "admin",
        "role": "admin",
    },
    "diretor": {
        "nome": "Carlos Alberto (Diretor)",
        "senha": "123",
        "role": "gestor",
    },
    "secretaria": {
        "nome": "Mariana Souza (Chefe de Secretaria)",
        "senha": "123",
        "role": "gestor",
    },
}


def main():
    linhas = [
        "# ==================== NAO VERSIONAR ESTE ARQUIVO ====================",
        "# Credenciais locais de demonstracao geradas em:",
        "#   python scripts/gerar_credenciais.py",
        "# Se precisar trocar senhas/chaves, gere novamente e RODE TAMBEM:",
        "#   python scripts/migrar_ledger.py   (re-assina a ledger)",
        "",
        "[geral]",
        f'chave_genesis = "{gerar_chave_aleatoria()}"',
        "",
    ]

    for id_usuario, dados in USUARIOS_DEMO.items():
        linhas.append(f"[users.{id_usuario}]")
        linhas.append(f'nome = "{dados["nome"]}"')
        linhas.append(f'hash_senha = "{gerar_hash_senha(dados["senha"])}"')
        linhas.append(f'role = "{dados["role"]}"')
        linhas.append(f'chave = "{gerar_chave_aleatoria()}"')
        linhas.append("")

    os.makedirs(os.path.dirname(ALVO), exist_ok=True)
    with open(ALVO, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")

    print(f"OK -> {ALVO}")
    print("Usuarios de demonstracao: admin/admin | diretor/123 | secretaria/123")
    print("Lembre-se de executar: python scripts/migrar_ledger.py (re-assina a ledger).")


if __name__ == "__main__":
    main()