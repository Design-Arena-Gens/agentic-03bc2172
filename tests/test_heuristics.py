from insightagent.heuristics import generate_rule_based_insights
from insightagent.models import MetricSnapshot


def test_roas_low_generates_actionable_recommendation():
    snapshot = MetricSnapshot(roas=1.6, ctr_percent=2.5, atc_to_purchase_percent=15)
    insights = generate_rule_based_insights([snapshot])
    labels = [insight.label for insight in insights]
    assert "ROAS 1–2" in labels


def test_ctr_gap_detected():
    snapshot = MetricSnapshot(ctr_percent=2.2, atc_to_purchase_percent=10)
    insights = generate_rule_based_insights([snapshot])
    matching = [ins for ins in insights if "conversion" in ins.signal.lower()]
    assert matching
