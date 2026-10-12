
import json
import os

import chromadb
import ollama


INPUT_PATH = "data/processed/cve_documents.jsonl"
DB_PATH = "chroma_db"
COLLECTION_NAME = "cybersecurity_intelligence"
EMBEDDING_MODEL = "nomic-embed-text"


def main():
    # 1. Load the prepared CVE documents
    with open(INPUT_PATH, "r", encoding="utf-8") as file:
        documents = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    if not documents:
        raise ValueError("No documents found in the input file.")

    # 2. Generate embeddings using Ollama
    texts = [document["text"] for document in documents]

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    embeddings = response["embeddings"]

    if len(embeddings) != len(documents):
        raise ValueError("Number of embeddings does not match documents.")

    # 3. Open (or create) the persistent ChromaDB database
    os.makedirs(DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_PATH)

    # Use cosine distance to compare embedding vectors
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # 4. Store IDs, text, metadata, and embeddings
    ids = [document["id"] for document in documents]
    texts = [document["text"] for document in documents]

    metadatas = [
        {
            key: value
            for key, value in document["metadata"].items()
            if value is not None
        }
        for document in documents
    ]

    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    # 5. Verify the index
    print("Documents processed:", len(documents))
    print("Collection name:", collection.name)
    print("Documents in collection:", collection.count())

    sample = collection.get(
        ids=[ids[0]],
        include=["documents", "metadatas"],
    )

    print("\nSample stored document:")
    print("ID:", sample["ids"][0])
    print("Text:", sample["documents"][0])
    print("Metadata:", sample["metadatas"][0])


if __name__ == "__main__":
    main()
