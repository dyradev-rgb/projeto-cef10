# 🛡️ Portal de Transparência e Governança Cidadã — CEF 10

Sistema descentralizado de prestação de contas, rastreabilidade orçamentária e análise preditiva baseado em tecnologia Blockchain (SHA-256 e HMAC), desenvolvido para o Centro de Ensino Fundamental 10 (CEF 10) do Gama, Distrito Federal.

## 🚀 Sobre o Projeto
Este projeto foi desenvolvido como requisito da **Atividade Extensionista II (CST em Ciência de Dados)** do Centro Universitário UNINTER. O objetivo é solucionar a falta de granularidade e transparência na gestão de recursos escolares, unindo **criptografia aplicada à segurança pública** e **modelos de Inteligência Artificial para projeção orçamentária**.

## ✨ Principais Funcionalidades
* **Motor Ledger Criptográfico:** Cadeia de blocos com hashing SHA-256 e encadeamento imutável de transações.
* **Assinatura Digital HMAC:** Garantia de não-repúdio e autoria vinculada às chaves privadas dos gestores (Direção, Secretaria e Admin).
* **Trava de Segurança Fail-Safe:** Detecção automática de adulterações diretas no banco de dados (JSON) com bloqueio imediato do portal.
* **Quarentena Forense e Rollback Inteligente:** Isolamento de arquivos corrompidos e restauração do último estado válido sem perda de dados históricos legítimos.
* **Portal de Dados Abertos:** Exportação instantânea de relatórios de auditoria em formatos `.csv` e `.json`.
* **Módulo de IA & Análise Preditiva:** Algoritmo de Regressão Linear (`scikit-learn`) integrado a gráficos dinâmicos (`plotly`) para projeção de tendências de consumo orçamentário.
* **Controle de Acesso RBAC:** Perfis distintos para Cidadão (Consulta pública), Gestores (Lançamento de obras) e Administrador (Central de auditoria/testes).

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.10+
* **Interface Web:** Streamlit
* **Ciência de Dados & IA:** Pandas, NumPy, Scikit-Learn, Plotly
* **Criptografia:** Bibliotecas nativas `hashlib` e `hmac`

## ⚙️ Como Executar o Projeto Localmente

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/dyegoalquimim/projeto-cef10.git](https://github.com/dyegoalquimim/projeto-cef10.git)
   cd projeto-cef10