# Initial Architecture

## 1. Purpose

Build a cybersecurity intelligence RAG system that retrieves evidence from public cybersecurity sources and uses a locally hosted LLM to produce useful, source-backed answers.

## 2. Core Principles

1. Authoritative sources take precedence over model memory.
2. Answers should be supported by retrieved evidence.
3. The system should acknowledge insufficient evidence rather than invent facts.
4. Structured queries should use structured data when appropriate.
5. Retrieval improvements must be evaluated.
6. Architectural decisions and trade-offs must be documented.

## 3. Initial Sources

* NVD vulnerability records
* CISA Known Exploited Vulnerabilities (KEV) catalog
* Vendor security advisories

Source integration will be incremental. NVD will be the first ingestion target.

## 4. Initial Technology Stack

| Component         | Initial choice            | Rationale                              |
| ----------------- | ------------------------- | -------------------------------------- |
| Language          | Python                    | Core application and data processing   |
| Vector store      | ChromaDB                  | Local development and vector retrieval |
| Local LLM runtime | Ollama                    | Local model experimentation            |
| API               | FastAPI                   | Python-based HTTP interface            |
| UI                | Lightweight web interface | Simple user interaction                |
| Version control   | Git                       | Traceable development history          |

The embedding model, generation model, chunking parameters, and evaluation tooling remain experimental decisions.

## 5. Initial RAG Flow

1. Receive a user question.
2. Convert the question into an embedding.
3. Retrieve relevant chunks from ChromaDB.
4. Construct context from retrieved evidence.
5. Send the question and context to Ollama.
6. Return the answer with source references.
7. Indicate when the retrieved evidence is insufficient.

## 6. Data Ingestion Flow

1. Fetch public-source data.
2. Preserve raw source data where practical.
3. Parse and validate records.
4. Normalize common metadata.
5. Convert relevant textual content into documents.
6. Chunk documents when appropriate.
7. Generate embeddings.
8. Store searchable representations and source metadata.

Structured fields will be retained for precise lookups and filters. Embeddings will support semantic retrieval over descriptive text.

## 7. Retrieval Evolution

* V1: dense vector retrieval.
* V2: metadata filtering.
* V3: hybrid semantic and keyword retrieval.
* V4: reranking, if evaluation demonstrates a benefit.

These are planned stages, not claims that the features already exist.

## 8. Evaluation

Create a fixed evaluation dataset with questions covering direct lookup, affected products, exploitation status, mitigation, multi-source questions, comparisons, and insufficient-evidence cases.

Potential metrics include Recall@K, Precision@K, MRR, answer correctness, groundedness, and latency.

The evaluation harness will be separate from the normal user query path. Results will guide retrieval changes.

## 9. Initial Repository Boundaries

The initial repository contains documentation, configuration templates, and tests. Application modules will be added as the corresponding implementation phases begin.

## 10. Current Limitations

* No ingestion pipeline implemented yet.
* No embeddings or vector index created yet.
* No LLM integration implemented yet.
* No evaluation baseline measured yet.
* No web interface implemented yet.

## 11. Deferred Scope

Complex agents, knowledge graphs, evidence-confidence scoring, security-hardening experiments, automated threat hunting, and elaborate UI features are outside the initial implementation scope.

## 12. Change Management

Significant architecture changes should be documented in an Architecture Decision Record (ADR) and, where applicable, supported by a reproducible experiment.

The architecture document must reflect the actual implementation as the project evolves.
