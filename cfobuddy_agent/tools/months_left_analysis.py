# tools/runway_analysis.py

import json
from langchain_core.tools import tool

def load_data():
    with open("data/sample_data.json") as f:
        return json.load(f)

def get_burn(data: dict) -> float:
    # reuse burn logic inline to avoid circular imports
    orders       = data["orders"]
    fixed_costs  = data["monthly_fixed_costs"]
    order_volume = data["monthly_order_volume"]

    avg_aov          = sum(o["aov"] for o in orders) / len(orders)
    avg_discount     = sum(o["discount"] for o in orders) / len(orders)
    avg_cogs         = sum(o["cogs"] for o in orders) / len(orders)
    avg_delivery     = sum(o["delivery_cost"] for o in orders) / len(orders)
    avg_platform_fee = sum(o["aov"] * o["platform_fee_pct"] for o in orders) / len(orders)
    avg_overhead     = sum(o["dark_store_overhead"] for o in orders) / len(orders)

    avg_revenue  = (avg_aov - avg_discount) * order_volume
    avg_costs    = (avg_cogs + avg_delivery + avg_platform_fee + avg_overhead) * order_volume
    monthly_burn = (fixed_costs + avg_costs) - avg_revenue
    return round(monthly_burn, 2)

@tool
def runway_analysis() -> str:
    """
    Calculates how many months of runway the company has left.
    Signal 01 - Cash Health.
    Use when user asks 'how long can we survive', 'what is our runway',
    or 'how is our cash health'.
    """
    data         = load_data()
    cash         = data["cash_in_bank"]
    monthly_burn = get_burn(data)

    if monthly_burn <= 0:
        return json.dumps({
            "status"        : "GREEN",
            "label"         : "Cash flow positive",
            "runway_months" : "Infinite — company is profitable",
            "monthly_burn"  : monthly_burn,
            "message"       : "You are not burning cash. You are generating profit."
        }, indent=2)

    runway = cash / monthly_burn

    if runway > 6:
        status  = "GREEN"
        label   = "Calm runway"
        message = f"You have {round(runway, 1)} months of runway. No immediate action needed."
    elif runway >= 3:
        status  = "YELLOW"
        label   = "Watch closely"
        message = f"Only {round(runway, 1)} months left. Begin fundraising conversations now."
    else:
        status  = "RED"
        label   = "Critical"
        message = f"URGENT: Only {round(runway, 1)} months left. Cut costs or raise immediately."

    return json.dumps({
        "signal"          : "01 - Cash Health",
        "status"          : status,
        "label"           : label,
        "cash_in_bank"    : cash,
        "monthly_burn"    : monthly_burn,
        "runway_months"   : round(runway, 1),
        "message"         : message
    }, indent=2)