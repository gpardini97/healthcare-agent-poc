# 🧠 Healthcare Agent POC

**Prova de Conceito (POC) de aplicação de inteligência artificial para geração de relatório de  monitoramento de surtos de Síndrome Respiratória Aguda Grave (SRAG).**  

Combina dados do **Open DATASUS** com **agentes de IA generativa** para gerar relatórios automatizados contendo:  
- 📊 Métricas de saúde essenciais  
- 📈 Visualizações gráficas  
- 📰 Contexto de notícias em tempo real  

Tudo pensado para apoiar profissionais de saúde na análise rápida e precisa de informações sobre SRAG.

## Estrutura do Projeto
```
healthcare-agent-poc/
│
├── data/
│   ├── raw/           # 📁 Tabelas cruas baixadas do OpenData SUS (somente local, não versionadas)
│   ├── interim/       # 📦 Arquivo .parquet pré-processado para cálculos (versionado e gerado via notebooks/eda_notebook.ipynb)
│   └── processed/     # 📄 Pasta de saída com o relatório final em PDF (versionado em git, consta como final_report.pdf)
│
├── images/             # 🖼️ Gráficos gerados salvos em .png
│
├── notebooks/          # 📓 Notebooks utilizados para prototipação e geração de df_srag.parquet
│
├── src/                # 💻 Código fonte principal
│   ├── charts/         # Script `create_charts.py` para criação e armazenamento de gráficos
│
│   ├── metrics/        # Script `calc_metrics.py` que calcula métricas a partir dos dados
│
│   ├── news/           # Scripts para busca de notícias, embeddings e vetores de similaridade
│   │   ├── embeddings.py
│   │   ├── fetch_news.py
│   │   ├── news_prompt.py
│   │   ├── similarity_search.py
│   │   └── vectorstore.py
│
│   ├── preprocessing/  # Geração de DataFrame auxiliar diário (`df_daily_info`) para métricas e plots
│
│   └── processing/     # Processamentos críticos da solução
│       ├── generate_final_prompt.py  # Gera o prompt final para o relatório
│       ├── generate_pdf_file.py      # Agrega texto final + gráficos em PDF
│       ├── generate_report_text.py   # Contém a chain de geração do texto final
│       └── process_data.py      # 🔄 Função que gera o prompt das métricas e aciona cálculo + geração de plots
│
├── run_agent.py         # 🚀 Script principal do agente (sequência completa, variáveis, chains e prompts)
│
├── .env                 # 🔑 Variáveis de ambiente
│
├── .gitignore
│
├── diag_conceitual.pdf  # Diagrama conceitual do projeto em .pdf 
│
└── README.md            # 📖 Documentação do projeto
```

## 🚀 Como executar o projeto

A POC inteira é executada em linha de comando, assim como interações com o agente. 
Para rodar, siga os passos abaixo:

---

### 1️⃣ Criar um ambiente virtual (preferencialmente fora da pasta do repositório)

```bash
python -m venv venv_srag
```

### 2️⃣ Ativar ambiente virtual

- Windows:

```venv_srag\Scripts\activate```

- macOS / Linux:

```source venv_srag/bin/activate```

### 3️⃣ Instalar as dependências

```pip install -r requirements.txt```

### 4️⃣ Criar arquivo .env e editá-lo

- Copie o arquivo de exemplo `.env.example` para `.env`, com:

    - Windows: 
    ```bash
    copy .env.example .env
    ```

    - macOS / Linux:
    ```
    cp .env.example .env
    ``` 

- Insira as variáveis de ambiente necessárias: 
    - ANTHROPIC_API_KEY - Chave API da Anthropic (paga) para acesso ao modelo Claude Haiku 3.5 utilizado nessa solução, disponível em https://console.anthropic.com/

    - NEWS_API_KEY - Chave API do site https://newsapi.org/ que faz a busca por notícias em tempo real (gratuita, mas possui limite de caracteres para a descrição das notícias)

### 5️⃣ Executar o agente
- Executar o comando para iniciar a interação com o sistema de agentes: 

    ```python run_agent.py```

    - O agente interage via linha de comando.

    - Relatório final em PDF será gerado em data/processed/, mas é também aberto automaticamente.

    - Gráficos utilizados são salvos em images/. 


## Funcionamento do sistema:

- O sistema funciona apenas a partir da confirmação do usuário via prompt em linguagem natural, dado o fornecimento de informações relvantes como a data da base, períodos considerados para os cálculos das taxas, entre outros. A partir da confirmação, todo o fluxo é acionado e o .pdf é gerado. O fluxo de operações e cálculos está detalhado no arquivo diag_conceitual.pdf. 
