# ==========================================
# PAINEL DE TRANSPARÊNCIA - CEF 10 (STREAMLIT, SEGURANÇA COM TIMEOUT E LOGOUT, ÁRVORE DE EVOLUÇÃO DE OBRAS e SELO DE AUDITORIA CRIPTOGRÁFICA)
# Autor: Dyego Alquimim
# Objetivo: Interface cívica descentralizada para 
# monitoramento de recursos, status e evidências.
# ==========================================

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import streamlit as st
import pandas as pd
import sys
import os
import json
from fpdf import FPDF
import io
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.blockchain_cef10 import BlockchainCEF10

st.set_page_config(
    page_title="Transparência CEF 10 - Portal Cidadão",
    page_icon="🛡️",
    layout="wide"
)

IMAGENS_DIR = "data/imagens"
JSON_PATH = "data/ledger_cef10.json"
os.makedirs(IMAGENS_DIR, exist_ok=True)

if 'cofre_escola' not in st.session_state:
    st.session_state.cofre_escola = BlockchainCEF10(filepath=JSON_PATH)

cofre = st.session_state.cofre_escola

# ==========================================
# MATRIZ DE USUÁRIOS, NÍVEIS DE ACESSO E CHAVES
# ==========================================
USUARIOS_SISTEMA = {
    # SUPERUSUÁRIO DE AUDITORIA E APRESENTAÇÃO
    "000.000.000-00": {
        "nome": "Administrador do Sistema (Root)",
        "senha": "admin",
        "role": "admin",
        "chave_privada": "CHAVE_PRIVADA_ADMIN_ROOT_2026"
    },
    # GESTORES ESCOLARES OFICIAIS
    "123.456.789-00": {
        "nome": "Carlos Alberto (Diretor)", 
        "senha": "123",
        "role": "gestor",
        "chave_privada": "CHAVE_PRIVADA_DIRETOR_CARLOS_2026"
    },
    "987.654.321-11": {
        "nome": "Mariana Souza (Chefe de Secretaria)", 
        "senha": "123",
        "role": "gestor",
        "chave_privada": "CHAVE_PRIVADA_SECRETARIA_MARIANA_2026"
    }
}

DICIONARIO_CIDADAO = {
    "1. Empenhado / Alocado": "Dinheiro reservado e garantido pelo governo para este projeto específico.",
    "2. Em Licitação": "O governo está cotando preços e selecionando a empresa qualificada para realizar a obra ou serviço.",
    "3. Em Execução": "A obra ou serviço está fisicamente acontecendo na escola neste exato momento.",
    "4. Entregue / Concluído": "Serviço finalizado, atestado e entregue para uso e benefício da comunidade escolar."
}

# Inicialização de Variáveis de Sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.nome_gestor = ""
    st.session_state.cpf_gestor = ""
    st.session_state.role_gestor = ""
    st.session_state.chave_privada = ""

# ==========================================
# AUDITORIA E VALIDAÇÃO AUTOMÁTICA DA CADEIA
# ==========================================
cadeia_integra, mensagem_auditoria, idx_corrompido = cofre.validar_cadeia(USUARIOS_SISTEMA)

# ==========================================
# BARRA LATERAL: LOGIN E CONTROLE
# ==========================================
st.sidebar.header("🔐 Portal de Acesso Restrito")

if not st.session_state.autenticado:
    cpf_input = st.sidebar.text_input("CPF do Usuário", placeholder="Ex: 000.000.000-00")
    senha_input = st.sidebar.text_input("Senha Pessoal", type="password")
    btn_login = st.sidebar.button("Entrar no Sistema")

    if btn_login:
        if cpf_input in USUARIOS_SISTEMA:
            if senha_input == USUARIOS_SISTEMA[cpf_input]["senha"]:
                st.session_state.autenticado = True
                st.session_state.nome_gestor = USUARIOS_SISTEMA[cpf_input]["nome"]
                st.session_state.cpf_gestor = cpf_input
                st.session_state.role_gestor = USUARIOS_SISTEMA[cpf_input]["role"]
                st.session_state.chave_privada = USUARIOS_SISTEMA[cpf_input]["chave_privada"]
                st.rerun()
            else:
                st.sidebar.error("Senha incorreta.")
        else:
            st.sidebar.error("CPF não cadastrado.")
    st.sidebar.info("💡 **Modo Cidadão:** Consulta pública e transparente ativada.")
else:
    st.sidebar.success(f"Sessão Ativa:\n**{st.session_state.nome_gestor}**")
    st.sidebar.markdown(f"**Perfil:** `{st.session_state.role_gestor.upper()}` | **CPF:** `{st.session_state.cpf_gestor}`")
    
    if st.sidebar.button("🚪 Fazer Logout"):
        st.session_state.autenticado = False
        st.session_state.nome_gestor = ""
        st.session_state.cpf_gestor = ""
        st.session_state.role_gestor = ""
        st.session_state.chave_privada = ""
        st.rerun()

# ==========================================
# CENTRAL DE TESTES E CONTROLE FORENSE (EXCLUSIVA ADMIN/ROOT)
# ==========================================
if st.session_state.autenticado and st.session_state.role_gestor == "admin":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧪 Central de Testes (Ambiente Admin/Demo)")
    with st.sidebar.expander("🛠️ Ferramentas de Segurança e Rollback", expanded=True):
        st.caption("Ferramentas para simulação de ataques e recuperação forense da Ledger.")
        
        if st.button("🚨 Simular Adulteração no JSON", use_container_width=True):
            try:
                if os.path.exists(JSON_PATH):
                    with open(JSON_PATH, "r", encoding="utf-8") as f:
                        dados = json.load(f)
                    if len(dados) > 1:
                        # Altera o último bloco inserido para simular ataque
                        dados[-1]["valor"] += 90000.00  
                        dados[-1]["justificativa"] += " [ADULTERAÇÃO FRAUDULENTA EM BANCO]"
                        with open(JSON_PATH, "w", encoding="utf-8") as f:
                            json.dump(dados, f, indent=4, ensure_ascii=False)
                        st.sidebar.warning("⚠️ O último bloco do JSON foi adulterado ilicitamente!")
                        st.rerun()
            except Exception as e:
                st.sidebar.error(f"Erro ao simular: {e}")

        if st.button("🛡️ Rollback para Último Estado Válido", use_container_width=True):
            sucesso, msg_res = cofre.recuperar_ultimo_estado_valido(USUARIOS_SISTEMA)
            if sucesso:
                st.sidebar.success(msg_res)
            else:
                st.sidebar.info(msg_res)
            st.rerun()

        st.markdown("---")
        if st.button("🔄 Resetar para Dados de Fábrica (Demo)", use_container_width=True):
            cofre.resetar_base_demonstracao()
            st.sidebar.success("Base de dados resetada para o estado inicial de testes.")
            st.rerun()

# ==========================================
# TELA PRINCIPAL E CABEÇALHO
# ==========================================
st.title("🛡️ Portal de Transparência e Governança Cidadã — CEF 10")

# TRATAMENTO DE SEGURANÇA E BLOQUEIO FAIL-SAFE
if not cadeia_integra:
    st.error(f"🚨 **ALERTA CRÍTICO DE SEGURANÇA E BLOQUEIO DO SISTEMA**\n\n{mensagem_auditoria}\n\n*O acesso público às informações foi suspenso preventivamente para garantir que nenhum cidadão seja induzido ao erro por dados adulterados.*")
    
    # Se o Admin estiver logado, exibe o painel de recuperação forense no centro da tela
    if st.session_state.autenticado and st.session_state.role_gestor == "admin":
        st.warning("🔧 **Painel de Perícia do Administrador:**")
        st.write("Como Superusuário autenticado, você pode efetuar o Rollback de Segurança. Isso salvará o arquivo corrompido na quarentena e restaurará os dados legítimos registrados até antes do ataque.")
        
        col_rec1, col_rec2 = st.columns(2)
        with col_rec1:
            if st.button("🛡️ Executar Rollback Criptográfico (Preservar Dados Autênticos)"):
                ok, res_msg = cofre.recuperar_ultimo_estado_valido(USUARIOS_SISTEMA)
                st.success(res_msg)
                st.rerun()
        with col_rec2:
            if st.button("🔄 Resetar para Padrão Inicial (Demonstração)"):
                cofre.resetar_base_demonstracao()
                st.success("Base resetada para os dados de teste.")
                st.rerun()
    else:
        st.info("ℹ️ *Apenas o Administrador do Sistema possui autorização para periciar e restabelecer a integridade do nó.*")
        
    st.stop() # TRAVA TOTAL DE SEGURANÇA
else:
    st.success(f"🟢 **Selo de Auditabilidade Ativo:** {mensagem_auditoria} (Verificação SHA-256 e HMAC)")

st.markdown("Acompanhe a aplicação dos recursos públicos, contratos oficiais, editais e a evolução física das obras com total rastreabilidade.")

# ==========================================
# FORMULÁRIO DE GESTÃO (PARA GESTORES E ADMIN)
# ==========================================
if st.session_state.autenticado:
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Gestão de Recursos e Obras")
    
    acao_gestao = st.sidebar.radio(
        "Selecione a Ação:",
        ["🌱 Cadastrar Novo Projeto (Tronco)", "🌿 Atualizar / Evoluir Obra Existente"]
    )
    
    with st.sidebar.form(key="form_evolucao_obra", clear_on_submit=True):
        projeto_id_selecionado = None
        
        if acao_gestao == "🌱 Cadastrar Novo Projeto (Tronco)":
            tipo_reg = "Criacao"
            descricao_input = st.text_input("Nome / Descrição do Novo Projeto")
        else:
            tipo_reg = "Atualizacao"
            projetos_dict = cofre.obter_projetos_existentes()
            
            if projetos_dict:
                projeto_escolhido_nome = st.selectbox("Selecione a Obra / Projeto", list(projetos_dict.values()))
                for pid, pdesc in projetos_dict.items():
                    if pdesc == projeto_escolhido_nome:
                        projeto_id_selecionado = pid
                        descricao_input = pdesc
                        break
            else:
                st.warning("Nenhum projeto cadastrado.")
                descricao_input = ""

        valor_input = st.number_input("Valor Alocado / Aditivo (R$)", min_value=0.0, format="%.2f")
        
        origem_input = st.selectbox(
            "Origem do Recurso / Fonte",
            [
                "Tesouro / Recursos Próprios da Secretaria de Educação (SEEDF)",
                "Programa de Descentralização Administrativa e Financeira (PDAF / SEEDF)",
                "Emenda Parlamentar Distrital (CLDF)",
                "Emenda Parlamentar Federal (Congresso Nacional)",
                "Programa Nacional de Dinheiro Direto na Escola (PNDE / FNDE)",
                "Doação / Parceria com a Comunidade"
            ]
        )
        
        responsavel_input = st.text_input("Autoridade / Órgão Responsável", placeholder="Ex: SEEDF...")
        status_input = st.selectbox("Fase / Status Atualizado", list(DICIONARIO_CIDADAO.keys()))
        
        st.markdown("---")
        st.caption("📄 **Dados Oficiais de Licitação e Governo**")
        empenho_input = st.text_input("Número da Nota de Empenho (Ex: 2026NE00123)")
        edital_input = st.text_input("Edital de Licitação / Processo (Ex: PE nº 04/2026)")
        empresa_input = st.text_input("Razão Social da Empresa Contratada")
        cnpj_input = st.text_input("CNPJ da Empresa Contratada")

        justificativa_input = st.text_area("Justificativa / Observações")
        arquivo_upload = st.file_uploader("Anexar Evidência (Foto ou arquivo PDF)", type=["jpg", "jpeg", "png", "pdf"])
        
        botao_enviar = st.form_submit_button("Assinar Digitalmente e Gravar")

        if botao_enviar:
            if descricao_input and valor_input >= 0:
                caminho_foto_final = "N/A"
                if arquivo_upload is not None:
                    caminho_arquivo = os.path.join(IMAGENS_DIR, arquivo_upload.name)
                    with open(caminho_arquivo, "wb") as f:
                        f.write(arquivo_upload.getbuffer())
                    caminho_arquivo_final = caminho_arquivo

                autor_completo = f"{st.session_state.nome_gestor} (CPF: {st.session_state.cpf_gestor})"
                
                cofre.adicionar_bloco(
                    descricao=descricao_input,
                    valor=valor_input,
                    status=status_input,
                    justificativa=justificativa_input,
                    foto_path=caminho_arquivo_final,
                    origem=origem_input,
                    responsavel=responsavel_input if responsavel_input.strip() else "Não informado",
                    empenho=empenho_input if empenho_input.strip() else "N/A",
                    edital=edital_input if edital_input.strip() else "N/A",
                    empresa=empresa_input if empresa_input.strip() else "N/A",
                    cnpj=cnpj_input if cnpj_input.strip() else "N/A",
                    autor=autor_completo,
                    tipo_registro=tipo_reg,
                    chave_privada=st.session_state.chave_privada,
                    projeto_id=projeto_id_selecionado
                )
                st.sidebar.success("Evolução registrada e assinada digitalmente!")
                st.rerun()

# ==========================================
# DASHBOARD DE MÉTRICAS PRINCIPAIS (CONTABILIDADE PÚBLICA)
# ==========================================
total_alocado = 0.0
total_gasto = 0.0

# Agrupa os blocos para separar o Orçamento (Empenho) do Gasto Real (Contrato)
mapa_projetos = {}
for bloco in cofre.chain:
    if bloco.projeto_id == "genesis-cef10":
        continue
    if bloco.projeto_id not in mapa_projetos:
        mapa_projetos[bloco.projeto_id] = []
    mapa_projetos[bloco.projeto_id].append(bloco)

for pid, blocos in mapa_projetos.items():
    # O primeiro bloco define o Teto Orçamentário
    total_alocado += blocos[0].valor
    
    # O último bloco define o Gasto Real (se já saiu da fase 1)
    ultimo_bloco = blocos[-1]
    if "Empenhado" not in ultimo_bloco.status:
        total_gasto += ultimo_bloco.valor

total_disponivel = total_alocado - total_gasto
total_projetos = len(mapa_projetos)

# Rótulos 
col1, col2 = st.columns(2)
col1.metric("Orçamento", f"R$ {total_alocado:,.2f}")
col2.metric("Obras e Serviços", total_projetos)

st.write("") # Espaço para separar as métricas

col3, col4 = st.columns(2)
col3.metric("Contratado", f"R$ {total_gasto:,.2f}")
col4.metric("Saldo", f"R$ {total_disponivel:,.2f}")

# Mini-dicionário sugerido para clareza do cidadão
with st.expander("ℹ️ Entenda as Métricas Financeiras acima"):
    st.markdown("""
    - **Orçamento:** Teto de gastos reservado inicialmente pelo governo (Nota de Empenho).
    - **Contratado:** Valor real e definitivo firmado com a empresa após a fase de licitação.
    - **Saldo:** Dinheiro economizado (Orçamento - Contratado) que retorna ou é realocado.
    - **Obras e Serviços:** Quantidade de projetos sendo monitorados no painel.
    """)

st.divider()

# ==========================================
# FUNÇÃO AUXILIAR: GERADOR DE RELATÓRIO PDF
# ==========================================
def gerar_pdf_relatorio(cofre):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    # Cabeçalho Institucional
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "PORTAL DE TRANSPARÊNCIA E GOVERNANÇA CIDADÃ", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, "Centro de Ensino Fundamental 10 (CEF 10) - Gama/DF", ln=True, align="C")
    pdf.cell(0, 6, f"Emitido em: {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "RELATÓRIO DE AUDITORIA DE RECURSOS E OBRAS", ln=True)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 9)
    for bloco in cofre.chain:
        if bloco.projeto_id == "genesis-cef10":
            continue
            
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, f" Projeto: {bloco.descricao}", ln=True, fill=True)
        
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(95, 5, f"Status: {bloco.status}", ln=False)
        pdf.cell(95, 5, f"Valor: R$ {bloco.valor:,.2f}", ln=True)
        
        pdf.cell(95, 5, f"Empenho: {bloco.num_empenho}", ln=False)
        pdf.cell(95, 5, f"Edital: {bloco.num_edital}", ln=True)
        
        pdf.cell(95, 5, f"Empresa: {bloco.empresa_contratada}", ln=False)
        pdf.cell(95, 5, f"CNPJ: {bloco.cnpj_empresa}", ln=True)
        
        pdf.cell(0, 5, f"Origem do Recurso: {bloco.origem_recurso}", ln=True)
        pdf.cell(0, 5, f"Assinado por: {bloco.autor}", ln=True)
        
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 5, f"Hash SHA-256: {bloco.hash}", ln=True)
        pdf.cell(0, 5, f"Assinatura HMAC: {bloco.assinatura_digital}", ln=True)
        pdf.ln(4)
    
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 10, "Documento gerado com autenticidade criptográfica imutável via Blockchain CEF 10.", align="C")
    
    return bytes(pdf.output())

# ==========================================
# PORTAL DE DADOS ABERTOS (DOWNLOAD CÍVICO)
# ==========================================
st.markdown("#### 📥 Portal de Dados Abertos (Open Data)")
st.caption("Baixe o histórico integral e inviolável das transações para auditoria independente pelo Conselho Escolar ou Tribunal de Contas.")

# Preparação dos dados para download
df_exportacao = cofre.obter_dataframe_historico()
csv_dados = df_exportacao.to_csv(index=False).encode('utf-8')
json_dados = json.dumps([bloco.to_dict() for bloco in cofre.chain], ensure_ascii=False, indent=4)
pdf_dados = gerar_pdf_relatorio(cofre)

col_d1, col_d2, col_d3 = st.columns(3)
with col_d1:
    st.download_button(label="📄 Baixar Relatório (PDF)", data=pdf_dados, file_name="relatorio_auditoria_cef10.pdf", mime="application/pdf", use_container_width=True)
with col_d2:
    st.download_button(label="📄 Baixar Histórico (CSV)", data=csv_dados, file_name="historico_cef10_auditoria.csv", mime="text/csv", use_container_width=True)
with col_d3:
    st.download_button(label="📦 Baixar Ledger (JSON)", data=json_dados, file_name="ledger_cef10_autentica.json", mime="application/json", use_container_width=True)

st.divider()

# ==========================================
# EXIBIÇÃO DOS PROJETOS E HISTÓRICO EM ABAS
# ==========================================
st.subheader("📂 Índice Cívico de Obras e Recursos")

# Títulos curtos para encaixar perfeitamente em telas menores
aba_todos, aba_empenhado, aba_licitacao, aba_execucao, aba_concluido, aba_ia = st.tabs([
    "📋 Todos", "🔴 Empenhados", "🟡 Licitação", "🔵 Execução", "🟢 Concluídos", "🔮 Projeções de IA"
])

def renderizar_lista_projetos(filtro_status=None):
    if not mapa_projetos:
        st.info("Nenhum projeto cadastrado na blockchain até o momento.")
        return

    encontrou_projeto = False

    for projeto_id, blocos in mapa_projetos.items():
        bloco_atual = blocos[-1]
        
        if filtro_status and not str(bloco_atual.status).startswith(filtro_status):
            continue
            
        encontrou_projeto = True
        
        # Pega apenas o valor do último contrato vigente (evita a soma cumulativa)
        valor_vigente_projeto = bloco_atual.valor
        
        cor_status = "📌"
        if "Empenhado" in bloco_atual.status:
            cor_status = "🔴"
        elif "Licitação" in bloco_atual.status:
            cor_status = "🟡"
        elif "Execução" in bloco_atual.status:
            cor_status = "🔵"
        elif "Entregue" in bloco_atual.status:
            cor_status = "🟢"

        explicacao_status = DICIONARIO_CIDADAO.get(bloco_atual.status, bloco_atual.status)

        with st.expander(f"{cor_status} **{bloco_atual.descricao}** — Status: *{bloco_atual.status}* (Valor Vigente: R$ {valor_vigente_projeto:,.2f})"):
            
            st.markdown(f"### 📊 Situação Atual do Projeto")
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.write(f"**Status Atual:** {bloco_atual.status}")
                st.info(f"💡 **O que isso significa:** {explicacao_status}")
                st.write(f"**Valor do Contrato:** R$ {valor_vigente_projeto:,.2f}")
                st.write(f"**Origem do Recurso:** 🏛️ `{bloco_atual.origem_recurso}`")
            with col_info2:
                st.write(f"**Última Atualização:** {bloco_atual.timestamp}")
                st.write(f"**Gestor Responsável:** ✍️ {bloco_atual.autor}")
                st.markdown(f"🔑 **Hash do Bloco:** `{bloco_atual.hash[:16]}...`")
                st.markdown(f"🔏 **Assinatura HMAC:** `{bloco_atual.assinatura_digital[:16]}...`")

            st.markdown("#### 🔍 Ficha de Auditoria e Rastreabilidade")
            with st.container(border=True):
                col_aud1, col_aud2 = st.columns(2)
                with col_aud1:
                    st.write(f"📄 **Nº Nota de Empenho:** `{bloco_atual.num_empenho}`")
                    st.write(f"📜 **Edital / Processo:** `{bloco_atual.num_edital}`")
                with col_aud2:
                    st.write(f"🏢 **Empresa:** `{bloco_atual.empresa_contratada}`")
                    st.write(f"🆔 **CNPJ:** `{bloco_atual.cnpj_empresa}`")

            # EXIBIÇÃO INTELIGENTE DE PDF OU IMAGEM
            if bloco_atual.foto_path != "N/A" and os.path.exists(bloco_atual.foto_path):
                if bloco_atual.foto_path.lower().endswith('.pdf'):
                    with open(bloco_atual.foto_path, "rb") as f:
                        # Define uma tag de aba para garantir chaves 100% únicas entre abas
                        aba_tag = filtro_status if filtro_status else "todos"
                        st.download_button(
                            label="📄 Baixar Documento Oficial (PDF)",
                            data=f,
                            file_name=os.path.basename(bloco_atual.foto_path),
                            mime="application/pdf",
                            key=f"pdf_{bloco_atual.hash}_{aba_tag}" # Chave única por aba
                        )
                else:
                    st.image(bloco_atual.foto_path, width=500)

            st.divider()
            st.markdown("🌿 **Histórico e Evolução da Obra (Árvore de Blocos):**")
            for idx, b_historico in enumerate(blocos):
                badge = "🌱 [Tronco Alocado]" if b_historico.tipo_registro == "Criacao" else f"🌿 [Atualização {idx}]"
                st.markdown(f"""
                * **{badge}** — **Data:** {b_historico.timestamp} | **Fase:** `{b_historico.status}` | **Valor:** R$ {b_historico.valor:,.2f}
                  * *Empenho:* `{b_historico.num_empenho}` | *Empresa:* `{b_historico.empresa_contratada}`
                  * *Hash:* `{b_historico.hash[:15]}...`
                """)

    if not encontrou_projeto and filtro_status:
        st.info("Nenhum projeto encontrado para esta fase.")

with aba_todos:
    renderizar_lista_projetos(None)
with aba_empenhado:
    renderizar_lista_projetos("1")
with aba_licitacao:
    renderizar_lista_projetos("2")
with aba_execucao:
    renderizar_lista_projetos("3")
with aba_concluido:
    renderizar_lista_projetos("4")
# ==========================================
# ABA 6: MÓDULO DE INTELIGÊNCIA ARTIFICIAL E ANÁLISE PREDITIVA
# ==========================================
with aba_ia:
    st.markdown("### 🤖 Análise Preditiva e Projeção de Gastos (Machine Learning)")
    st.markdown("Utilização do algoritmo de **Regressão Linear (Scikit-Learn)** para projetar a tendência do consumo orçamentário contratado do CEF 10.")
    
    # Monta a base de treinamento usando apenas o valor vigente de cada projeto
    projetos_vigentes = []
    for pid, blocos in mapa_projetos.items():
        bloco_atual = blocos[-1]
        projetos_vigentes.append({
            "Data": bloco_atual.timestamp,
            "Projeto": bloco_atual.descricao,
            "Valor": bloco_atual.valor,
            "Status": bloco_atual.status
        })
        
    df_ia = pd.DataFrame(projetos_vigentes)
    
    if df_ia.empty or len(df_ia) < 2:
        st.info("💡 **Aviso do Módulo de IA:** Cadastre ou atualize pelo menos 2 projetos/obras para ativar o modelo preditivo de Regressão Linear.")
    else:
        df_diario = df_ia.groupby("Data")["Valor"].sum().reset_index().sort_values("Data")
        df_diario["Data"] = pd.to_datetime(df_diario["Data"])
        df_diario["Dias"] = (df_diario["Data"] - df_diario["Data"].min()).dt.days
        
        # Tratamento para testes realizados no mesmo dia
        if df_diario["Dias"].max() == 0:
            df_diario["Dias"] = range(len(df_diario))
            
        X = df_diario[["Dias"]].values
        y = df_diario["Valor"].values
        
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        ultimos_dias = df_diario["Dias"].max()
        dias_futuros = np.array([[ultimos_dias + 30], [ultimos_dias + 60], [ultimos_dias + 90]])
        datas_futuras = [df_diario["Data"].max() + pd.DateOffset(days=i) for i in [30, 60, 90]]
        predicoes_futuras = np.maximum(modelo.predict(dias_futuros), 0)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_diario["Data"], y=df_diario["Valor"],
            mode='lines+markers', name='Valores Vigentes Registrados',
            line=dict(color='#1f77b4', width=3)
        ))
        
        x_projecao = [df_diario["Data"].max()] + datas_futuras
        y_projecao = [df_diario["Valor"].values[-1]] + list(predicoes_futuras)
        
        fig.add_trace(go.Scatter(
            x=x_projecao, y=y_projecao,
            mode='lines+markers', name='Projeção Orçamentária (IA)',
            line=dict(color='#ff7f0e', width=3, dash='dash')
        ))
        
        fig.update_layout(
            title="Tendência de Alocação de Recursos Contratados",
            xaxis_title="Linha do Tempo",
            yaxis_title="Valor Contratado (R$)",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col_pred1, col_pred2 = st.columns(2)
        col_pred1.metric("Projeção Média Trimestral (Próx 90d)", f"R$ {predicoes_futuras.mean():,.2f}")
        col_pred2.metric("Tendência de Consumo", "Crescente 📈" if modelo.coef_[0] > 0 else "Estável / Decrescente 📉")
        
        st.info("💡 **Insights da IA:** O modelo projeta o comportamento do saldo contratado com base na evolução atual das licitações e obras do CEF 10.")