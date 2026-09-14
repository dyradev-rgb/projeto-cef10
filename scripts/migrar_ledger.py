# =====================================================================
# scripts/migrar_ledger.py - MIGRACAO DA LEDGER (uma unica vez)
# CORRECAO APLICADA - aplica na base de dados as correcoes:
#   1) Remove CPFs -> identifica gestor por "(ID: <usuario>)"
#   2) Normaliza foto_path: "\" -> "/" (portabilidade Linux/Windows)
#   3) Recalcula hashes com o HASH CANONICO (ISO-8601 com "T")
#   4) Re-encadeia previous_hash e re-assina com as chaves atuais
#
# PRE-REQUISITO: rodar antes `python scripts/gerar_credenciais.py`
#               (a ledra e assinada com as chaves do secrets.toml).
# O script e IDEMPOTENTE: rodar de novo sempre re-sincroniza com o secrets.
# O arquivo original e salvo em data/quarentena/ para auditoria.
# =====================================================================
import datetime
import hashlib
import hmac
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.seguranca import carregar_credenciais

LEDGER = os.path.join("data", "ledger_cef10.json")
QUARENTENA = os.path.join("data", "quarentena")

# Mapeamento antigo (CPF) -> novo identificador (ID)
MAP_CPF_PARA_ID = {
    "123.456.789-00": "diretor",
    "987.654.321-11": "secretaria",
}


def calcular_hash_canonico(item: dict) -> str:
    """Replica o new BlocoFinanceiro.calcular_hash() do motor,
    usando timestamp .isoformat() (canonico)."""
    conteudo = (
        str(item["index"]) +
        item["timestamp"] +  # ja em ISO-8601 canonico no JSON
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


def assinar(bloco_hash: str, chave: str) -> str:
    return hmac.new(chave.encode("utf-8"), bloco_hash.encode("utf-8"), hashlib.sha256).hexdigest()


def obter_chave_do_autor(item: dict, usuarios: dict, chave_genesis: str) -> str:
    """Descobre a chave HMAC conforme o autor do bloco."""
    if item["index"] == 0:
        return chave_genesis
    for usuario_id, dados in usuarios.items():
        if f"(ID: {usuario_id})" in item.get("autor", ""):
            chave = dados.get("chave", "")
            if not chave:
                raise RuntimeError(f"Usuario '{usuario_id}' sem chave configurada.")
            return chave
    raise RuntimeError(f"Bloco #{item['index']}: autor sem ID conhecido -> {item.get('autor')}")


def main():
    credenciais = carregar_credenciais()
    usuarios = credenciais["users"]
    chave_genesis = credenciais["geral"].get("chave_genesis", "")

    if not os.path.exists(LEDGER):
        print("Ledger nao encontrada; nada a migrar.")
        return

    with open(LEDGER, "r", encoding="utf-8") as f:
        registros = json.load(f)

    # Backup de auditoria (imutavel)
    os.makedirs(QUARENTENA, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = os.path.join(QUARENTENA, f"backup_pre_migracao_{ts}.json")
    shutil.copy(LEDGER, backup)
    print(f"[1/4] Backup de auditoria -> {backup}")

    # [1/4] Normaliza autor (CPF -> ID) e foto_path (\\ -> /)
    anterior_hash = "0"
    for item in registros:
        autor = item.get("autor", "")
        for cpf, novo_id in MAP_CPF_PARA_ID.items():
            autor = autor.replace(f"(CPF: {cpf})", f"(ID: {novo_id})")
        item["autor"] = autor
        item["foto_path"] = (
            item["foto_path"].replace("\\", "/") if item["foto_path"] != "N/A" else "N/A"
        )
        item["previous_hash"] = anterior_hash
        novo_hash = calcular_hash_canonico(item)
        item["hash"] = novo_hash
        # [4/4] Re-assina com a chave atual do gestor
        chave = obter_chave_do_autor(item, usuarios, chave_genesis)
        item["assinatura_digital"] = assinar(novo_hash, chave)
        anterior_hash = novo_hash

    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=4)

    print(f"[2/4] {len(registros)} blocos migrados (hash canonico + re-assinado).")
    print("[3/4] CPFs substituidos por IDs; foto_path normalizado.")
    print("[4/4] Pronto. Valide com: python tests/validar_ledger.py")


if __name__ == "__main__":
    main()