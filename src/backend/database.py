from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.utils.config import load_config

class VectorDatabase:
    def __init__(self):
        config = load_config()
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=config["EMBEDDING_MODEL"]
        )
        self.vector_db = Chroma(
            persist_directory=config["CHROMA_DB_PATH"],
            embedding_function=self.embedding_model
        )
    
    def query(self, query_text, k=3):
        """
        Search for top-k relevant chunks in ChromaDB based on query similarity.
        """
        results = self.vector_db.similarity_search(query_text, k=k)
        return [doc.page_content for doc in results]

# Create a singleton instance
db = VectorDatabase() 