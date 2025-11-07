"""Agent definitions leveraging LangGraph for multi-agent orchestration."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Sequence

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from .models import Insight, InsightContext, InsightResponse, Recommendation


def marketing_system_prompt(channel: str) -> str:
    return (
        "You are InsightAgent, a senior performance marketing strategist. "
        "You receive structured campaign metrics and must produce concise insight summaries. "
        "Respond with short bullet point recommendations tailored to {channel} advertising."
    ).format(channel=channel)


class InsightSynthesisAgent:
    """LLM-backed agent that transforms metrics into insights."""

    def __init__(self, llm: Any) -> None:
        self._llm = llm

    async def arun(self, context: InsightContext, config: RunnableConfig | None = None) -> InsightResponse:
        prompt = [
            SystemMessage(content=marketing_system_prompt(context.channel.value)),
            HumanMessage(
                content=[
                    {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "insight_payload",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "insights": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "label": {"type": "string"},
                                                "signal": {"type": "string"},
                                                "recommendation": {
                                                    "type": "object",
                                                    "properties": {
                                                        "summary": {"type": "string"},
                                                        "actions": {
                                                            "type": "array",
                                                            "items": {"type": "string"},
                                                        },
                                                        "priority": {
                                                            "type": "string",
                                                            "enum": ["low", "medium", "high"],
                                                        },
                                                    },
                                                    "required": ["summary"],
                                                },
                                                "confidence": {
                                                    "type": "number",
                                                    "minimum": 0,
                                                    "maximum": 1,
                                                },
                                            },
                                            "required": ["label", "signal", "recommendation"],
                                        },
                                    },
                                    "summary": {"type": "string"},
                                },
                                "required": ["insights"],
                            },
                        },
                    }
                ]
            ),
            AIMessage(  # Provide contextual data as tool response style message
                content=[
                    {
                        "type": "tool_result",
                        "tool_call_id": "metrics_snapshot",
                        "output": {
                            "metrics": [m.model_dump() for m in context.metrics],
                            "resolved_columns": context.resolved_columns,
                            "baseline_insights": [insight.model_dump() for insight in context.baseline_insights],
                        },
                    }
                ]
            ),
        ]
        raw = await self._llm.ainvoke(prompt, config=config)
        payload = raw if isinstance(raw, dict) else getattr(raw, "content", raw)
        if isinstance(payload, str):
            payload = json.loads(payload)
        return InsightResponse.model_validate(payload)


def build_graph(llm: Any):
    graph = StateGraph(dict)

    agent = InsightSynthesisAgent(llm)

    async def run_agent(state: Dict[str, Any]) -> Dict[str, Any]:
        context: InsightContext = state["context"]
        response = await agent.arun(context)
        return {"insight_response": response}

    graph.add_node("synthesis", run_agent)
    graph.add_edge("synthesis", END)

    graph.set_entry_point("synthesis")
    return graph.compile()
