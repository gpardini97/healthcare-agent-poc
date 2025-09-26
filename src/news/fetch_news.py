"""
Module: fetch_news

Fetches news articles about SRAG from NewsAPI and returns a DataFrame.
"""

from typing import Optional
import pandas as pd
import requests

def fetch_news(API_KEY: str) -> Optional[pd.DataFrame]:

    """
    Fetches recent news articles related to SRAG in Portuguese.

    Args:
        api_key (str): Your NewsAPI key.

    Returns:
        Optional[pd.DataFrame]: A DataFrame with columns
        ['title', 'description', 'url', 'publishedAt', 'source'].
        Returns None if no articles are found or request fails.
    """

    query = "SRAG"
    language = "pt"
    page_size = 20  # How many news are displayed
    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": language,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") == "ok":
        articles = data.get("articles", [])
        if articles:
            # Transform news to a dataframe 
            df_news = pd.DataFrame([
                {
                    "title": art["title"],
                    "description": art["description"],
                    "url": art["url"],
                    "publishedAt": art["publishedAt"],
                    "source": art["source"]["name"]
                }
                for art in articles
            ])

            df_news["title"] = (
                df_news["title"].fillna("no-title")
            )

            return df_news
    else:
        print("Erro na requisição:", data.get("message"))