import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Load environment variables
load_dotenv()

# Load the ChromaDB
persist_directory = "chroma_db"

# Define your embedding model (same as used during storage)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load the database
vector_db = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)

# Fetch all vectors
ids = vector_db.get(include=["documents", "embeddings"])

# Ensure embeddings exist
if not ids['embeddings']:
    print("No embeddings found. Please check the ChromaDB data.")
    exit()


# Function to plot the vectors using PCA for dimensionality reduction
def plot_vectors():
    embeddings = np.array(ids['embeddings'])
    pca = PCA(n_components=2)  # Reduce to 2 dimensions for visualization
    reduced_embeddings = pca.fit_transform(embeddings)

    # Plot the vectors in 2D space
    plt.figure(figsize=(10, 8))
    plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], color='blue')

    # Annotate each point with the document's name or ID
    for i, vector_id in enumerate(ids['ids']):
        plt.annotate(f'{vector_id}', (reduced_embeddings[i, 0], reduced_embeddings[i, 1]), fontsize=8, alpha=0.7)

    plt.title('Vector Embeddings in 2D Space (PCA)')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.show()


# Main code for plotting vectors
if __name__ == "__main__":
    print("Plotting vector embeddings in 2D...")
    plot_vectors()
