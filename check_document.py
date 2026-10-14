
import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection(
    name="cybersecurity_intelligence"
)

document_id = "CISA_KEV:CVE-2017-1000486"

result = collection.get(
    ids=[document_id],
    include=["documents", "metadatas"],
)

if not result["ids"]:
    print("Document was not found in Chroma.")
else:
    print("Document ID:", result["ids"][0])
    print("Metadata:", result["metadatas"][0])
    print("Document:", result["documents"][0])
