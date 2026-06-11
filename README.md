# 📊 Totale Indicadores - Painel de Produção & Ranking

Este é um aplicativo multipáginas desenvolvido em **Streamlit** focado no monitoramento de indicadores de produção, análise de performance e engajamento de equipes através de um ranking de pontuação (gamificação).

## 🚀 Funcionalidades Principais

* **Painel de Produção**: Visualização dinâmica e em tempo real dos principais KPIs de produtividade.
* **Ranking de Pontos**: Sistema de leaderboard (pódio) para destacar equipes ou operadores de alta performance.
* **Navegação Inteligente**: Estrutura multipáginas segmentada para separar painéis gerais de relatórios específicos.
* **Gráficos Interativos**: Análise visual de evolução das metas e comportamento de dados temporais.

## 📁 Estrutura do Repositório

O projeto segue a organização padrão recomendada pelo Streamlit:

```text
├── .devcontainer/        # Configuração para desenvolvimento conteinerizado
├── .github/              # Workflows e automações do GitHub
├── .vscode/              # Configurações de workspace do Visual Studio Code
├── images/               # Ativos visuais, logos e capturas de tela do painel
├── pages/                # Páginas secundárias do aplicativo (ex: Rankings, Detalhes)
├── .gitignore            # Arquivos ignorados pelo controle de versão
├── LICENSE               # Licença de uso do projeto (Apache-2.0)
├── README.md             # Documentação do projeto
├── requirements.txt      # Bibliotecas e dependências Python
└── streamlit_app.py      # Ponto de entrada (página principal) do dashboard
```

## 🛠️ Tecnologias Utilizadas

* **Python 3.10+**
* **Streamlit**: Criação da interface do usuário.
* **Pandas / NumPy**: Processamento analítico dos dados de produção.
* **Plotly**: Visualizações e gráficos interativos de alta qualidade.

## 📦 Como Instalar e Executar Localmente

Siga os passos abaixo para rodar o painel na sua máquina local:

### 1. Clonar o Repositório
```bash
git clone https://github.com
cd totale-indicadores
```

### 2. Configurar o Ambiente Virtual (Recomendado)
```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar no Windows:
venv\Scripts\activate

# Ativar no Linux/macOS:
source venv/bin/activate
```

### 3. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 4. Executar o Aplicativo
```bash
streamlit run streamlit_app.py
```
O painel abrirá automaticamente no seu navegador em `http://localhost:8501`.

---

## ⚙️ Regras do Ranking (Gamificação)
A pontuação exibida no ranking é gerada dinamicamente utilizando as seguintes regras básicas:
* **Entrega de Meta**: +100 pontos.
* **Eficiência Operacional (>90%)**: +50 pontos bônus.
* **Taxa de Desperdício/Refugo (<1%)**: +30 pontos bônus.
* **Desvios ou Atrasos**: -20 pontos.

---
Desenvolvido por [denisvick-dev](https://github.com/denisvick-dev). Licença Apache-2.0.