import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv

# Add project root to Python path when running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.backend.document_processing.extract_text import extract_text_from_folder
from src.backend.document_processing.preprocess import preprocess_text, split_text_into_chunks, clean_text
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from src.utils.config import load_config

def create_chunks_window(chunks_data):
    # Create the main window
    root = tk.Tk()
    root.title("Database Chunks Viewer")
    root.geometry("1400x900")  # Increased size for more information

    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create a canvas with scrollbar
    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Add chunks to the scrollable frame
    for i, (doc, metadata) in enumerate(zip(chunks_data['documents'], chunks_data['metadatas']), 1):
        # Create a frame for each chunk
        chunk_frame = ttk.LabelFrame(scrollable_frame, text=f"Chunk {i}/{len(chunks_data['ids'])}")
        chunk_frame.pack(fill="x", padx=5, pady=5)

        # Create metadata frame
        metadata_frame = ttk.Frame(chunk_frame)
        metadata_frame.pack(fill="x", padx=5, pady=2)

        # Add metadata information
        metadata_info = [
            ("Source File", metadata.get('source', 'Unknown')),
            ("Document ID", metadata.get('source_doc', 'Unknown')),
            ("Chunk ID", chunks_data['ids'][i-1]),
            ("Is Table", "Yes" if doc.startswith("Table:") else "No"),
            ("Chunk Length", f"{len(doc)} characters")
        ]

        # Create a grid of metadata labels
        for row, (label, value) in enumerate(metadata_info):
            ttk.Label(metadata_frame, text=f"{label}:", font=('TkDefaultFont', 9, 'bold')).grid(row=row, column=0, sticky="w", padx=5)
            ttk.Label(metadata_frame, text=str(value)).grid(row=row, column=1, sticky="w", padx=5)

        # Add content in a text widget with monospace font for better table display
        content_text = tk.Text(chunk_frame, wrap=tk.WORD, height=10, font=('Courier', 10))
        content_text.pack(fill="x", padx=5, pady=5)
        content_text.insert("1.0", doc)
        content_text.config(state="disabled")  # Make read-only

        # Add separator
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=5, pady=5)

    # Add a close button at the bottom
    close_button = ttk.Button(scrollable_frame, text="Close", command=root.destroy)
    close_button.pack(pady=10)

    # Start the main loop
    root.mainloop()

# Load environment variables and config
load_dotenv()
config = load_config()

# Paths
data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docs")
chroma_path = config["CHROMA_DB_PATH"]

# Delete existing database if it exists
if os.path.exists(chroma_path):
    print(f"Deleting existing database at {chroma_path}")
    shutil.rmtree(chroma_path)

# Extract text from files
text_data = extract_text_from_folder(data_path)
print(f"\nExtracted text data from {len(text_data)} files")

# Preprocess text
cleaned_text = [clean_text(txt) for txt in text_data]
chunks = split_text_into_chunks(cleaned_text)

# Filter out empty or whitespace-only chunks
filtered_chunks = [chunk for chunk in chunks if chunk.page_content.strip()]

# Initialize HuggingFace Embeddings with the same model as the main application
embeddings_model = HuggingFaceEmbeddings(model_name=config["EMBEDDING_MODEL"])

# Store in ChromaDB (auto-persist)
vector_db = Chroma.from_documents(filtered_chunks, embedding=embeddings_model, persist_directory=chroma_path)

print("\nChromaDB created successfully at:", chroma_path)
print(f"Total Chunks Stored: {len(filtered_chunks)}")

# Get all documents from the database with their metadata
results = vector_db.get()

# Display chunks in a separate window
create_chunks_window(results)
