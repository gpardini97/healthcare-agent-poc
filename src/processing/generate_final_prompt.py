from datetime import datetime

def generate_final_prompt(
        metrics_prompt: str,
        top_news_content_list: list,
        last_date: datetime,
        chart_daily_period: int,
        chart_monthly_period: int
    ) -> str:

    """
    Generate the final prompt for the AI agent to produce a SRAG report.

    Args:
        metrics_prompt (str): Text describing the calculated metrics.
        top_news_content_list (List): List of LangChain Document objects representing top news.
        last_date (datetime): Latest date of the dataset.
        chart_daily_period (int): Number of days to reference in the daily chart.
        chart_monthly_period (int): Number of months to reference in the monthly chart.

    Returns:
        str: The final prompt string, ready to be sent to the AI model.
    """

    news_prompt = build_news_prompt(top_news_content_list)

    # Formatting datetime to a more coherent style “dd/mm/yyyy”
    last_date_str = last_date.strftime("%d/%m/%Y")

    final_prompt = f"""
        Você é um analista de saúde pública especializado em surtos de Síndrome Respiratória Aguda Grave (SRAG).
        Com base nos dados e nas notícias fornecidas, produza um relatório técnico, bem estruturado e coerente.

        Dados até {last_date_str}:
        {metrics_prompt}

        Notícias de apoio:
        {news_prompt}

        Instruções para elaboração do relatório:
        1. Faça uma abertura contextual apresentando o cenário recente da SRAG.
        2. Comente cada métrica, destacando tendências (alta, queda ou estabilidade).
        3. Use as notícias apresentadas para contextualizar ou explicar os números, se possível.
        4. Finalize com considerações, pontos de atenção e recomendações de acompanhamento.
        5. Ao final, inclua introdução textual para os dois gráficos de casos relativos aos últimos {chart_daily_period} dias e aos últimos {chart_monthly_period} meses.

        O texto deve ser corrido (não listas), linguagem clara, profissional e objetiva.

        Observações:
        - Use apenas as informações fornecidas neste prompt.
        - Se alguma relação entre métricas e notícias não for evidente, não invente: informe apenas o que for suportado pelos dados ou pelas notícias.
        - Não realize assinaturas no final.
        - Quando mencionar uma notícia pela primeira vez, inclua o URL de referência em (). 

        """
    
    return final_prompt

def build_news_prompt(top_news_content_list: list) -> str:
    """
    Convert a list of news Document objects into a formatted text block.

    Args:
        top_news_content_list (List): List of LangChain Document objects with metadata for each news item.

    Returns:
        str: Formatted text containing title, URL, publication date, source, and description for each news item.
    """
    news_texts = []
    for doc in top_news_content_list:
        news_texts.append(
            f"Título: {doc.metadata['title']}\n"
            f"URL: {doc.metadata['url']}\n"
            f"Publicado em: {doc.metadata['publishedAt']}\n"
            f"Fonte: {doc.metadata['source']}\n"
            f"Descrição: {doc.metadata['description']}\n"
        )
    return "\n".join(news_texts)
