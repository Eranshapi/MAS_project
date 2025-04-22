# backend.py
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set. Check your .env file.")

# Embedding model configuration
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
chroma_path = "chroma_db"

# Load persisted Chroma vector database
vector_db = Chroma(
    persist_directory=chroma_path,
    embedding_function=embedding_model
)

def query_database(query_text, k=3):
    """
    Search for top-k relevant chunks in ChromaDB based on query similarity.
    """
    results = vector_db.similarity_search(query_text, k=k)

    print(f"[QUERY] {query_text}")
    print(f"[TOP {k} CHUNKS]")
    for i, doc in enumerate(results):
        print(f"[{i+1}] {doc.page_content[:150]}...")

    return [doc.page_content for doc in results]

import requests

def ask_groq(prompt, model="llama3-70b-8192"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"[ERROR] Groq API failed: {response.status_code} - {response.text}")
        return "שגיאה: לא ניתן היה לקבל תשובה מהבינה המלאכותית."

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

