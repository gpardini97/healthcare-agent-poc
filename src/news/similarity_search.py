from langchain_community.vectorstores import FAISS

def perform_similarity_search(
        query: str, vectorstore: FAISS, k:int=2
    ):
    """
    Perform a similarity search on a FAISS vector store.

    Args:
        query (str): The query string to search for.
        vectorstore (FAISS): A FAISS vector store object.
        k (int, optional): Number of top similar results to return. Defaults to 2.

    Returns:
        list: List of top-k documents most similar to the query.
    """
    results = vectorstore.similarity_search(query, k)
    return results

