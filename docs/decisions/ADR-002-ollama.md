# ADR-002: Use Ollama for Local LLM Inference

* **Status:** Accepted for the initial implementation
* **Date:** 2026-10-09

## Context

The project needs an LLM to synthesize retrieved cybersecurity evidence. The initial goal is to build and learn the RAG pipeline without requiring a paid hosted inference API.

## Options Considered

* Ollama with a local model
* A hosted LLM API
* Other local inference runtimes

## Decision

Use Ollama as the initial local inference runtime.

## Rationale

Ollama supports local model experimentation and avoids making a hosted API a mandatory dependency for normal development.

## Trade-offs

* Latency and quality depend on the selected model and available hardware.
* Local inference consumes system resources.
* A smaller local model may produce weaker answers than a larger hosted model.

## Reconsideration Criteria

Revisit the decision if local model quality, latency, compatibility, or resource requirements prevent the project from meeting its evaluation targets.

## Validation Plan

Verify that a candidate model runs locally, measure basic inference latency, and evaluate its answers using retrieved evidence before finalizing the model choice.
