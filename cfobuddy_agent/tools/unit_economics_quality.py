# tools/unit_economics.py

import json
from langchain_core.tools import tool

def load_data():
    with open("data/sample_data.json") as f:
        return json.load(f)

def compute_order_economics(order: dict) -> dict:
    aov           = order["aov"]
    discount      = order["discount"]
    cogs          = order["cogs"]
    delivery      = order["delivery_cost"]
    platform_fee  = aov * order["platform_fee_pct"]   # e.g. 2% of AOV
    overhead      = order["dark_store_overhead"]

    cm1 = aov - discount - cogs
    cm2 = cm1 - delivery - platform_fee
    cm3 = cm2 - overhead

    return {
        "order_id"          : order["order_id"],
        "AOV"               : aov,
        "Discount"          : discount,
        "COGS"              : cogs,
        "CM1_gross_margin"  : round(cm1, 2),
        "CM2_after_delivery": round(cm2, 2),
        "CM3_after_overhead": round(cm3, 2),
        "is_viable"         : cm2 > 0,
        "status"            : "✅ Profitable" if cm2 > 0 else "❌ Burning money"
    }

@tool
def calculate_unit_economics(order_id: str = None) -> str:
    """
    Calculates unit economics (CM1, CM2, CM3) per order.
    If order_id is given, analyzes that order only.
    If no order_id, analyzes all orders and gives a summary.
    Use when user asks about margins, profitability, or unit economics.
    """
    data   = load_data()
    orders = data["orders"]

    # filter if specific order asked
    if order_id:
        orders = [o for o in orders if o["order_id"] == order_id]
        if not orders:
            return f"Order {order_id} not found in data."

    results       = [compute_order_economics(o) for o in orders]
    viable_count  = sum(1 for r in results if r["is_viable"])
    avg_cm2       = sum(r["CM2_after_delivery"] for r in results) / len(results)

    summary = {
        "total_orders_analyzed" : len(results),
        "cm2_positive_orders"   : viable_count,
        "cm2_negative_orders"   : len(results) - viable_count,
        "average_CM2"           : round(avg_cm2, 2),
        "overall_health"        : "Healthy" if avg_cm2 > 0 else "Burning",
        "order_breakdown"       : results
    }

    return json.dumps(summary, indent=2)