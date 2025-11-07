"""LangGraph orchestrator for InsightAgent."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Mapping, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from .agents import build_graph
from .metrics import canonicalize_headers, extract_metrics
from .models import InsightAgentConfig, InsightContext, InsightRequest, InsightResponse
from .heuristics import generate_rule_based_insights


class ColumnResolver:
    """Resolve raw column headers to canonical names."""

    def __init__(self, enable_fuzzy: bool = True) -> None:
        self._enable_fuzzy = enable_fuzzy

    def resolve(self, rows: List[Mapping[str, Any]]) -> Dict[str, str]:
        headers = set()
        for row in rows:
            headers.update(row.keys())
        return canonicalize_headers(headers, enable_fuzzy=self._enable_fuzzy)


class InsightAgentEngine:
    """Primary entry point for generating insights from marketing datasets."""

    def __init__(self, llm: BaseChatModel, config: Optional[InsightAgentConfig] = None) -> None:
        self._llm = llm
        self._config = config or InsightAgentConfig()
        self._column_resolver = ColumnResolver(enable_fuzzy=self._config.fuzzy_column_match)
        self._graph: Optional[Any] = None

    def _ensure_graph(self) -> Any:
        if self._graph is None:
            self._graph = build_graph(self._llm)
        return self._graph

    def _build_context(self, rows: List[Mapping[str, Any]]) -> InsightContext:
        resolved_columns = self._column_resolver.resolve(rows)
        metrics = extract_metrics(rows, resolved_columns)
        baseline_insights = generate_rule_based_insights(metrics)
        return InsightContext(
            resolved_columns=resolved_columns,
            metrics=metrics,
            channel=self._config.channel,
            config=self._config,
            baseline_insights=baseline_insights,
        )

    async def arun(self, request: InsightRequest, *, config: Optional[RunnableConfig] = None) -> InsightResponse:
        context = self._build_context(request.payload.rows)
        graph = self._ensure_graph()
        state = {"context": context}
        result = await graph.ainvoke(state, config=config)
        response: InsightResponse = result["insight_response"]
        response.metadata.setdefault("resolved_columns", context.resolved_columns)
        return response

    def run(self, request: InsightRequest, *, config: Optional[RunnableConfig] = None) -> InsightResponse:
        return asyncio.run(self.arun(request, config=config))


def load_default_engine(llm_factory: Any) -> InsightAgentEngine:
    """Convenience helper to instantiate engine from LLM factory."""

    llm = llm_factory()
    return InsightAgentEngine(llm=llm)
