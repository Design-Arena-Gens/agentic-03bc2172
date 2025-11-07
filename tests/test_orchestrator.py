import json
from typing import Any, List

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.language_models.chat_models import BaseChatModel

from insightagent.models import InsightPayload, InsightRequest
from insightagent.orchestrator import InsightAgentEngine


class FakeChatModel(BaseChatModel):
    def __init__(self, payload: AIMessage) -> None:
        super().__init__()
        self._payload = payload

    def _generate(self, messages: List[BaseMessage], stop: Any | None = None, run_manager: Any | None = None) -> ChatResult:
        generation = ChatGeneration(message=self._payload)
        return ChatResult(generations=[generation])

    async def _agenerate(self, messages: List[BaseMessage], stop: Any | None = None, run_manager: Any | None = None) -> ChatResult:
        return self._generate(messages, stop, run_manager)

    @property
    def _llm_type(self) -> str:
        return "fake"


def test_engine_returns_structured_response():
    message = AIMessage(
        content=json.dumps(
            {
                "insights": [
                    {
                        "label": "ROAS 1–2",
                        "signal": "Below efficiency threshold",
                        "recommendation": {
                            "summary": "Test 2–3 new creatives and cap frequency",
                            "actions": [
                                "Launch new hook variants",
                                "Rotate thumbnails",
                                "Apply frequency cap",
                            ],
                            "priority": "high",
                        },
                        "confidence": 0.82,
                    }
                ]
            }
        )
    )
    llm = FakeChatModel(message)
    engine = InsightAgentEngine(llm=llm)
    request = InsightRequest(
        payload=InsightPayload(
            rows=[
                {
                    "Campaign name": "Test",
                    "Ad set name": "Set",
                    "Ad name": "Ad",
                    "Ad ID": "1",
                    "Spend": 100,
                    "Impressions": 1000,
                    "Clicks": 50,
                    "Adds to cart": 40,
                    "Purchases": 10,
                }
            ]
        )
    )

    response = engine.run(request)
    assert response.insights[0].recommendation.summary.startswith("Test 2–3")
    assert response.metadata["resolved_columns"]["campaign_name"] == "Campaign name"
