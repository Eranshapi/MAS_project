import os
from dotenv import load_dotenv

def load_config():
    """Load environment variables and configuration settings."""
    load_dotenv()
    
    # Required environment variables
    required_vars = ["GROQ_API_KEY"]
    
    # Check for required environment variables
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Get the absolute path of the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "EMBEDDING_MODEL": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "CHROMA_DB_PATH": os.path.join(project_root, "chroma_db"),
        "VECTOR_CHILD_DB_PATH": os.path.join(project_root, "db", "vector_child"),
        "PARENT_STORE_PATH": os.path.join(project_root, "db", "parent_store"),
        "GROQ_MODEL": "llama-3.3-70b-versatile",
        # Ollama configuration for local LLM
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "llama3.2"),
    } 