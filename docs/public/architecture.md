# Daily Brief Architecture

## Product Shape

Daily Brief is built around one opinionated founder workflow:

1. capture founder context
2. generate a morning brief with rationale
3. approve the plan into execution
4. learn from what actually happened

The public repo defaults to a seeded demo mode so reviewers can understand the value immediately.

## Runtime Modes

### Demo-first mode

- frontend runs with seeded founder data
- no credentials are required
- best for public reviewers, hackathon judges, and fast product understanding

### Live integration mode

- FastAPI backend provides operational APIs
- Supabase stores structured operational state
- OpenMemory stores memory and pattern context
- OpenAI / Azure OpenAI generates briefs and planning artifacts

## System Diagram

```mermaid
flowchart TB
    subgraph Frontend
        A["Landing / Demo Entry"]
        B["Founder Context Editor"]
        C["Morning Brief"]
        D["Execution Board"]
    end

    subgraph Backend
        E["FastAPI Routes"]
        F["OpenAI Service"]
        G["Hybrid Context Service"]
    end

    subgraph Data
        H["Supabase"]
        I["OpenMemory MCP"]
    end

    A --> B
    B --> C
    C --> D

    B -. optional live mode .-> E
    C -. optional live mode .-> E
    D -. optional live mode .-> E

    E --> F
    E --> G
    G --> H
    G --> I
```

## Public Repo Principles

- default to a no-secrets first experience
- keep one excellent founder workflow in focus
- make integration-dependent tests skip cleanly when services are not configured
- avoid internal planning docs, private business context, and placeholder demo behavior in the published tree
