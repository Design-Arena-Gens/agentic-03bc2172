"""Example usage of InsightAgentEngine."""

from insightagent import InsightAgentEngine, InsightRequest, InsightPayload
from insightagent.config import openai_chat_factory
from insightagent.models import InsightAgentConfig

sample_rows = [
    {
        "Campaign name": "Holiday Blitz",
        "Ad set name": "Retargeting",
        "Ad name": "Carousel A",
        "Ad ID": "12345",
        "Spend": 1200.5,
        "Impressions": 45000,
        "Clicks": 900,
        "CTR %": 2.0,
        "Frequency": 3.5,
        "ROAS": 1.8,
        "Purchases": 45,
        "Purchase value": 5400.0,
        "Adds to cart": 200,
        "CTR 7d %": 2.2,
        "CTR prev7 %": 2.5,
    }
]

config = InsightAgentConfig(llm_model="gpt-4o-mini")
engine = InsightAgentEngine(llm=openai_chat_factory(config)())

request = InsightRequest(payload=InsightPayload(rows=sample_rows), config=config)
response = engine.run(request)
print(response.model_dump())
