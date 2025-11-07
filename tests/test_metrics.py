import math

from insightagent.metrics import extract_metrics


def test_extract_metrics_with_derived_values():
    rows = [
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
    columns = {
        "campaign_name": "Campaign name",
        "ad_set_name": "Ad set name",
        "ad_name": "Ad name",
        "ad_id": "Ad ID",
        "spend": "Spend",
        "impressions": "Impressions",
        "clicks": "Clicks",
        "adds_to_cart": "Adds to cart",
        "purchases": "Purchases",
    }

    metrics = extract_metrics(rows, columns)
    snapshot = metrics[0]
    assert math.isclose(snapshot.ctr_percent, 5.0)
    assert math.isclose(snapshot.atc_to_purchase_percent, 25.0)
