
import chromadb

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_collection(
    name="cybersecurity_intelligence"
)

result = collection.get(
    limit=1,
    include=["embeddings", "documents", "metadatas"],
)

print("Total documents:", collection.count())
print("Sample ID:", result["ids"][0])
print("Stored text:", result["documents"][0])
print("Metadata:", result["metadatas"][0])
print("Embedding dimensions:", len(result["embeddings"][0]))
