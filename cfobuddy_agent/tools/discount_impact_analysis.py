# tools/discount_impact.py

import json
from langchain_core.tools import tool

def load_data():
    with open("data/sample_data.json") as f:
        return json.load(f)

@tool
def discount_impact_analysis(new_discount_pct: float) -> str:
    """
    What-if analysis: if we apply X% discount on AOV across all orders,
    how many orders stay CM2-positive vs go negative?
    Use when user asks 'what if we give 15% discount' or similar.
    new_discount_pct: a number like 10, 15, 20 (meaning 10%, 15%, 20%)
    """
    data   = load_data()
    orders = data["orders"]

    results = []
    for o in orders:
        aov          = o["aov"]
        new_discount = aov * (new_discount_pct / 100)
        cogs         = o["cogs"]
        delivery     = o["delivery_cost"]
        platform_fee = aov * o["platform_fee_pct"]

        new_cm1 = aov - new_discount - cogs
        new_cm2 = new_cm1 - delivery - platform_fee

        old_discount = o["discount"]
        old_cm1      = aov - old_discount - cogs
        old_cm2      = old_cm1 - delivery - platform_fee

        results.append({
            "order_id"      : o["order_id"],
            "aov"           : aov,
            "old_discount"  : old_discount,
            "new_discount"  : round(new_discount, 2),
            "old_CM2"       : round(old_cm2, 2),
            "new_CM2"       : round(new_cm2, 2),
            "cm2_change"    : round(new_cm2 - old_cm2, 2),
            "still_viable"  : new_cm2 > 0
        })

    viable      = sum(1 for r in results if r["still_viable"])
    not_viable  = len(results) - viable
    avg_new_cm2 = sum(r["new_CM2"] for r in results) / len(results)

    summary = {
        "scenario"              : f"{new_discount_pct}% discount on AOV",
        "total_orders"          : len(results),
        "still_cm2_positive"    : viable,
        "gone_cm2_negative"     : not_viable,
        "average_new_CM2"       : round(avg_new_cm2, 2),
        "recommendation"        : (
            "Safe to run promo" if viable == len(results)
            else f"WARNING: {not_viable} orders will burn money at this discount"
        ),
        "order_breakdown"       : results
    }

    return json.dumps(summary, indent=2)