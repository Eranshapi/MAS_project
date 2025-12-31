from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.storage import LocalFileStore
from ..utils.config import load_config
from typing import List, Tuple, Dict, Optional
import json

class VectorDatabase:
    def __init__(self):
        config = load_config()
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=config["EMBEDDING_MODEL"]
        )
        # Vector store for child chunks
        self.vector_db = Chroma(
            persist_directory=config["VECTOR_CHILD_DB_PATH"],
            embedding_function=self.embedding_model
        )
        # Document store for parent chunks
        self.parent_store = LocalFileStore(config["PARENT_STORE_PATH"])
        print(f"\nDatabase initialized with {self.get_total_chunks()} child chunks")
    
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
    
    def get_parent_by_id(self, parent_id: str) -> Optional[Dict]:
        """
        Retrieve a parent document by its ID from the LocalFileStore.
        
        Args:
            parent_id: The unique ID of the parent document
            
        Returns:
            Dictionary with 'page_content' and 'metadata', or None if not found
        """
        result = self.parent_store.mget([parent_id])
        if result and result[0]:
            return json.loads(result[0].decode('utf-8'))
        return None
    
    def query_with_parent_context(
        self, 
        query_text: str, 
        k: int = 3, 
        score_threshold: float = 0.14
    ) -> List[Dict]:
        """
        Search for relevant child chunks and return with their parent context.
        
        This method uses the Parent-Document Retrieval pattern:
        1. Search child chunks in vector DB for precise similarity matching
        2. Retrieve the parent chunk for each matched child for broader context
        
        Args:
            query_text: The query text to search for
            k: Number of top child results to return
            score_threshold: Minimum similarity score threshold (0-1)
            
        Returns:
            List of dictionaries containing:
            - 'child_content': The matched child chunk text
            - 'parent_content': The parent chunk text (broader context)
            - 'similarity_score': Similarity score of the child match
            - 'metadata': Child chunk metadata including parent_id
        """
        # Search child chunks in vector DB
        results = self.vector_db.similarity_search_with_score(query_text, k=k)
        
        enriched_results = []
        seen_parents = set()  # Track unique parents to avoid duplicates
        
        for doc, distance in results:
            # Convert distance to similarity score
            similarity_score = 1.0 / (1.0 + distance * 0.5)
            
            if similarity_score < score_threshold:
                continue
            
            parent_id = doc.metadata.get('parent_id')
            parent_content = None
            
            # Retrieve parent chunk if available
            if parent_id:
                parent = self.get_parent_by_id(parent_id)
                if parent:
                    parent_content = parent['page_content']
            
            enriched_results.append({
                'child_content': doc.page_content,
                'parent_content': parent_content,
                'similarity_score': similarity_score,
                'metadata': doc.metadata,
                'is_new_parent': parent_id not in seen_parents
            })
            
            if parent_id:
                seen_parents.add(parent_id)
        
        return enriched_results

# Create a singleton instance
db = VectorDatabase() 