"""Metric extraction and derived KPI formulas."""

from __future__ import annotations

from difflib import get_close_matches
from typing import Any, Dict, Iterable, List, Mapping, Optional

import numpy as np

from .models import MetricSnapshot


COLUMN_CANONICAL_NAMES: Dict[str, List[str]] = {
    "campaign_name": ["campaign name", "campaign"],
    "ad_set_name": ["ad set name", "ad set"],
    "ad_name": ["ad name", "ad"],
    "ad_id": ["ad id", "ad identifier"],
    "spend": ["spend", "amount spent"],
    "impressions": ["impressions", "impr"],
    "clicks": ["clicks", "link clicks"],
    "ctr_percent": ["ctr %", "ctr", "click through rate"],
    "frequency": ["frequency"],
    "roas": ["roas", "return on ad spend"],
    "purchases": ["purchases", "purchase"],
    "purchase_value": ["purchase value", "conversion value", "revenue"],
    "adds_to_cart": ["adds to cart", "atc"],
    "ctr_7d_percent": ["ctr 7d %", "ctr 7 day"],
    "ctr_prev7_percent": ["ctr prev7 %", "ctr previous 7"],
    "status": ["status"]
}

DERIVED_METRICS = {
    "ctr_percent": lambda r: safe_pct(r.get("clicks"), r.get("impressions")),
    "atc_to_purchase_percent": lambda r: safe_pct(r.get("purchases"), r.get("adds_to_cart")),
    "ctr_drop_vs_prev7_percent": lambda r: safe_delta_pct(r.get("ctr_7d_percent"), r.get("ctr_prev7_percent")),
}


def safe_pct(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator in (None, 0):
        return None
    return float(numerator) / float(denominator) * 100


def safe_delta_pct(current: Optional[float], previous: Optional[float]) -> Optional[float]:
    if current is None or previous is None:
        return None
    return current - previous


def canonicalize_headers(headers: Iterable[str], *, enable_fuzzy: bool = True) -> Dict[str, str]:
    header_map: Dict[str, str] = {}
    normalized_headers = {header.strip().lower(): header for header in headers}
    for canonical, aliases in COLUMN_CANONICAL_NAMES.items():
        for candidate in headers:
            lc = candidate.strip().lower()
            alias_match = lc in aliases
            if alias_match and canonical not in header_map:
                header_map[canonical] = candidate
                break
        if enable_fuzzy and canonical not in header_map:
            search_bag = set(aliases + [canonical])
            for query in search_bag:
                matches = get_close_matches(query, normalized_headers.keys(), n=1, cutoff=0.85)
                if matches:
                    header_map[canonical] = normalized_headers[matches[0]]
                    break
    return header_map


def resolve_value(row: Mapping[str, Any], resolved_column: Optional[str]) -> Optional[Any]:
    if resolved_column is None:
        return None
    return row.get(resolved_column)


def parse_metric_row(row: Mapping[str, Any], column_map: Dict[str, str]) -> MetricSnapshot:
    resolved = {}
    for canonical in COLUMN_CANONICAL_NAMES.keys():
        resolved_column = column_map.get(canonical)
        value = resolve_value(row, resolved_column)
        resolved[canonical] = value

    for derived_key, formula in DERIVED_METRICS.items():
        resolved[derived_key] = formula(resolved)

    return MetricSnapshot(**resolved)


def extract_metrics(rows: List[Mapping[str, Any]], column_map: Dict[str, str]) -> List[MetricSnapshot]:
    metrics: List[MetricSnapshot] = []
    for row in rows:
        metrics.append(parse_metric_row(row, column_map))
    return metrics


def compute_series_stat(metrics: List[MetricSnapshot], attr: str) -> Dict[str, Optional[float]]:
    values = [getattr(m, attr) for m in metrics if getattr(m, attr) is not None]
    if not values:
        return {"mean": None, "median": None, "std": None, "min": None, "max": None}
    arr = np.array(values, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }
