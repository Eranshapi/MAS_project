import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np
from scipy.spatial.distance import cosine

# Load environment variables
load_dotenv()

# Load the ChromaDB
persist_directory = r"C:\Users\erans\.cursor\MAS_Project\chroma_db"

# Define your embedding model (same as used during storage)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

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
    print(f"Cosine Distance between ID {id_1 + 1} and ID {id_2 + 1}: {distance}")

# Function for manual search (query-based similarity search)
def manual_search(query_text, k=3):
    results = vector_db.similarity_search(query_text, k=k)
    print(f"Top {k} Results for Query: '{query_text}'")
    print("=" * 80)
    for i, doc in enumerate(results):
        print(f"Result {i + 1}:")
        print(f"Text: {doc.page_content}")
        print("-" * 40)

# Main code
if __name__ == "__main__":
    print("Choose an option from 0 to 4:")
    print("0. Exit")
    print("1. Display vector information")
    print("2. Compare two vectors by ID (Cosine distance)")
    print("3. Manual search (query-based)")
    print("4. Display all vector IDs and associated descriptions")

    option = input("Enter option number (0-4): ")

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
    else:
        print("Invalid option. Please choose a valid option (0-4).")
