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
    
    return {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "EMBEDDING_MODEL": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "CHROMA_DB_PATH": "chroma_db",
        "GROQ_MODEL": "llama3-70b-8192"
    } 