"""
Module: Sentence Transformer Embeddings

Provides a LangChain-compatible wrapper around the
SentenceTransformers library for generating embeddings.
"""

from typing import List

from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings


class SentenceTransformerEmbeddings(Embeddings):
    """
    LangChain-compatible wrapper for SentenceTransformers models.

    Args:
        model_name (str, optional): Name of the pre-trained model
            to use. Defaults to 'all-MiniLM-L6-v2'.
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.

        Args:
            texts (List[str]): List of text documents.

        Returns:
            List[List[float]]: Embeddings for each document.
        """
        return [self.model.encode(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        """
        Generate an embedding for a single query string.

        Args:
            text (str): The input query string.

        Returns:
            List[float]: Embedding vector for the query.
        """
        return self.model.encode(text)