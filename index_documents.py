
import json
import os

import chromadb
import ollama


INPUT_PATHS = [
    "data/processed/cve_documents.jsonl",
    "data/processed/kev_documents.jsonl",
]

DB_PATH = "chroma_db"
COLLECTION_NAME = "cybersecurity_intelligence"
EMBEDDING_MODEL = "nomic-embed-text"
BATCH_SIZE = 64


def load_documents():
    documents = []

    for path in INPUT_PATHS:
        with open(path, "r", encoding="utf-8") as file:
            source_documents = [
                json.loads(line)
                for line in file
                if line.strip()
            ]

        print(f"Loaded {len(source_documents)} documents from {path}")
        documents.extend(source_documents)

    if not documents:
        raise ValueError("No prepared documents found.")

    ids = [document["id"] for document in documents]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate document IDs found across input files.")

    return documents


def main():
    # 1. Load the prepared documents from both sources
    documents = load_documents()

    # 2. Open the existing persistent ChromaDB collection
    os.makedirs(DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    print("\nDocuments to index:", len(documents))
    print("Existing collection count:", collection.count())

    # 3. Generate embeddings and upsert documents in batches
    for start in range(0, len(documents), BATCH_SIZE):
        batch = documents[start:start + BATCH_SIZE]

        texts = [document["text"] for document in batch]

        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input=texts,
        )

        embeddings = response["embeddings"]

        if len(embeddings) != len(batch):
            raise ValueError(
                f"Embedding count mismatch in batch starting at {start}."
            )

        metadatas = [
            {
                key: value
                for key, value in document["metadata"].items()
                if value is not None
            }
            for document in batch
        ]

        collection.upsert(
            ids=[document["id"] for document in batch],
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        processed = start + len(batch)
        print(f"Processed {processed}/{len(documents)} documents")

    # 4. Verify the resulting index
    print("\nIndexing complete.")
    print("Collection name:", collection.name)
    print("Total documents in collection:", collection.count())

    sample = collection.get(
        ids=["CISA_KEV:CVE-2015-5477"],
        include=["documents", "metadatas"],
    )

    if sample["ids"]:
        print("\nSample KEV document in ChromaDB:")
        print("ID:", sample["ids"][0])
        print("Text:", sample["documents"][0])
        print("Metadata:", sample["metadatas"][0])
    else:
        raise RuntimeError("Sample KEV document was not found in the index.")


if __name__ == "__main__":
    main()
