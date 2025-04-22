# store_db.py
from extract_text import extract_text_from_folder
from preprocess import split_text_into_chunks
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

# Define your document source directory
data_path = "docs"
chroma_path = "chroma_db"

# Extract documents using your text extraction functions (ensure this returns a list of plain text strings)
text_data = extract_text_from_folder(data_path)

# Check the format of the extracted documents (print to inspect the result)
print(f"Extracted {len(text_data)} documents.")
for i, doc in enumerate(text_data[:3]):
    print(f"Document {i + 1}: Type: {type(doc)}, Content: {str(doc['text'])[:100]}...")  # Preview type and first 100 characters

# Preprocess and chunk the text data
documents = [doc['text'] for doc in text_data]  # Extract the 'text' from each document
chunks = split_text_into_chunks(documents, chunk_size=500, overlap=50)

# Debugging: Print the number of chunks stored
print(f"Total Chunks Stored: {len(chunks)}")

# Debugging: Preview the first 5 chunks (if any)
for i, chunk in enumerate(chunks[:5]):
    print(f"Chunk {i+1}: {chunk.page_content[:150]}...")  # Preview the first 150 characters of each chunk

# Initialize HuggingFace Embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Store to vector DB with persistence directory
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=chroma_path
)

# If you want to force saving (optional)
if hasattr(vector_db, "_persist"):
    vector_db._persist()

print(f"ChromaDB created at: {chroma_path}")

