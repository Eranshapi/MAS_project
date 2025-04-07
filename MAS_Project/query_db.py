import os
from dotenv import load_dotenv
import requests
from langchain_chroma import Chroma  # Updated import
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
# Load environment variables
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Load ChromaDB with HuggingFace Embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = Chroma(
    persist_directory=r"C:\Users\erans\.cursor\MAS_Project\chroma_db",
    embedding_function=embedding_model
)

# Search ChromaDB
def query_database(query_text, k=3):
    results = vector_db.similarity_search(query_text, k=k)
    return [doc.page_content for doc in results]

# Ask Groq API
def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama3-70b-8192",  # Latest Groq model
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Groq API Error: {response.text}")

    return response.json()["choices"][0]["message"]["content"]

# Main Program
if __name__ == "__main__":
    query = input("Enter your question:\n")

    print("\nTop Retrieved Chunks from DB:")
    print("-" * 50)
    top_chunks = query_database(query)

    for chunk in top_chunks:
        print(chunk)
        print("-" * 50)

    # Optional: Pass combined context to Groq LLM
    context = "\n".join(top_chunks)
    prompt = f"Based on the following context answer the question:\n\nContext:\n{context}\n\nQuestion: {query}"

    answer = ask_groq(prompt)

    print("\nGroq Answer:")
    print("-" * 50)
    print(answer)
