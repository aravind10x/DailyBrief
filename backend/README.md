# Backend

The backend provides the optional live integration path for Daily Brief.

## Responsibilities

- receive founder context and task-planning requests
- assemble hybrid context from structured data and memory
- generate daily briefs and weekly planning artifacts
- manage task and approval workflows

## Run

```bash
conda run -n daily-brief python -m pip install -r backend/requirements.txt
conda run -n daily-brief uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Verify

```bash
conda run -n daily-brief python -m pytest backend/tests -q
```

Tests that require Supabase, OpenMemory, or OpenAI credentials skip cleanly when those services are not configured.

## Environment

Use either [backend/.env.example](.env.example) or [backend/env.sample](env.sample) as the starting point for local configuration.

For the product overview and public demo story, see [README.md](../README.md).
