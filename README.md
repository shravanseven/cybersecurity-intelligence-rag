# Cybersecurity Intelligence RAG

An experiment-driven Retrieval-Augmented Generation (RAG) system for answering cybersecurity questions using information from authoritative public sources.

The project explores how vulnerability intelligence can be ingested, normalized, indexed, and retrieved to support evidence-grounded cybersecurity question answering. The system is being built incrementally using local models and open-source tools, with experiments and architectural decisions documented throughout development.

## Objectives

- Build a RAG pipeline from its fundamental components.
- Ingest and normalize cybersecurity intelligence from public sources.
- Explore semantic and structured retrieval.
- Generate answers grounded in retrieved evidence.
- Evaluate retrieval quality, answer groundedness, and latency.
- Document experiments, architectural decisions, trade-offs, and limitations.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data ingestion, document preparation, and retrieval pipeline |
| NVD CVE API | Initial source of vulnerability intelligence |
| Ollama | Local embedding generation and planned LLM inference |
| `nomic-embed-text` | Generates 768-dimensional text embeddings |
| ChromaDB | Persistent storage and semantic similarity search |
| FastAPI | Planned API layer |
| Lightweight web interface | Planned user interface |

## Architecture

The current implementation follows this pipeline:

1. **Ingestion:** Retrieve a bounded sample of CVE records from the NVD API.
2. **Normalization:** Extract CVE identifiers, English descriptions, and publication timestamps.
3. **Document preparation:** Transform normalized records into retrieval-ready documents with IDs, text, and metadata.
4. **Embedding generation:** Use Ollama and `nomic-embed-text` to convert document text into numerical vectors.
5. **Vector indexing:** Store document IDs, text, metadata, and embeddings in a persistent ChromaDB collection.
6. **Semantic retrieval:** Convert a user query into an embedding and retrieve the nearest CVE documents using cosine distance.

Answer generation, source citations in generated answers, and the application interface have not yet been implemented.

## Current Implementation

### NVD Data Ingestion

The ingestion pipeline retrieves a bounded sample of CVE records from the NVD CVE API v2.0.

For each record, it extracts:

- CVE identifier
- English description, when available
- Publication timestamp

The normalized records are saved in JSONL format at `data/nvd_cves.jsonl`.

Run the ingestion and validation scripts:

```bash
python ingest_nvd.py
python validate_nvd.py
```

The current development sample contains 15 records. It is not a complete NVD dataset.

### CVE Document Preparation

The preparation pipeline transforms normalized CVE records into documents suitable for embedding and retrieval.

Each prepared document contains:

- `id`: CVE identifier used as the document ID.
- `text`: CVE identifier combined with the vulnerability description.
- `metadata`: Publication timestamp and source.

The prepared documents are saved at `data/processed/cve_documents.jsonl`.

Run document preparation and validation:

```bash
python prepare_documents.py
python validate_documents.py
```

Validation checks document structure, required fields, non-empty text, and unique IDs.

### Embeddings and Vector Indexing

The indexing pipeline uses Ollama with `nomic-embed-text` to generate a 768-dimensional embedding for each prepared CVE document.

The embeddings, document text, IDs, and metadata are stored in a persistent ChromaDB collection named `cybersecurity_intelligence`. The collection uses cosine distance for similarity comparisons.

The indexing script uses `upsert`, allowing existing document IDs to be updated without creating duplicate entries for the same IDs.

Build or update the index:

```bash
python index_documents.py
```

Verify the stored documents and embeddings:

```bash
python verify_index.py
```

The current index contains 15 unique CVE documents.

### Semantic Retrieval

The retrieval script accepts a cybersecurity question, generates its embedding using the same model used during indexing, and queries ChromaDB for the three nearest documents.

Run a search:

```bash
python search_cves.py
```

The results include the CVE identifier, description, metadata, and cosine distance.

A lower cosine distance generally indicates greater similarity between vectors. However, distance is not a probability or a guarantee of relevance. The current implementation returns the nearest available documents even when the collection does not contain suitable evidence.

## Initial Retrieval Experiments

Manual tests have been performed using three types of questions:

| Query type | Observation |
|---|---|
| Privilege escalation | Retrieved vulnerabilities describing root-level command execution and privilege escalation. |
| Sendmail vulnerabilities | The top two results explicitly mentioned Sendmail, while a lower-ranked result concerned another utility. |
| Modern quantum encryption | Returned unrelated historical CVEs because the current dataset contains no relevant documents. |

These experiments provide an initial indication that semantic retrieval works, while also demonstrating the limitations of a small dataset and nearest-neighbour search without relevance filtering.

The results are preliminary observations, not a formal retrieval evaluation.

## Development Philosophy

Start with a minimal, working RAG baseline and evaluate it before introducing more sophisticated techniques.

Major architectural changes should be supported by experiments, tests, or explicit reasoning. The implementation is developed incrementally so that individual components can be understood, verified, and evaluated independently.

## Planned Capabilities

- Expand ingestion to additional cybersecurity intelligence sources, including CISA Known Exploited Vulnerabilities (KEV) and vendor security advisories.
- Explore metadata filtering and hybrid retrieval.
- Build a fixed evaluation dataset and measure retrieval quality using metrics such as Recall@K, Precision@K, and MRR.
- Generate evidence-grounded answers using a locally hosted LLM.
- Explore source citations and insufficient-evidence handling.
- Evaluate answer groundedness, relevance, and latency.
- Build a FastAPI backend and lightweight web interface.

## Scope Boundaries

The project is a defensive cybersecurity information retrieval and question-answering system. It is not intended to be a vulnerability scanner, SIEM, automated penetration-testing tool, or autonomous security agent.

## Repository and Local Data

Generated datasets and the local ChromaDB index are development artifacts and should not be committed to Git. The scripts, configuration, documentation, and dependency manifest should be tracked in the repository.

## Documentation

- [Architecture](docs/architecture.md)
- [ChromaDB decision — ADR-001](docs/decisions/ADR-001-chromadb.md)
- [Ollama decision — ADR-002](docs/decisions/ADR-002-ollama.md)

## Project Status

**Current milestone:** Local semantic retrieval baseline implemented.

The pipeline can ingest and validate a small NVD sample, prepare documents, generate embeddings locally, persist them in ChromaDB, and retrieve similar CVE records for a query.

LLM-based answer generation, multi-source ingestion, formal retrieval evaluation, relevance thresholds, and the application interface remain future work. Features and performance claims will be documented after implementation and testing.

## Hybrid Retrieval: Exact CVE Lookup + Semantic Search

### Problem

Initially, the system relied exclusively on semantic similarity to retrieve documents from ChromaDB. This worked for descriptive queries but did not reliably retrieve the requested vulnerability when a query explicitly contained a CVE identifier.

For example, the query `Does CVE-2017-1000486 describe a remote code execution vulnerability?` failed to retrieve the target CVE in the top five results, despite the document existing in the collection.

### Investigation

A diagnostic script compared the target document's stored embedding with a freshly generated embedding from the same Ollama model, `nomic-embed-text`. Their cosine distance was `0.00000000`, indicating that the embeddings matched.

The target CVE ranked first when the query closely matched its descriptive content, but not when the query combined the CVE identifier with a natural-language question.

This indicated that semantic similarity alone was insufficient for reliably resolving explicit vulnerability identifiers.

### Solution

The retrieval pipeline was updated to use a hybrid approach:

1. **CVE identifier detection:** A regular expression detects identifiers such as `CVE-2017-1000486` in the user's query.
2. **Exact lookup:** ChromaDB is queried using the supported document ID formats for NVD and CISA KEV. A metadata lookup is also used as a fallback.
3. **Semantic retrieval:** The query is embedded using `nomic-embed-text`, and ChromaDB returns up to `TOP_K` semantically similar documents.
4. **Result combination:** Exact matches are placed first, followed by semantic results. Duplicate document IDs are removed.

### Query behaviour

- **Query containing a CVE ID:** Exact lookup is performed, followed by semantic search. The exact match is prioritized, and duplicate results are removed.
- **Query without a CVE ID:** The system uses semantic search only, preserving the original retrieval behaviour.

`TOP_K` currently limits the number of semantic results, not the total number of combined results.

### Validation

The updated retrieval pipeline was manually tested with:

- A query explicitly containing `CVE-2017-1000486`.
- A natural-language query about vulnerabilities affecting PrimeFaces.

The target CVE was successfully retrieved first in the exact-identifier case, while the descriptive query continued to return semantic results.

### Design rationale

CVE identifiers are structured keys, whereas embeddings represent semantic similarity. Combining exact lookup with vector search makes retrieval more reliable for known vulnerabilities without sacrificing the ability to discover related documents through natural language.

### Current limitation

Retrieving a document does not by itself guarantee that a generated answer will be correct or fully supported by the evidence. Grounded answer generation, source citations, insufficient-evidence handling, and systematic evaluation remain separate tasks in the project roadmap.