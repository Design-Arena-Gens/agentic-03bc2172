"""Pydantic models for InsightAgent."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Iterable, List, Literal, Mapping, Optional

from pydantic import BaseModel, Field, RootModel, ValidationInfo, field_validator


class ChannelType(str, Enum):
    FACEBOOK = "facebook"
    GOOGLE = "google"
    TIKTOK = "tiktok"
    SNAP = "snap"
    OTHER = "other"


class ColumnAlias(BaseModel):
    name: str
    synonyms: List[str] = Field(default_factory=list)


class ColumnSchema(BaseModel):
    key: str
    aliases: List[ColumnAlias]
    required: bool = True


class InsightAgentConfig(BaseModel):
    llm_model: str = Field(default="gpt-4o-mini")
    channel: ChannelType = Field(default=ChannelType.FACEBOOK)
    enable_structured_validation: bool = Field(default=True)
    fuzzy_column_match: bool = Field(default=True)
    min_confidence: float = Field(default=0.75)
    max_workers: int = Field(default=4)


class MetricSnapshot(BaseModel):
    campaign_name: Optional[str] = None
    ad_set_name: Optional[str] = None
    ad_name: Optional[str] = None
    ad_id: Optional[str] = None
    spend: Optional[float] = None
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    ctr_percent: Optional[float] = Field(default=None, description="Click-through rate in %")
    frequency: Optional[float] = None
    roas: Optional[float] = Field(default=None, description="Return on ad spend")
    purchases: Optional[int] = None
    purchase_value: Optional[float] = None
    adds_to_cart: Optional[int] = None
    atc_to_purchase_percent: Optional[float] = Field(default=None, description="ATC to purchase conversion %")
    ctr_7d_percent: Optional[float] = None
    ctr_prev7_percent: Optional[float] = None
    ctr_drop_vs_prev7_percent: Optional[float] = None
    status: Optional[Literal["pause", "fix", "test", "keep"]] = None


class InsightPayload(BaseModel):
    rows: List[Mapping[str, Any]]

    @field_validator("rows")
    @classmethod
    def ensure_non_empty(cls, value: Iterable[Mapping[str, Any]]) -> Iterable[Mapping[str, Any]]:
        data = list(value)
        if not data:
            msg = "Insight payload must include at least one row"
            raise ValueError(msg)
        return data


class InsightContext(BaseModel):
    resolved_columns: Dict[str, str]
    metrics: List[MetricSnapshot]
    channel: ChannelType
    config: InsightAgentConfig
    baseline_insights: List[Insight] = Field(default_factory=list)


class Recommendation(BaseModel):
    summary: str
    actions: List[str] = Field(default_factory=list)
    priority: Literal["low", "medium", "high"] = Field(default="medium")


class Insight(BaseModel):
    label: str
    signal: str
    recommendation: Recommendation
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class InsightRequest(BaseModel):
    payload: InsightPayload
    config: InsightAgentConfig = Field(default_factory=InsightAgentConfig)


class InsightResponse(BaseModel):
    insights: List[Insight]
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InsightResponseEnvelope(RootModel[List[Insight]]):
    pass
