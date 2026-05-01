# tools/pulse_dashboard.py

import json
from langchain_core.tools import tool

def load_data():
    with open("data/sample_data.json") as f:
        return json.load(f)

def _cash_health(data):
    from tools.months_left_analysis import get_burn
    cash         = data["cash_in_bank"]
    monthly_burn = get_burn(data)
    if monthly_burn <= 0:
        return {"status": "GREEN", "label": "Cash flow positive", "runway_months": "∞"}
    runway = cash / monthly_burn
    if runway > 6:
        return {"status": "GREEN",  "label": "Calm runway",    "runway_months": round(runway,1)}
    elif runway >= 3:
        return {"status": "YELLOW", "label": "Watch closely",  "runway_months": round(runway,1)}
    else:
        return {"status": "RED",    "label": "Critical",       "runway_months": round(runway,1)}

def _fulfillment_flow():
    import random
    COST_PER_MIN = 4.5
    zones = []
    for name in ["Zone A", "Zone B"]:
        delay = round(random.uniform(0.5, 8.0), 1)
        zones.append({
            "zone"       : name,
            "congestion" : random.choice(["LOW", "MEDIUM", "HIGH"]),
            "delay_min"  : delay,
            "extra_cost" : round(delay * COST_PER_MIN, 2)
        })
    avg_delay = sum(z["delay_min"] for z in zones) / len(zones)
    any_high  = any(z["congestion"] == "HIGH" for z in zones)

    if avg_delay < 2 and not any_high:
        return {"status": "GREEN",  "label": "Flowing smoothly",    "avg_delay": avg_delay}
    elif avg_delay < 5 and not any_high:
        return {"status": "YELLOW", "label": "Zone bottlenecks",    "avg_delay": avg_delay}
    else:
        return {"status": "RED",    "label": "Operations disrupted","avg_delay": avg_delay}

def _unit_econ_quality(data):
    orders      = data["orders"]
    cm2_positive = 0
    for o in orders:
        aov  = o["aov"]
        cm1  = aov - o["discount"] - o["cogs"]
        cm2  = cm1 - o["delivery_cost"] - (aov * o["platform_fee_pct"])
        if cm2 > 0:
            cm2_positive += 1
    pct = (cm2_positive / len(orders)) * 100

    if pct >= 80:
        return {"status": "BLUE",   "label": "Margin quality",        "cm2_positive_pct": pct}
    elif pct >= 50:
        return {"status": "YELLOW", "label": "Margin under pressure", "cm2_positive_pct": pct}
    else:
        return {"status": "RED",    "label": "Margin crisis",         "cm2_positive_pct": pct}

@tool
def get_pulse_dashboard() -> str:
    """
    Returns the CEO Pulse Dashboard showing all 3 signals:
    Signal 01 - Cash Health (runway)
    Signal 02 - Fulfillment Flow (CV/operations)
    Signal 03 - Unit Economics Quality (margins)
    Use when user asks 'how is business', 'show dashboard', or 'give me a summary'.
    """
    data = load_data()

    s1 = _cash_health(data)
    s2 = _fulfillment_flow()
    s3 = _unit_econ_quality(data)

    dashboard = {
        "CEO Pulse Dashboard": [
            {"Signal 01 - Cash Health"            : s1},
            {"Signal 02 - Fulfillment Flow"       : s2},
            {"Signal 03 - Unit Economics Quality" : s3},
        ],
        "overall_health": (
            "🟢 Business under control"
            if all(s["status"] in ["GREEN", "BLUE"]
                   for s in [s1, s2, s3])
            else "⚠️ Attention needed on some signals"
        )
    }

    return json.dumps(dashboard, indent=2)
