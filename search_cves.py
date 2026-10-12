
import chromadb
import ollama


DB_PATH = "chroma_db"
COLLECTION_NAME = "cybersecurity_intelligence"
EMBEDDING_MODEL = "nomic-embed-text"
TOP_K = 3


def main():
    # 1. Connect to the existing ChromaDB collection
    try:
        client = chromadb.PersistentClient(path=DB_PATH)
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as error:
        print("Could not access the ChromaDB collection.")
        print("Run index_documents.py first to create the index.")
        print("Details:", error)
        return

    if collection.count() == 0:
        print("The collection is empty. Index some documents first.")
        return

    # 2. Get a question from the user
    query = input("Ask a cybersecurity question: ").strip()

    if not query:
        print("Please enter a question.")
        return

    # 3. Convert the question into an embedding
    try:
        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input=query,
        )
        query_embedding = response["embeddings"][0]
    except Exception as error:
        print("Could not generate the query embedding.")
        print("Check that Ollama is running and the embedding model is available.")
        print("Details:", error)
        return

    # 4. Search ChromaDB for similar documents
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(TOP_K, collection.count()),
            include=["documents", "metadatas", "distances"],
        )
    except Exception as error:
        print("The vector search failed.")
        print("Details:", error)
        return

    # 5. Display results in ChromaDB's returned order
    print("\nSearch results:")

    for i, cve_id in enumerate(results["ids"][0], start=1):
        print(f"\n{i}. {cve_id}")
        print("Text:", results["documents"][0][i - 1])
        print("Metadata:", results["metadatas"][0][i - 1])
        print("Cosine distance:", results["distances"][0][i - 1])


if __name__ == "__main__":
    main()
