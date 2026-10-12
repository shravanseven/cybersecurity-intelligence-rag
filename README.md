# Cybersecurity Intelligence RAG

An experiment-driven Retrieval-Augmented Generation (RAG) system for answering cybersecurity questions using information from authoritative public sources.

The system will combine structured vulnerability intelligence with textual security advisories, retrieve relevant evidence, and generate answers with source citations using a locally hosted LLM.

## Objectives

* Build a RAG pipeline from its fundamental components.
* Ingest and normalize multiple cybersecurity intelligence sources.
* Explore structured and semantic retrieval.
* Generate answers grounded in retrieved evidence.
* Evaluate retrieval quality, answer groundedness, and latency.
* Document experiments, architectural decisions, and trade-offs.

## Initial Data Sources

* **NVD:** vulnerability records and related metadata.
* **CISA KEV:** known exploited vulnerability information.
* **Vendor security advisories:** product-specific impact and remediation guidance.

## Initial Technology Choices

* Python
* ChromaDB
* Ollama
* FastAPI
* A lightweight web interface

Specific embedding and generation models will be selected after local compatibility and quality experiments.

## Development Philosophy

Start with a minimal, working RAG baseline. Evaluate it before introducing more sophisticated retrieval techniques.

Major changes should be supported by experiments, tests, or explicit architectural reasoning.

## Current Status

**Phase 0 — Project foundation**

The repository and development environment are being established. Data ingestion and RAG implementation have not started yet.

## Planned Capabilities

* Public-source ingestion and normalization
* Vector embeddings and semantic retrieval
* Metadata filtering and hybrid retrieval
* Local LLM-based answer generation
* Source citations and insufficient-evidence handling
* Evaluation dataset and regression testing
* FastAPI backend and simple web interface

## Scope Boundaries

The initial project is a defensive cybersecurity information retrieval and question-answering system. It is not a vulnerability scanner, SIEM, automated penetration-testing tool, or autonomous security agent.

## Documentation

* [Architecture](docs/architecture.md)
* [ChromaDB decision](docs/decisions/ADR-001-chromadb.md)
* [Ollama decision](docs/decisions/ADR-002-ollama.md)

## Project Status

Early development. Features, evaluation results, and performance claims will be documented only after they have been implemented and tested.



## NVD Data Ingestion

The initial ingestion pipeline retrieves a bounded sample of CVE
records from the NVD CVE API v2.0.

For each record, it extracts:
- CVE identifier
- English description, when available
- Publication timestamp

The records are normalized and saved locally in JSONL format at
`data/nvd_cves.jsonl`.

### Run the pipeline

```bash
python ingest_nvd.py
python validate_nvd.py
```

The current implementation is a small development sample, not a
complete NVD dataset. API error handling and retry logic are
planned improvements.
