# =====================================================================
# VERIFICADOR INDEPENDENTE DA LEDGER
# Valida 100% fora do app:
#   - hash canonico de cada bloco
#   - encadeamento (previous_hash)
#   - assinatura HMAC contra as chaves do secrets atual
# =====================================================================
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import hashlib
import hmac
import uuid  # noqa: F401  (mantido apenas para padronizar future checks)

from config.seguranca import carregar_credenciais

LEDGER = os.path.join("data", "ledger_cef10.json")


def calcular_hash_canonico(item: dict) -> str:
    conteudo = (
        str(item["index"]) +
        item["timestamp"] +
        str(item.get("projeto_id", "")) +
        str(item.get("tipo_registro", "")) +
        str(item["descricao"]) +
        str(item["valor"]) +
        str(item["status"]) +
        str(item["justificativa"]) +
        str(item["foto_path"]) +
        str(item.get("origem_recurso", "")) +
        str(item.get("responsavel_indicacao", "")) +
        str(item.get("num_empenho", "")) +
        str(item.get("num_edital", "")) +
        str(item.get("empresa_contratada", "")) +
        str(item.get("cnpj_empresa", "")) +
        str(item.get("autor", "")) +
        str(item.get("previous_hash", ""))
    )
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()


def main():
    credenciais = carregar_credenciais()
    usuarios = credenciais["users"]
    chave_genesis = credenciais["geral"].get("chave_genesis", "")

    with open(LEDGER, "r", encoding="utf-8") as f:
        dados = json.load(f)

    falhas = 0
    for i, item in enumerate(dados):
        # 1) Hash canonico
        hash_ok = item["hash"] == calcular_hash_canonico(item)
        if not hash_ok:
            print(f"[ERRO] bloco {i}: hash divergente")
            falhas += 1

        # 2) Encadeamento
        if i > 0 and item["previous_hash"] != dados[i - 1]["hash"]:
            print(f"[ERRO] bloco {i}: previous_hash quebrado")
            falhas += 1

        # 3) Comissario HMAC
        if item["index"] == 0:
            chave = chave_genesis
        else:
            id_autor = next(
                (uid for uid in usuarios if f"(ID: {uid})" in item.get("autor", "")), None
            )
            if not id_autor:
                print(f"[ERRO] bloco {i}: autor sem ID -> {item.get('autor')}")
                falhas += 1
                continue
            chave = usuarios[id_autor]["chave"]
        assinatura_esperada = hmac.new(
            chave.encode("utf-8"), item["hash"].encode("utf-8"), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(assinatura_esperada, item["assinatura_digital"]):
            print(f"[ERRO] bloco {i}: assinatura HMAC invalida")
            falhas += 1

    if falhas:
        print(f"\nRESULTADO: {falhas} falha(s) encontrada(s).")
        sys.exit(1)
    print(f"\nLEDGER INTEGRA: {len(dados)} blocos validados com sucesso.")


if __name__ == "__main__":
    main()