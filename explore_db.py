import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np
from scipy.spatial.distance import cosine

# Load environment variables
load_dotenv()

# Load the ChromaDB
persist_directory = "chroma_db"

# Define your embedding model (same as used during storage)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Load the database
vector_db = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)

# Fetch all IDs
collection = vector_db._collection
ids = collection.get(include=["documents", "embeddings"])

print(f"Total Vectors in DB: {len(ids['ids'])}")
print("=" * 80)


# Function to display the vector information
def display_vector_info():
    for i, vector_id in enumerate(ids['ids']):
        print(f"ID {i + 1}: {vector_id}")
        print("-" * 40)
        print(f"Vector Values (truncated): {ids['embeddings'][i][:10]}...")  # First 10 numbers for readability
        print(f"Description / Original Text: {ids['documents'][i]}")
        print("=" * 80)


# Function to compare two vectors by cosine distance
def compare_vectors(id_1, id_2):
    # Get embeddings for the given IDs
    vector_1 = np.array(ids['embeddings'][id_1])
    vector_2 = np.array(ids['embeddings'][id_2])

    # Calculate cosine similarity (distance)
    distance = cosine(vector_1, vector_2)
    print(f"Cosine Distance between ID {id_1 + 1} and ID {id_2 + 1}: {distance:.4f}")


# Function for manual search (query-based similarity search)
def manual_search(query_text, k=3):
    # Retrieve the k most similar documents based on the query
    results = vector_db.similarity_search(query_text, k=k)
    print(f"Top {k} Results for Query: '{query_text}'")
    print("=" * 80)
    for i, doc in enumerate(results):
        print(f"Result {i + 1}:")
        print(f"Text: {doc.page_content}")
        print("-" * 40)


# Function to compare cosine similarity between adjacent chunks (contexts)
def compare_adjacent_chunks():
    # Compare all adjacent chunks
    for i in range(len(ids['ids']) - 1):  # Loop through all vectors except the last one
        print(f"Comparing chunk {i + 1} (ID: {i + 1}) with chunk {i + 2} (ID: {i + 2})")

        # Get the text (or description) of the chunks being compared
        chunk_1_text = ids['documents'][i]  # Text of the first chunk
        chunk_2_text = ids['documents'][i + 1]  # Text of the second chunk

        # Print the chunk descriptions
        print(
            f"Chunk {i + 1} (ID: {i + 1}): {chunk_1_text[:100]}...")  # Display first 100 characters of the chunk for readability
        print(f"Chunk {i + 2} (ID: {i + 2}): {chunk_2_text[:100]}...")
        print("-" * 40)

        # Compare the vectors
        compare_vectors(i, i + 1)


# Main code
if __name__ == "__main__":

    print("Choose an option from 0 to 5:")
    print("0. Exit")
    print("1. Display vector information")
    print("2. Compare two vectors by ID (Cosine distance)")
    print("3. Manual search (query-based)")
    print("4. Display all vector IDs and associated descriptions")
    print("5. Compare adjacent vectors for similarity")

    option = input("Enter option number (0-5): ")

    if option == "0":
        print("Exiting the program. Goodbye!")
    elif option == "1":
        print("Displaying vector information from the ChromaDB...")
        display_vector_info()
    elif option == "2":
        id_1 = int(input("Enter the first ID to compare (1-indexed): ")) - 1
        id_2 = int(input("Enter the second ID to compare (1-indexed): ")) - 1
        print("Comparing vectors...")
        compare_vectors(id_1, id_2)
    elif option == "3":
        query = input("Enter your search query: ")
        print("Performing manual search...")
        manual_search(query)
    elif option == "4":
        print("Displaying all vector IDs and their associated descriptions...")
        display_vector_info()
    elif option == "5":
        print("Comparing adjacent vectors for similarity...")
        compare_adjacent_chunks()
    else:
        print("Invalid option. Please choose a valid option (0-5).")
