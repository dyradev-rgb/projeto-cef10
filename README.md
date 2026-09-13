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
   git clone [https://github.com/dyradev-rgb/projeto-cef10.git](https://github.com/dyradev-rgb/projeto-cef10.git)
   cd projeto-cef10
   ```

2. **Crie um ambiente virtual e instale as dependências:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Linux/macOS
   .venv\Scripts\activate           # Windows
   pip install -r requirements.txt
   ```

3. **Gere as credenciais locais** (senhas hasheadas PBKDF2 + chaves HMAC aleatórias, fora do repositório):
   ```bash
   python scripts/gerar_credenciais.py
   python scripts/migrar_ledger.py   # re-assina a ledger demo com as novas chaves
   ```
   > ⚠️ Nunca regenere as credenciais depois sem rodar `scripts/migrar_ledger.py` novamente.

4. **Execute o portal:**
   ```bash
   streamlit run app/app.py
   ```
   Usuários de demonstração: `admin/admin` (Root), `diretor/123`, `secretaria/123`.

5. **Validação independente da cadeia** (hash, encadeamento e assinaturas):
   ```bash
   python tests/validar_ledger.py
   ```

## 🔐 Notas de Segurança (aplicadas nesta versão)
* Credenciais removidas do código-fonte → `config/seguranca.py` + `.streamlit/secrets.toml` (não versionado).
* Senhas armazenadas como hash **PBKDF2-SHA256** e comparadas em tempo constante.
* **Rate-limit** de login (trava de 30s após 5 tentativas erradas).
* Upload de evidências sanitizado (basename + revisão de extensão no servidor).
* Hash dos blocos **canônico** (`timestamp.isoformat()`), foto_path com separador `/` (portável).
* Gestores identificados por `ID` no ledger, sem CPF/nomes pessoais no JSON público.