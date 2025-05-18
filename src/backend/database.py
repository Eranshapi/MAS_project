from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from ..utils.config import load_config
from typing import List, Tuple, Dict

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
        print(f"\nDatabase initialized with {self.get_total_chunks()} chunks")
    
    def get_total_chunks(self):
        """
        Get the total number of chunks in the database.
        """
        return len(self.vector_db.get()['ids'])
    
    def query(self, query_text: str, k: int = 3, score_threshold: float = 0.14) -> List[Tuple[str, float]]:
        """
        Search for top-k relevant chunks in ChromaDB based on query similarity.
        Returns a list of tuples containing (chunk_content, similarity_score).
        
        Args:
            query_text: The query text to search for
            k: Number of top results to return
            score_threshold: Minimum similarity score threshold (0-1)
        """
        # Get results with scores
        results = self.vector_db.similarity_search_with_score(
            query_text,
            k=k
        )
        
        print(f"\nRaw similarity scores:")
        for doc, score in results:
            print(f"Distance: {score:.4f}")
        
        # Filter and format results
        filtered_results = []
        for doc, score in results:
            # Convert distance to similarity score with better scaling
            similarity_score = 1.0 / (1.0 + score * 0.5)  # Adjusted multiplier for better scaling
            print(f"Converted similarity score: {similarity_score:.4f}")
            
            if similarity_score >= score_threshold:
                filtered_results.append((doc.page_content, similarity_score))
        
        return filtered_results

# Create a singleton instance
db = VectorDatabase() 