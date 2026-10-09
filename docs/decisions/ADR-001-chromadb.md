# ADR-001: Use ChromaDB for the Initial Vector Store

* **Status:** Accepted for the initial implementation
* **Date:** 2026-10-09

## Context

The project needs a vector store for embeddings and semantic retrieval. The initial objective is to understand and evaluate the RAG pipeline without introducing unnecessary infrastructure.

## Options Considered

* ChromaDB
* FAISS
* Qdrant
* PostgreSQL with pgvector

## Decision

Use ChromaDB for the initial implementation.

## Rationale

ChromaDB provides a convenient local development experience and supports vector search and metadata. This allows us to focus on ingestion, embeddings, retrieval, and evaluation.

## Trade-offs

* Another vector store may be more appropriate for a production deployment.
* Storage and retrieval behavior must be measured rather than assumed.
* The initial choice does not establish that ChromaDB will be optimal for every workload.

## Reconsideration Criteria

Revisit this decision if experiments or deployment requirements reveal limitations in filtering, performance, persistence, operational complexity, or scale.

## Validation Plan

Implement baseline retrieval and measure retrieval quality and latency before considering migration.
