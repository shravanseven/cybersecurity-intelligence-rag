
import math
import chromadb
import ollama

DB_PATH = "chroma_db"
COLLECTION_NAME = "cybersecurity_intelligence"
MODEL = "nomic-embed-text"

TARGET_ID = "CISA_KEV:CVE-2017-1000486"

QUERIES = [
    "CVE-2017-1000486",
    "Does CVE-2017-1000486 describe a remote code execution vulnerability?",
    "Primetek Primefaces weak encryption flaw resulting in remote code execution",
]


def cosine_distance(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        raise ValueError("Cannot compare a zero-length vector.")

    return 1 - (dot / (norm_a * norm_b))


client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection(name=COLLECTION_NAME)

target = collection.get(
    ids=[TARGET_ID],
    include=["documents", "metadatas", "embeddings"],
)

if not target["ids"]:
    raise ValueError(f"Target document not found: {TARGET_ID}")

stored_text = target["documents"][0]
stored_embedding = target["embeddings"][0].tolist()

print("Target ID:", TARGET_ID)
print("Stored document:", stored_text)
print("Stored embedding dimensions:", len(stored_embedding))

# Check whether the current embedding model reproduces
# the embedding stored in Chroma.
doc_response = ollama.embed(
    model=MODEL,
    input=stored_text,
)
fresh_doc_embedding = doc_response["embeddings"][0]

print(
    "\nDistance between stored and freshly generated "
    "document embeddings:",
    f"{cosine_distance(stored_embedding, fresh_doc_embedding):.8f}",
)

# Compare each query vector with the target document vector.
for query in QUERIES:
    response = ollama.embed(model=MODEL, input=query)
    query_embedding = response["embeddings"][0]

    distance = cosine_distance(query_embedding, stored_embedding)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=["distances"],
    )

    result_ids = results["ids"][0]
    target_rank = (
        result_ids.index(TARGET_ID) + 1
        if TARGET_ID in result_ids
        else None
    )

    print("\n" + "-" * 65)
    print("Query:", query)
    print("Distance to target document:", f"{distance:.4f}")
    print("Target in top 5:", target_rank or "No")
    print("Top 5 IDs:", result_ids)
