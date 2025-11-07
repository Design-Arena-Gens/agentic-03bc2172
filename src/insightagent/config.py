"""Configuration helpers for InsightAgent."""

from __future__ import annotations

import os
from typing import Any, Callable

from langchain_openai import ChatOpenAI

from .models import InsightAgentConfig


def openai_chat_factory(config: InsightAgentConfig) -> Callable[[], ChatOpenAI]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required")

    def factory() -> ChatOpenAI:
        return ChatOpenAI(model=config.llm_model, temperature=0.2)

    return factory
