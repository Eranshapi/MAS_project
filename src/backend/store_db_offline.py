"""
Parent-Document Retrieval Database Store (Offline Version)

This module implements a Parent-Document Retrieval architecture where:
- Child chunks are stored in ChromaDB vector store for precise similarity search
- Parent chunks are stored in LocalFileStore for context retrieval
- Children link to parents via unique parent_id in metadata

Author: Senior Database Engineer
"""

import os
import sys
import shutil
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path when running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.backend.parent_child_chunker import process_documents_directory
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.storage import LocalFileStore
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from src.utils.config import load_config

# Load environment variables and config
load_dotenv()
config = load_config()

# Paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_path = os.path.join(project_root, "docs")
vector_child_path = config["VECTOR_CHILD_DB_PATH"]
parent_store_path = config["PARENT_STORE_PATH"]
models_dir = os.path.join(project_root, "models")

# Ensure directories exist
os.makedirs(models_dir, exist_ok=True)
os.makedirs(os.path.dirname(vector_child_path), exist_ok=True)
os.makedirs(parent_store_path, exist_ok=True)

# Model configuration
model_name = config["EMBEDDING_MODEL"]
# Create a safe directory name from the model ID
model_dir_name = model_name.replace("/", "_")
local_model_path = os.path.join(models_dir, model_dir_name)

# Check if model exists locally, if not download it
if not os.path.exists(local_model_path):
    print(f"Model not found locally at {local_model_path}")
    print(f"Downloading {model_name} for offline use...")
    try:
        model = SentenceTransformer(model_name)
        model.save(local_model_path)
        print(f"Model saved to {local_model_path}")
    except Exception as e:
        print(f"Error downloading model: {e}")
        sys.exit(1)
else:
    print(f"Using existing local model at {local_model_path}")


def clear_existing_stores():
    """Clear existing vector and parent stores for fresh rebuild."""
    if os.path.exists(vector_child_path):
        print(f"Deleting existing vector store at {vector_child_path}")
        shutil.rmtree(vector_child_path)
    
    if os.path.exists(parent_store_path):
        print(f"Deleting existing parent store at {parent_store_path}")
        shutil.rmtree(parent_store_path)
    
    # Recreate directories
    os.makedirs(vector_child_path, exist_ok=True)
    os.makedirs(parent_store_path, exist_ok=True)


def store_parent_documents(parent_chunks, store_path):
    """
    Store parent documents in LocalFileStore.
    
    Args:
        parent_chunks: List of parent Document objects with parent_id in metadata
        store_path: Path to the LocalFileStore directory
        
    Returns:
        LocalFileStore instance
    """
    parent_store = LocalFileStore(store_path)
    
    for parent in parent_chunks:
        parent_id = parent.metadata.get('parent_id')
        if parent_id:
            # Serialize the document as JSON
            doc_data = {
                'page_content': parent.page_content,
                'metadata': parent.metadata
            }
            # Store as bytes (LocalFileStore requires bytes)
            parent_store.mset([(parent_id, json.dumps(doc_data).encode('utf-8'))])
    
    print(f"Stored {len(parent_chunks)} parent documents in {store_path}")
    return parent_store


def get_parent_by_id(parent_store, parent_id):
    """
    Retrieve a parent document by its ID.
    
    Args:
        parent_store: LocalFileStore instance
        parent_id: The unique ID of the parent document
        
    Returns:
        Dictionary with 'page_content' and 'metadata', or None if not found
    """
    result = parent_store.mget([parent_id])
    if result and result[0]:
        return json.loads(result[0].decode('utf-8'))
    return None


def create_vector_store_for_children(child_chunks, embeddings_model, store_path):
    """
    Create ChromaDB vector store for child chunks.
    
    Args:
        child_chunks: List of child Document objects
        embeddings_model: HuggingFaceEmbeddings instance
        store_path: Path for ChromaDB persistence
        
    Returns:
        Chroma vector store instance
    """
    # Initialize ChromaDB client with telemetry disabled
    client = chromadb.PersistentClient(
        path=store_path,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Filter out empty chunks
    filtered_chunks = [chunk for chunk in child_chunks if chunk.page_content.strip()]
    
    print(f"Creating ChromaDB with {len(filtered_chunks)} child chunks...")
    
    vector_db = Chroma.from_documents(
        documents=filtered_chunks,
        embedding=embeddings_model,
        client=client,
        collection_metadata={"hnsw:batch_size": 1000}
    )
    
    return vector_db


def main():
    """Main function to process documents and build Parent-Document Retrieval stores."""
    print("=" * 60)
    print("Parent-Document Retrieval Database Builder")
    print("=" * 60)
    
    # Clear existing stores
    clear_existing_stores()
    
    # Step 1: Process documents using parent-child chunker
    print("\n[Step 1] Processing documents with Parent-Child Chunking...")
    result = process_documents_directory(
        directory_path=data_path,
        parent_chunk_size=2000,
        parent_chunk_overlap=200,
        child_chunk_size=400,
        child_chunk_overlap=50,
    )
    
    parent_chunks = result['parent_chunks']
    child_chunks = result['child_chunks']
    parent_child_mapping = result['parent_child_mapping']
    stats = result['stats']
    
    if not parent_chunks:
        print("No documents found to process. Exiting.")
        sys.exit(0)
    
    # Step 2: Initialize embeddings model
    print(f"\n[Step 2] Initializing embeddings with local model: {local_model_path}")
    embeddings_model = HuggingFaceEmbeddings(model_name=local_model_path)
    
    # Step 3: Store parent documents in LocalFileStore
    print(f"\n[Step 3] Storing parent documents in LocalFileStore...")
    parent_store = store_parent_documents(parent_chunks, parent_store_path)
    
    # Step 4: Create vector store for child chunks
    print(f"\n[Step 4] Creating vector store for child chunks...")
    vector_db = create_vector_store_for_children(
        child_chunks, 
        embeddings_model, 
        vector_child_path
    )
    
    # Step 5: Verify and display results
    print("\n" + "=" * 60)
    print("Database Creation Complete!")
    print("=" * 60)
    print(f"\nStatistics:")
    print(f"  - Total documents processed: {stats['total_documents']}")
    print(f"  - Parent chunks stored: {stats['total_parent_chunks']}")
    print(f"  - Child chunks vectorized: {stats['total_child_chunks']}")
    print(f"  - Avg children per parent: {stats['avg_children_per_parent']:.2f}")
    print(f"\nStorage Locations:")
    print(f"  - Vector store (children): {vector_child_path}")
    print(f"  - Document store (parents): {parent_store_path}")
    
    # Verify retrieval works
    print("\n" + "-" * 60)
    print("Verification: Testing parent-child linking...")
    
    # Get a sample child and verify its parent can be retrieved
    if child_chunks:
        sample_child = child_chunks[0]
        sample_parent_id = sample_child.metadata.get('parent_id')
        
        if sample_parent_id:
            retrieved_parent = get_parent_by_id(parent_store, sample_parent_id)
            if retrieved_parent:
                print(f"✓ Successfully retrieved parent for child (parent_id: {sample_parent_id[:8]}...)")
                print(f"  Child preview: {sample_child.page_content[:80]}...")
                print(f"  Parent preview: {retrieved_parent['page_content'][:80]}...")
            else:
                print(f"✗ Failed to retrieve parent for parent_id: {sample_parent_id}")
        else:
            print("✗ Sample child has no parent_id in metadata")
    
    # Get vector DB stats
    results = vector_db.get(include=['documents', 'metadatas'])
    print(f"\n✓ Vector DB contains {len(results['documents'])} child documents")
    
    print("\n" + "=" * 60)
    print("Parent-Document Retrieval system ready!")
    print("=" * 60)


if __name__ == "__main__":
    main()
