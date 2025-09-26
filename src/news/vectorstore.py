import pandas as pd
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from .embeddings import SentenceTransformerEmbeddings

def generate_vector_store(df_news: pd.DataFrame):
    """
    Generate a FAISS vector store from a DataFrame of news articles.

    Each document in the vector store contains the title and URL as content,
    which is the only part that will be vectorized. Additional metadata 
    (title, URL, publication date, source, description) is stored for 
    reference but is not included in the embedding.

    Args:
        df_news (pd.DataFrame): DataFrame containing news articles with columns:
            'title', 'url', 'publishedAt', 'source', 'description'.

    Returns:
        FAISS: A FAISS vector store object containing all news embeddings.
    """

    documents = []
    for _, row in df_news.iterrows():
        # Only content will be vectorized
        content = f"{row['title']} {row['url']}"
        metadata = {
            "title": row["title"],
            "url": row["url"],
            "publishedAt": row["publishedAt"],
            "source": row["source"],
            "description": row["description"]
        }
        documents.append(Document(page_content=content, metadata=metadata))

    embedding_wrapper = SentenceTransformerEmbeddings()

    vectorstore = FAISS.from_documents(documents, embedding_wrapper)

    return vectorstore