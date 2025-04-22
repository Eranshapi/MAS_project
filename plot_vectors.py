# visualize_vectors.py

# Optional: uncomment this if your plot silently crashes
# import matplotlib
# matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
# from sklearn.manifold import TSNE  # Optional, if you prefer t-SNE
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Config
CHROMA_PATH = "chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
NUM_POINTS = 200  # Limit for visualization

# Load vector DB
embedding_function = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

# Extract all documents
docs = vector_db.get(include=["embeddings", "documents", "metadatas"])

embeddings = docs["embeddings"]
texts = docs["documents"]

print(f"Loaded {len(embeddings)} embeddings from Chroma.")

# Limit to first N for clarity
embeddings = embeddings[:NUM_POINTS]
texts = texts[:NUM_POINTS]

# Dimensionality reduction
pca = PCA(n_components=2)
coords = pca.fit_transform(embeddings)

# Optional: t-SNE instead of PCA
# from sklearn.manifold import TSNE
# tsne = TSNE(n_components=2, perplexity=30, random_state=42)
# coords = tsne.fit_transform(embeddings)

# Plotting
plt.figure(figsize=(12, 8))
plt.scatter(coords[:, 0], coords[:, 1], alpha=0.7, c='lightblue', edgecolors='black')

# Annotate with reversed & shortened preview
for i, txt in enumerate(texts):
    try:
        preview = txt.replace("\n", " ").strip()[:25][::-1] + "…"  # Reverse + truncate
        plt.annotate(preview, (coords[i, 0], coords[i, 1]), fontsize=7, alpha=0.6)
    except Exception as e:
        print(f"[ANNOTATION ERROR] Index {i}: {e}")

plt.title("2D Visualization of Document Embeddings (PCA)")
plt.xlabel("Component 1")
plt.ylabel("Component 2")
plt.grid(True)
plt.tight_layout()

print("Displaying plot...")
plt.show()
