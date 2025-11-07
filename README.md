# InsightAgent Engine

InsightAgent is a headless Python 3.10+ engine that combines LangGraph orchestration, OpenAI-compatible LLMs, and Pydantic v2 schemas to produce structured performance marketing insights.

## Features

- Semantic column resolution for typical campaign exports (campaign/ad set/ad naming, spend, impressions, CTR, ROAS, etc.).
- Derived KPI computation (CTR %, ATC→Purchase %, ROAS deltas) with statistical summaries.
- LangGraph-driven multi-agent workflow to call LLMs with JSON schema validation.
- Pydantic v2 request/response contracts for embeddable plugin or microservice usage.
- Dockerized development environment with pytest-based smoke tests.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
export OPENAI_API_KEY=sk-your-key
python examples/basic_usage.py
```

The example script loads sample meta ads metrics, runs the engine, and prints the structured insights JSON payload.

## Project Layout

```
├── src/insightagent/       # Engine source code
│   ├── agents.py           # LangGraph agent definitions
│   ├── config.py           # LLM factories (OpenAI)
│   ├── metrics.py          # Metric parsing & derived KPIs
│   ├── models.py           # Pydantic v2 schemas
│   └── orchestrator.py     # Engine entrypoint
├── examples/               # Usage samples
├── tests/                  # Pytest suite
└── Dockerfile              # Containerized tooling
```

## Docker

```bash
docker build -t insightagent .
docker run --rm -e OPENAI_API_KEY=sk-your-key insightagent
```

## Deployment

Package the library or run it behind your preferred API layer. The codebase is designed for embedding inside orchestration frameworks or invoking from serverless jobs.
