import os
import json
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_anthropic import ChatAnthropic

from src.processing.process_data import generate_metrics_prompt_and_plots
from src.processing.generate_final_prompt import generate_final_prompt
from src.processing.generate_report_text import generate_final_report
from src.processing.generate_pdf_file import build_pdf_report
from src.news.fetch_news import fetch_news
from src.news.vectorstore import generate_vector_store
from src.news.similarity_search import perform_similarity_search


# Loading environment variables 
load_dotenv()
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")

# Utilizing Claude Haiku 3.5 model (to start) as the LLM
llm = ChatAnthropic(
    model="claude-3-5-haiku-latest", temperature=0, 
    anthropic_api_key=anthropic_api_key
)

# Defining reading/output paths
BASE_DIR = Path("data/interim")  
EXP_DIR = Path("data/processed")
IMAGES_DIR = Path("images")

# Reading main dataframe
df_srag = pd.read_parquet(f"{BASE_DIR}/df_srag.parquet")
last_available_date = df_srag["DT_NOTIFIC"].max()

# Defining periods (days) for each rate calculation
# (now they are static, in the future they can be dynamic, if desired)
qty_of_cases_var_period_1 = 7
qty_of_cases_var_period_2 = 30
death_rate_period = 30 
uti_occup_rate_period = 30 
vacc_rate_period = 30 

# Defining chart periods 
chart_daily_period = 30 #days
chart_monthly_period = 12 #months

# Mensagem inicial enxuta
welcome_message = f"""
Olá! 👋

Bem-vindo ao agente de criação de relatórios automáticos de SRAG. Os dados mais recentes da base são de {last_available_date.date()}.

📊 Métricas principais calculadas, com seus respectivos períodos:
- Aumento de casos: últimos {qty_of_cases_var_period_1} dias e últimos {qty_of_cases_var_period_2} dias
- Taxa de mortalidade: últimos {death_rate_period} dias
- Taxa de ocupação de UTI: últimos {uti_occup_rate_period} dias
- Taxa de vacinação da população: últimos {vacc_rate_period} dias

🔹 Gráficos gerados, com seus respectivos períodos:
1. Casos diários dos últimos {chart_daily_period} dias
2. Casos mensais últimos 12 meses

Podemos gerar um relatório em .pdf? 
"""

pdf_confirm_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Você é um assistente que interpreta a resposta do usuário quando perguntado "
     "se deseja gerar o relatório em formato PDF.\n\n"
     "Sua resposta deve ser SEMPRE em JSON no formato:\n"
     "{{\n"
     "  \"generate_pdf\": true/false  # true se o usuário quer gerar o PDF, false caso contrário\n"
     "}}\n\n"
     "Regra: apenas analise se o usuário aceitou ou recusou, não explique nada."
    ),
    ("human", "{input}")
])

confirm_chain = pdf_confirm_prompt | llm | StrOutputParser()

def confirm_execution(texto: str) -> dict:
    raw = confirm_chain.invoke({"input": texto})
    return json.loads(raw)

if __name__ == "__main__":
    print(welcome_message)
    user_entry = input()
    decisao = confirm_execution(user_entry)

    if decisao["generate_pdf"]:
        print("Calculando métricas e gerando gráficos. . .")
        metrics_prompt = generate_metrics_prompt_and_plots(
            qty_of_cases_var_period_1, 
            qty_of_cases_var_period_2, 
            death_rate_period, 
            uti_occup_rate_period,
            vacc_rate_period,
            df_srag
        )

        print("Buscando noticias relacionadas a SRAG. . .")
        df_news = fetch_news(news_api_key)

        print("Criando embeddings e banco vetorial. . .")
        vector_store = generate_vector_store(df_news)

        print(
            "Realizando busca por similaridade, extraindo top 2 notícias relacionadas. . ."    
        )
        news_query = "SRAG aumento de casos/taxa de vacinação/taxa de mortalidade/taxa de internação em UTI/ Brasil"

        top_news_content_list = perform_similarity_search(
            news_query, vector_store, k=2
        )

        print("Gerando prompt final. . .")
        final_prompt = generate_final_prompt(
            metrics_prompt, top_news_content_list, last_available_date, 
            chart_daily_period, chart_monthly_period
        )

        print("Executando a chain final para criação do texto. . .")
        final_text_report = generate_final_report(final_prompt, llm)

        print("Gerando e salvando o .pdf. . .")
        build_pdf_report(
            EXP_DIR, IMAGES_DIR, final_text_report, 
            title = "Relatório Técnico do Panorama de SRAG"
        )


    else:
        print(
            "Poxa, que pena! 😕\n"
            "Mas não se preocupe: em breve vamos deixar a solução mais robusta, "
            "permitindo variar os períodos das métricas e da busca por notícias. "
            "Assim você terá ainda mais controle sobre os relatórios gerados!"
        )
