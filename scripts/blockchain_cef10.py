# ==========================================
# MOTOR DE LEDGER E HASHING - CEF 10 (COM PERSISTÊNCIA JSON e ÁRVORE DE EVOLUÇÃO DE OBRA/SERVIÇO)
# Autor: Dyego Alquimim
# Objetivo: Garantir imutabilidade, status de obras, 
# evidências visuais e persistência de dados em arquivo.
# ==========================================
import pandas as pd
import hashlib
import hmac
import datetime
import json
import os
import re
import shutil


class BlocoFinanceiro:
    def __init__(self, index, timestamp, projeto_id, tipo_registro, descricao, valor, status, 
                 justificativa, foto_path, origem_recurso, responsavel_indicacao, 
                 num_empenho, num_edital, empresa_contratada, cnpj_empresa, autor, 
                 previous_hash, hash_atual=None, assinatura_digital=None):
        self.index = index
        if isinstance(timestamp, str):
            self.timestamp = datetime.datetime.fromisoformat(timestamp)
        else:
            self.timestamp = timestamp

        self.projeto_id = projeto_id
        self.tipo_registro = tipo_registro
        self.descricao = descricao
        self.valor = valor
        self.status = status
        self.justificativa = justificativa
        self.foto_path = self.normalizar_caminho(foto_path)
        self.origem_recurso = origem_recurso
        self.responsavel_indicacao = responsavel_indicacao

        # Campos Oficiais de Auditoria do Governo
        self.num_empenho = num_empenho
        self.num_edital = num_edital
        self.empresa_contratada = empresa_contratada
        self.cnpj_empresa = cnpj_empresa

        self.autor = autor
        self.previous_hash = previous_hash
        self.hash = hash_atual if hash_atual else self.calcular_hash()

        # Camada de Assinatura Digital HMAC
        self.assinatura_digital = assinatura_digital if assinatura_digital else "N/A"

    @staticmethod
    def normalizar_caminho(caminho):
        """[AUDITORIA-03] Garante separador posix nos caminhos gravados."""
        if caminho in ("N/A", None, ""):
            return "N/A"
        return caminho.replace("\\", "/")

    def calcular_hash(self):
    
        conteudo = (
            str(self.index) +
            self.timestamp.isoformat() +
            str(self.projeto_id) +
            str(self.tipo_registro) +
            str(self.descricao) +
            str(self.valor) +
            str(self.status) +
            str(self.justificativa) +
            str(self.foto_path) +
            str(self.origem_recurso) +
            str(self.responsavel_indicacao) +
            str(self.num_empenho) +
            str(self.num_edital) +
            str(self.empresa_contratada) +
            str(self.cnpj_empresa) +
            str(self.autor) +
            str(self.previous_hash)
        )
        return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()

    def assinar_bloco(self, chave_privada_gestor):
        """Gera uma assinatura digital HMAC-SHA256 usando a chave secreta do gestor."""
        self.assinatura_digital = hmac.new(
            chave_privada_gestor.encode('utf-8'),
            self.hash.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def verificar_assinatura(self, chave_privada_gestor):
        """Valida se a assinatura gravada bate com a chave secreta do autor."""
        if self.assinatura_digital == "N/A":
            return True  # Bloco genesis

        assinatura_esperada = hmac.new(
            chave_privada_gestor.encode('utf-8'),
            self.hash.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(self.assinatura_digital, assinatura_esperada)

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "projeto_id": self.projeto_id,
            "tipo_registro": self.tipo_registro,
            "descricao": self.descricao,
            "valor": self.valor,
            "status": self.status,
            "justificativa": self.justificativa,
            "foto_path": self.normalizar_caminho(self.foto_path),
            "origem_recurso": self.origem_recurso,
            "responsavel_indicacao": self.responsavel_indicacao,
            "num_empenho": self.num_empenho,
            "num_edital": self.num_edital,
            "empresa_contratada": self.empresa_contratada,
            "cnpj_empresa": self.cnpj_empresa,
            "autor": self.autor,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "assinatura_digital": self.assinatura_digital
        }


class BlockchainCEF10:
    def __init__(self, filepath="data/ledger_cef10.json", credenciais=None, chave_genesis=None):
        self.filepath = filepath
        self.quarentena_dir = "data/quarentena"
        self.credenciais = credenciais if credenciais is not None else {}
        self.chave_genesis = chave_genesis
        self.ensure_data_dir()
        self.chain = self.carregar_chain()

    def ensure_data_dir(self):
        dir_name = os.path.dirname(self.filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        if not os.path.exists(self.quarentena_dir):
            os.makedirs(self.quarentena_dir, exist_ok=True)

    def criar_bloco_genesis(self, chave_genesis=None):
        if not chave_genesis:
            raise RuntimeError(
                "Chave do bloco genesis nao configurada. "
                "Gere credenciais: python scripts/gerar_credenciais.py"
            )
        bloco = BlocoFinanceiro(
            index=0,
            timestamp=datetime.datetime.now(),
            projeto_id="genesis-cef10",
            tipo_registro="Criacao",
            descricao="Inicialização do Sistema - Marco Zero CEF 10",
            valor=0.0,
            status="Iniciado",
            justificativa="Sistema implantado para governança, transparência e controle social.",
            foto_path="N/A",
            origem_recurso="N/A",
            responsavel_indicacao="N/A",
            num_empenho="N/A",
            num_edital="N/A",
            empresa_contratada="N/A",
            cnpj_empresa="N/A",
            autor="Sistema / Governança Central",
            previous_hash="0"
        )
        bloco.assinar_bloco(chave_genesis)
        return bloco

    def gerar_projeto_id(self, descricao):
        return re.sub(r'[^a-z0-9]', '_', descricao.lower().strip())

    def _gerar_base_inicial(self, credenciais=None, chave_genesis=None):
        credenciais = credenciais if credenciais is not None else self.credenciais
        chave_genesis = chave_genesis or self.chave_genesis
        if not chave_genesis:
            raise RuntimeError(
                "Chave do bloco genesis nao configurada. "
                "Gere credenciais: python scripts/gerar_credenciais.py"
            )

        diretor = credenciais.get("diretor", {})
        secretaria = credenciais.get("secretaria", {})
        if not diretor.get("chave") or not secretaria.get("chave"):
            raise RuntimeError(
                "Usuarios 'diretor' e 'secretaria' devem existir nas credenciais "
                "para gerar a base de demonstracao."
            )

        self.chain = [self.criar_bloco_genesis(chave_genesis)]

        self._adicionar_bloco_interno(
            "Manutenção Preventiva de Informática", 15000.00,
            "2. Em Licitação", "Aguardando homologação do pregão eletrônico.",
            "N/A",
            "Tesouro / Recursos Próprios da SEEDF", "Diretoria de Ensino",
            "2026NE00412", "Pregão Eletrônico nº 08/2026", "Em Definição", "N/A",
            "Carlos Alberto (Diretor) (ID: diretor)", "Criacao",
            chave_privada=diretor["chave"]
        )
        self._adicionar_bloco_interno(
            "Reforma da Cantina Escolar", 28500.50,
            "3. Em Execução", "Obras iniciadas conforme cronograma físico-financeiro.",
            "N/A",
            "Emenda Parlamentar Distrital (CLDF)", "Deputado Distrital Exemplo",
            "2026NE00189", "Dispensa de Licitação nº 02/2026", "Alfa Construções e Reformas EIRELI", "12.345.678/0001-90",
            "Mariana Souza (Chefe de Secretaria) (ID: secretaria)", "Criacao",
            chave_privada=secretaria["chave"]
        )
        self.salvar_chain()
        return self.chain

    def carregar_chain(self):
        """Lê o JSON do disco. Se não existir, gera a base autêntica limpa."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)
                    chain = []
                    for item in dados_json:
                        bloco = BlocoFinanceiro(
                            index=item["index"],
                            timestamp=item["timestamp"],
                            projeto_id=item.get("projeto_id", "projeto"),
                            tipo_registro=item.get("tipo_registro", "Criacao"),
                            descricao=item["descricao"],
                            valor=item["valor"],
                            status=item["status"],
                            justificativa=item["justificativa"],
                            foto_path=item["foto_path"],
                            origem_recurso=item.get("origem_recurso", "SEEDF"),
                            responsavel_indicacao=item.get("responsavel_indicacao", "SEEDF"),
                            num_empenho=item.get("num_empenho", "N/A"),
                            num_edital=item.get("num_edital", "N/A"),
                            empresa_contratada=item.get("empresa_contratada", "N/A"),
                            cnpj_empresa=item.get("cnpj_empresa", "N/A"),
                            autor=item.get("autor", "Sistema"),
                            previous_hash=item["previous_hash"],
                            hash_atual=item["hash"],
                            assinatura_digital=item.get("assinatura_digital", "N/A")
                        )
                        chain.append(bloco)
                    return chain
            except Exception as e:
                print(f"Erro ao carregar o ledger: {e}.")

        return self._gerar_base_inicial()

    def salvar_chain(self):
        dados_json = [bloco.to_dict() for bloco in self.chain]
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(dados_json, f, ensure_ascii=False, indent=4)

    def _adicionar_bloco_interno(self, descricao, valor, status, justificativa, foto_path, origem, responsavel, empenho, edital, empresa, cnpj, autor, tipo_registro, chave_privada, projeto_id=None):
        bloco_anterior = self.chain[-1]
        p_id = projeto_id if projeto_id else self.gerar_projeto_id(descricao)

        novo_bloco = BlocoFinanceiro(
            index=bloco_anterior.index + 1,
            timestamp=datetime.datetime.now(),
            projeto_id=p_id,
            tipo_registro=tipo_registro,
            descricao=descricao,
            valor=valor,
            status=status,
            justificativa=justificativa,
            foto_path=foto_path,
            origem_recurso=origem,
            responsavel_indicacao=responsavel,
            num_empenho=empenho,
            num_edital=edital,
            empresa_contratada=empresa,
            cnpj_empresa=cnpj,
            autor=autor,
            previous_hash=bloco_anterior.hash
        )
        novo_bloco.assinar_bloco(chave_privada)
        self.chain.append(novo_bloco)

    def adicionar_bloco(self, descricao, valor, status, justificativa, foto_path, origem, responsavel, empenho, edital, empresa, cnpj, autor, tipo_registro, chave_privada, projeto_id=None):
        self._adicionar_bloco_interno(descricao, valor, status, justificativa, foto_path, origem, responsavel, empenho, edital, empresa, cnpj, autor, tipo_registro, chave_privada, projeto_id)
        self.salvar_chain()

    def validar_cadeia(self, tabela_chaves_publicas):
        """Audita a integridade de hashes, encadeamento e assinaturas HMAC.
        [AUDITORIA-02] O autor do bloco agora carrega '(ID: <usuario>)' em vez
        de CPF; a chave correspondente e buscada na tabela por esse ID."""
        for i in range(1, len(self.chain)):
            bloco_atual = self.chain[i]
            bloco_anterior = self.chain[i - 1]

            # 1. Integridade do Hash SHA-256 (canonico)
            if bloco_atual.hash != bloco_atual.calcular_hash():
                return False, f"FRAUDE DETECTADA no Bloco #{bloco_atual.index} ('{bloco_atual.descricao}'): Conteúdo adulterado ilicitamente no banco/JSON!", i

            # 2. Encadeamento da Cadeia
            if bloco_atual.previous_hash != bloco_anterior.hash:
                return False, f"QUEBRA DE CADEIA entre o Bloco #{bloco_anterior.index} e o Bloco #{bloco_atual.index}!", i

            # 3. Assinatura Digital HMAC
            id_autor = None
            for usuario_id in tabela_chaves_publicas:
                if f"(ID: {usuario_id})" in bloco_atual.autor:
                    id_autor = usuario_id
                    break

            if id_autor and id_autor in tabela_chaves_publicas:
                chave_privada_cadastrada = tabela_chaves_publicas[id_autor]["chave"]
                if not bloco_atual.verificar_assinatura(chave_privada_cadastrada):
                    return False, f"ASSINATURA INVÁLIDA no Bloco #{bloco_atual.index}: Chave HMAC não confere com o autor ({bloco_atual.autor})!", i

        return True, "Cadeia 100% Íntegra e Auditada Criptograficamente.", None

    def realizar_quarentena_forense(self):
        """Salva uma cópia de segurança do arquivo corrompido para auditoria."""
        if os.path.exists(self.filepath):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = os.path.join(self.quarentena_dir, f"quarentena_fraude_{ts}.json")
            shutil.copy(self.filepath, dest)
            return dest
        return None

    def recuperar_ultimo_estado_valido(self, tabela_chaves_publicas):
        """
        ROLLBACK INTELIGENTE (Last Known Good State):
        Move o arquivo corrompido para a quarentena e recupera todos os blocos válidos até o ponto da fraude, sem apagar o histórico legítimo.
        """
        # 1. Copia o arquivo para a quarentena forense
        arquivo_quarentena = self.realizar_quarentena_forense()

        # 2. Identifica onde está o bloco adulterado
        integra, msg, idx_corrompido = self.validar_cadeia(tabela_chaves_publicas)

        if not integra and idx_corrompido is not None:
            # Mantém intactos todos os blocos anteriores ao primeiro bloco corrompido
            self.chain = self.chain[:idx_corrompido]
            self.salvar_chain()
            return True, f"Rollback efetuado com sucesso! Mantidos intactos {len(self.chain)} blocos autênticos. O bloco #{idx_corrompido} e os posteriores foram isolados na quarentena: `{arquivo_quarentena}`."

        return False, "Nenhum erro de integridade detectado para fazer rollback."

    def obter_projetos_existentes(self):
        projetos = {}
        for bloco in self.chain:
            if bloco.projeto_id != "genesis-cef10":
                projetos[bloco.projeto_id] = bloco.descricao
        return projetos

    # reset usa as credenciais/secrets vigentes.
    def resetar_base_demonstracao(self):
        """Restaura o arquivo JSON estritamente para os dados iniciais de demonstração."""
        self.realizar_quarentena_forense()
        self._gerar_base_inicial(self.credenciais, self.chave_genesis)

    def obter_dataframe_historico(self):
        """Converte a cadeia de blocos em um DataFrame Pandas formatado para análises e IA."""
        dados = []
        for bloco in self.chain:
            if bloco.projeto_id == "genesis-cef10":
                continue
            dados.append({
                "Index": bloco.index,
                "Data": bloco.timestamp,
                "Projeto": bloco.descricao,
                "Valor": bloco.valor,
                "Status": bloco.status,
                "Origem": bloco.origem_recurso,
                "Gestor": bloco.autor
            })
        df = pd.DataFrame(dados)
        if not df.empty:
            df["Data"] = pd.to_datetime(df["Data"])
            df["Mes_Ano"] = df["Data"].dt.to_period("M").dt.to_timestamp()
        return df