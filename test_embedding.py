
import ollama

response = ollama.embed(
    model="nomic-embed-text",
    input="A vulnerability allows remote code execution on a server."
)

embedding = response["embeddings"][0]

print("Embedding generated successfully!")
print("Vector dimensions:", len(embedding))
print("First five values:", embedding[:5])
