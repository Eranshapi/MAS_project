import os
import requests
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import gradio as gr
import webbrowser
from threading import Timer

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Load ChromaDB with HuggingFace Embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_db = Chroma(
    persist_directory="chroma_db",
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


# Gradio web interface function
def handle_query(query):
    if not query:
        return "Please enter a question."

    result = f"You asked: {query}\n"
    result += "-" * 70 + "\n"

    chunks = query_database(query)
    context = "\n".join(chunks)
    '''
    result += "Top Retrieved Chunks from DB:\n"
    for chunk in chunks:
        result += chunk + "\n"
        result += "-" * 50 + "\n"
    '''
    prompt = f"בהתבסס על הקונטקסט הבא תענה על השאלה בעברית:\n\nContext:\n{context}\n\nQuestion: {query}"
    answer = ask_groq(prompt)

    result += "\nGroq Answer:\n"
    result += "-" * 50 + "\n"
    result += answer + "\n"
    result += "=" * 70 + "\n"

    return result


# Create and launch the web interface
def run_gui():
    # Create Gradio interface
    interface = gr.Interface(
        fn=handle_query,
        inputs=gr.Textbox(placeholder="Enter your question here...", label="Question"),
        outputs=gr.Textbox(label="Results", lines=20),
        title="MAS Project - Smart Search",
        description="Ask questions about your documents and get AI-powered answers.",
        theme="huggingface",
        css=".gradio-container {font-family: 'Arial', sans-serif; font-size: 16px;}"
    )

    # Launch the interface
    app_url = interface.launch(share=False, inbrowser=False)
    print(f"Web interface is running at: {app_url}")

    # Open the browser after a short delay
    def open_browser():
        webbrowser.open(app_url)
        print(f"Browser opened to: {app_url}")

    Timer(1.5, open_browser).start()

    return app_url


if __name__ == "__main__":
    run_gui()
