import json
import random
from langchain_core.tools import tool


def load_data():
    with open("data/sample_data.json") as f:
        return json.load(f)


def compute_order_economics(order: dict) -> dict:
    aov = order["aov"]
    discount = order["discount"]
    cogs = order["cogs"]
    delivery = order["delivery_cost"]
    platform_fee = aov * order["platform_fee_pct"]
    overhead = order.get("dark_store_overhead", 0)

    cm1 = aov - discount - cogs
    cm2 = cm1 - delivery - platform_fee
    cm3 = cm2 - overhead

    return {
        "order_id": order["order_id"],
        "AOV": aov,
        "Discount": discount,
        "COGS": cogs,
        "CM1_gross_margin": round(cm1, 2),
        "CM2_after_delivery": round(cm2, 2),
        "CM3_after_overhead": round(cm3, 2),
        "is_viable": cm2 > 0,
        "status": "✅ Profitable" if cm2 > 0 else "❌ Burning money",
    }


@tool
def calculate_unit_economics(order_id: str = None) -> str:
    """Calculate unit economics for one order or all orders."""
    data = load_data()
    orders = data["orders"]

    if order_id:
        orders = [o for o in orders if o["order_id"] == order_id]
        if not orders:
            return f"Order {order_id} not found in data."

    results = [compute_order_economics(o) for o in orders]
    if not results:
        return json.dumps({"error": "No orders available"}, indent=2)

    viable_count = sum(1 for r in results if r["is_viable"])
    avg_cm2 = sum(r["CM2_after_delivery"] for r in results) / len(results)

    summary = {
        "total_orders_analyzed": len(results),
        "cm2_positive_orders": viable_count,
        "cm2_negative_orders": len(results) - viable_count,
        "average_CM2": round(avg_cm2, 2),
        "overall_health": "Healthy" if avg_cm2 > 0 else "Burning",
        "order_breakdown": results,
    }

    return json.dumps(summary, indent=2)


@tool
def discount_impact_analysis(new_discount_pct: float) -> str:
    """Run a price-discount what-if analysis across all sample orders."""
    data = load_data()
    orders = data["orders"]

    results = []
    for o in orders:
        aov = o["aov"]
        new_discount = aov * (new_discount_pct / 100)
        cogs = o["cogs"]
        delivery = o["delivery_cost"]
        platform_fee = aov * o["platform_fee_pct"]

        new_cm1 = aov - new_discount - cogs
        new_cm2 = new_cm1 - delivery - platform_fee

        old_discount = o["discount"]
        old_cm1 = aov - old_discount - cogs
        old_cm2 = old_cm1 - delivery - platform_fee

        results.append({
            "order_id": o["order_id"],
            "aov": aov,
            "old_discount": old_discount,
            "new_discount": round(new_discount, 2),
            "old_CM2": round(old_cm2, 2),
            "new_CM2": round(new_cm2, 2),
            "cm2_change": round(new_cm2 - old_cm2, 2),
            "still_viable": new_cm2 > 0,
        })

    viable = sum(1 for r in results if r["still_viable"])
    not_viable = len(results) - viable
    avg_new_cm2 = sum(r["new_CM2"] for r in results) / len(results)

    summary = {
        "scenario": f"{new_discount_pct}% discount on AOV",
        "total_orders": len(results),
        "still_cm2_positive": viable,
        "gone_cm2_negative": not_viable,
        "average_new_CM2": round(avg_new_cm2, 2),
        "recommendation": (
            "Safe to run promo" if viable == len(results)
            else f"WARNING: {not_viable} orders will burn money at this discount"
        ),
        "order_breakdown": results,
    }

    return json.dumps(summary, indent=2)


@tool
def get_cv_operational_signals() -> str:
    """Simulate CV operational signals for fulfillment flow."""
    zones = [
        {"zone": "Zone A", "congestion": random.choice(["LOW", "LOW", "MEDIUM"]), "queue_depth": random.randint(0, 18), "packing_delay_minutes": round(random.uniform(1.0, 6.5), 1)},
        {"zone": "Zone B", "congestion": random.choice(["LOW", "MEDIUM", "HIGH"]), "queue_depth": random.randint(0, 22), "packing_delay_minutes": round(random.uniform(1.5, 7.5), 1)},
    ]

    avg_delay = sum(z["packing_delay_minutes"] for z in zones) / len(zones)
    avg_cost = sum(z["packing_delay_minutes"] * 4.5 for z in zones) / len(zones)
    any_high = any(z["congestion"] == "HIGH" for z in zones)
    any_medium = any(z["congestion"] == "MEDIUM" for z in zones)

    if avg_delay < 2 and not any_high and not any_medium:
        status = "GREEN"
        label = "Flowing smoothly"
        message = "All zones operating normally. No bottlenecks."
    elif avg_delay < 5 and not any_high:
        status = "YELLOW"
        label = "Zone bottlenecks"
        message = f"Avg delay {round(avg_delay, 1)} min adding ₹{round(avg_cost, 2)}/order in cost."
    else:
        status = "RED"
        label = "Operations disrupted"
        message = f"HIGH congestion. Avg delay {round(avg_delay, 1)} min. Intervene immediately."

    return json.dumps({
        "signal": "02 - Fulfillment Flow",
        "status": status,
        "label": label,
        "avg_delay_minutes": round(avg_delay, 1),
        "avg_extra_cost": round(avg_cost, 2),
        "message": message,
        "zone_breakdown": zones,
    }, indent=2)
