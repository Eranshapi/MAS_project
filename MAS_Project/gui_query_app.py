import os
import requests
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Load ChromaDB with HuggingFace Embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = Chroma(
    persist_directory=r"C:\Users\erans\.cursor\MAS_Project\chroma_db",
    embedding_function=embedding_model
)

# ChromaDB Query
def query_database(query_text, k=3):
    results = vector_db.similarity_search(query_text, k=k)
    return [doc.page_content for doc in results]

# Ask Groq LLM
def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Groq API Error: {response.text}")
    return response.json()["choices"][0]["message"]["content"]
# GUI App with improved readability and Hebrew support
def run_gui():
    root = tk.Tk()
    root.title("MAS Project - Smart Search")

    # Set default font to a more readable one that supports Hebrew
    default_font = ("Arial", 12)
    root.option_add("*Font", default_font)

    # Configure the main window
    root.geometry("800x600")
    root.configure(bg="#f0f0f0")

    # Create a frame for better layout management
    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Create a scrolled text area for displaying results
    text_area = scrolledtext.ScrolledText(frame, width=100, height=30, wrap=tk.WORD, font=default_font)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def handle_query():
        query = simpledialog.askstring("Ask your Question", "Enter your question:", parent=root)
        if not query:
            return

        text_area.insert(tk.END, f"\n\nYou asked: {query}\n")
        text_area.insert(tk.END, "-" * 70 + "\n")

        chunks = query_database(query)
        context = "\n".join(chunks)

        text_area.insert(tk.END, "Top Retrieved Chunks from DB:\n")
        for chunk in chunks:
            text_area.insert(tk.END, chunk + "\n")
            text_area.insert(tk.END, "-" * 50 + "\n")

        prompt = f"בהתבסס על הקונטקסט הבא צענה על השאלה בשפה שבא נכתבה השאלה:\n\nContext:\n{context}\n\nQuestion: {query}"
        answer = ask_groq(prompt)

        text_area.insert(tk.END, "\nGroq Answer:\n")
        text_area.insert(tk.END, "-" * 50 + "\n")
        text_area.insert(tk.END, answer + "\n")
        text_area.insert(tk.END, "=" * 70 + "\n")

    ask_button = tk.Button(frame, text="Ask a Question", command=handle_query, font=("Arial", 14), bg="#4CAF50", fg="white")
    ask_button.pack(pady=10)

    root.mainloop()




# GUI App
def run_gui():
    root = tk.Tk()
    root.title("MAS Project - Smart Search")

    text_area = scrolledtext.ScrolledText(root, width=100, height=30, wrap=tk.WORD)
    text_area.pack(padx=10, pady=10)

    def handle_query():
        query = simpledialog.askstring("Ask your Question", "Enter your question:")
        if not query:
            return

        text_area.insert(tk.END, f"\n\nYou asked: {query}\n")
        text_area.insert(tk.END, "-" * 70 + "\n")

        chunks = query_database(query)
        context = "\n".join(chunks)

        text_area.insert(tk.END, "Top Retrieved Chunks from DB:\n")
        for chunk in chunks:
            text_area.insert(tk.END, chunk + "\n")
            text_area.insert(tk.END, "-" * 50 + "\n")

        prompt = f"בההתבסס על הקונטקסט הבא צענה על השאלה בשפה שבא נכתבה השאלה:\n\nContext:\n{context}\n\nQuestion: {query}"
        answer = ask_groq(prompt)

        text_area.insert(tk.END, "\nGroq Answer:\n")
        text_area.insert(tk.END, "-" * 50 + "\n")
        text_area.insert(tk.END, answer + "\n")
        text_area.insert(tk.END, "=" * 70 + "\n")

    ask_button = tk.Button(root, text="Ask a Question", command=handle_query, font=("Arial", 14))
    ask_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
