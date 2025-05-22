# test_chunking.py

import os
from database import db
from langchain_community.vectorstores import Chroma


# Helper function to simulate chunked data (replace with actual data if needed)
def test_chunking_data():
    """
    Simulate a chunked document. For testing purposes, we'll mock data as chunks.
    Replace this with actual text data if testing with a live DB.
    """
    chunks = [
        "This is a chunk with information about the first topic. It should not be cut in the middle of a sentence.",
        "This chunk talks about the second topic. It has additional details to follow.",
        "Another chunk related to a different section of the document. Important context is here.",
        "Final chunk which will provide concluding remarks for this document's content."
    ]
    return chunks


# 1. Testing if query is giving meaningful results.
def test_query_database():
    print("\n--- Testing Query with Chunk Retrieval ---")

    # Example query for testing (adjust as per your context)
    query = "Tell me about the second topic."
    print(f"\nQuery: {query}\n")

    # Get chunks from the database (replace with real query_database function if DB is set)
    results = db.query(query)

    # Print results for inspection
    print("Retrieved Chunks:\n")
    for idx, result in enumerate(results):
        print(f"Result {idx + 1}:\n{result}\n{'-' * 50}")

    if len(results) == 0:
        print("No relevant chunks were found. Please review chunking logic.")


# 2. Ensuring chunking is happening logically (for example, no mid-sentence cutting).
def test_chunking_logic():
    print("\n--- Testing Chunking Logic ---")

    chunks = test_chunking_data()  # Replace with actual chunking process if running live

    # Check chunking integrity
    for i, chunk in enumerate(chunks):
        if "." in chunk and not chunk.endswith("."):
            print(f"Warning: Chunk {i + 1} might be incomplete, not ending with a full sentence: {chunk}")

    print("\nChunk Integrity Check Completed.")


# Main function to run all tests
if __name__ == "__main__":
    print("Running Chunking and Query Testing...\n")

    # Test chunk retrieval from the database
    test_query_database()

    # Test if chunking happens logically (no mid-sentence cuts)
    test_chunking_logic()

    print("\nTesting Complete.")
