# Architecture

Phase 0 architecture is a minimal operational slice for reproducible startup and health validation.

```mermaid
flowchart LR
    Browser --> API[FastAPI]
    API --> Metrics[Prometheus endpoint]
    API --> LLM[Ollama service]
```

Detailed analysis pipeline and storage architecture are documented in later phases.
