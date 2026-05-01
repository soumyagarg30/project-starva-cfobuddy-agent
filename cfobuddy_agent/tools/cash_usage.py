# tools/burn_calculator.py

import json
from langchain_core.tools import tool

def load_data():
    with open("data/sample_data.json") as f:
        return json.load(f)

@tool
def calculate_monthly_burn() -> str:
    """
    Calculates the company's monthly burn rate.
    Burn = total monthly costs minus total monthly revenue.
    Use when user asks about burn rate, monthly losses, or cash usage.
    """
    data         = load_data()
    orders       = data["orders"]
    fixed_costs  = data["monthly_fixed_costs"]
    order_volume = data["monthly_order_volume"]

    # calculate averages from order data
    avg_aov          = sum(o["aov"] for o in orders) / len(orders)
    avg_discount     = sum(o["discount"] for o in orders) / len(orders)
    avg_cogs         = sum(o["cogs"] for o in orders) / len(orders)
    avg_delivery     = sum(o["delivery_cost"] for o in orders) / len(orders)
    avg_platform_fee = sum(o["aov"] * o["platform_fee_pct"] for o in orders) / len(orders)
    avg_overhead     = sum(o["dark_store_overhead"] for o in orders) / len(orders)

    # per order economics
    avg_revenue_per_order = avg_aov - avg_discount
    avg_cost_per_order    = avg_cogs + avg_delivery + avg_platform_fee + avg_overhead

    # monthly totals
    total_monthly_revenue     = avg_revenue_per_order * order_volume
    total_monthly_variable    = avg_cost_per_order * order_volume
    total_monthly_costs       = fixed_costs + total_monthly_variable
    monthly_burn              = total_monthly_costs - total_monthly_revenue

    result = {
        "monthly_order_volume"       : order_volume,
        "avg_revenue_per_order"      : round(avg_revenue_per_order, 2),
        "avg_cost_per_order"         : round(avg_cost_per_order, 2),
        "total_monthly_revenue"      : round(total_monthly_revenue, 2),
        "total_monthly_variable_cost": round(total_monthly_variable, 2),
        "monthly_fixed_costs"        : fixed_costs,
        "total_monthly_costs"        : round(total_monthly_costs, 2),
        "monthly_burn"               : round(monthly_burn, 2),
        "status"                     : (
            "🔴 Burning cash" if monthly_burn > 0
            else "🟢 Cash flow positive"
        ),
        "burn_per_order"             : round(monthly_burn / order_volume, 2)
    }

    return json.dumps(result, indent=2)