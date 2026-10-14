
import json
import chromadb
import ollama


# Configuration
DB_PATH = "chroma_db"
COLLECTION_NAME = "cybersecurity_intelligence"
EMBEDDING_MODEL = "nomic-embed-text"
EVALUATION_FILE = "evaluation_queries.json"
TOP_K = 5


def load_evaluation_queries():
    """Load manually labeled evaluation queries."""
    with open(EVALUATION_FILE, "r", encoding="utf-8") as file:
        queries = json.load(file)

    if not queries:
        raise ValueError("The evaluation dataset is empty.")

    return queries


def retrieve_documents(collection, query):
    """Embed a query and retrieve its top-K documents."""
    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=query,
    )

    query_embedding = response["embeddings"][0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(TOP_K, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []

    for i, document_id in enumerate(results["ids"][0]):
        retrieved.append({
            "id": document_id,
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i] or {},
            "distance": results["distances"][0][i],
        })

    return retrieved


def evaluate_query(test_case, retrieved):
    """Compare retrieved IDs with the expected relevant IDs."""
    expected_ids = set(test_case["expected_ids"])
    retrieved_ids = [item["id"] for item in retrieved]

    relevant_found = expected_ids.intersection(retrieved_ids)

    print("\n" + "=" * 75)
    print("Query:", test_case["query"])
    print("Type:", test_case["type"])
    print("Expected IDs:", sorted(expected_ids) or "None specified")

    print("\nRetrieved results:")

    if not retrieved:
        print("No documents returned.")

    for rank, item in enumerate(retrieved, start=1):
        is_relevant = item["id"] in expected_ids
        status = "EXPECTED MATCH" if is_relevant else "NOT IN LABELS"

        print(f"\nRank: {rank}")
        print(f"ID: {item['id']}")
        print(f"Distance: {item['distance']:.4f}")
        print(f"Label: {status}")
        print(f"Document: {item['document'][:300]}")

    # Unanswerable cases require separate assessment.
    if test_case["type"] == "unanswerable":
        print("\nUnanswerable-query check:")
        print("Candidates returned:", len(retrieved))
        print(
            "Review the candidates to determine whether any actually "
            "answers the question."
        )

        return None

    # Basic metrics for answerable queries.
    hit = int(bool(relevant_found))
    recall = len(relevant_found) / len(expected_ids) if expected_ids else 0

    # This precision treats documents not in expected_ids as non-relevant.
    # It is provisional until all top results have relevance judgments.
    precision = (
        len(relevant_found) / len(retrieved)
        if retrieved
        else 0
    )

    print("\nMetrics:")
    print(f"Hit@{TOP_K}: {hit}")
    print(f"Recall@{TOP_K}: {recall:.2f}")
    print(f"Labeled Precision@{TOP_K}: {precision:.2f}")

    return {
        "hit": hit,
        "recall": recall,
        "precision": precision,
    }


def main():
    # Connect to the existing index.
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)

    if collection.count() == 0:
        raise ValueError("The Chroma collection is empty.")

    test_cases = load_evaluation_queries()

    print("Collection:", COLLECTION_NAME)
    print("Indexed documents:", collection.count())
    print("Evaluation queries:", len(test_cases))
    print("Top K:", TOP_K)

    metrics = []

    for test_case in test_cases:
        retrieved = retrieve_documents(
            collection,
            test_case["query"],
        )

        result = evaluate_query(test_case, retrieved)

        if result is not None:
            metrics.append(result)

    print("\n" + "=" * 75)
    print("OVERALL RESULTS")

    if metrics:
        print(
            f"Average Hit@{TOP_K}: "
            f"{sum(m['hit'] for m in metrics) / len(metrics):.2f}"
        )
        print(
            f"Average Recall@{TOP_K}: "
            f"{sum(m['recall'] for m in metrics) / len(metrics):.2f}"
        )
        print(
            f"Average Labeled Precision@{TOP_K}: "
            f"{sum(m['precision'] for m in metrics) / len(metrics):.2f}"
        )

    print(
        "\nNote: These are preliminary results from a small, "
        "manually labeled dataset."
    )


if __name__ == "__main__":
    main()
