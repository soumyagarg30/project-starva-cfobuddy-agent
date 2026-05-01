# tools/cv_signals.py

import json
import random
from langchain_core.tools import tool

COST_PER_DELAY_MINUTE = 4.5   # ₹ per minute of packing delay

def simulate_zone_signal(zone_name: str) -> dict:
    """Simulates CV camera output for a dark store zone."""
    congestion = random.choice(["LOW", "LOW", "MEDIUM", "HIGH"])  # weighted
    queue      = random.randint(0, 20)
    delay      = round(random.uniform(0.5, 8.0), 1)

    return {
        "zone"                   : zone_name,
        "congestion"             : congestion,
        "queue_depth"            : queue,
        "packing_delay_minutes"  : delay,
        "extra_cost_per_order"   : round(delay * COST_PER_DELAY_MINUTE, 2)
    }

@tool
def get_cv_operational_signals() -> str:
    """
    Returns operational signals from dark store zones using CV simulation.
    Measures congestion, queue depth, packing delays and their cost impact.
    Signal 02 - Fulfillment Flow.
    Use when user asks about operations, delays, fulfillment, or zone health.
    """
    zones     = [simulate_zone_signal("Zone A"), simulate_zone_signal("Zone B")]
    avg_delay = sum(z["packing_delay_minutes"] for z in zones) / len(zones)
    avg_cost  = sum(z["extra_cost_per_order"] for z in zones) / len(zones)
    any_high  = any(z["congestion"] == "HIGH" for z in zones)
    any_medium= any(z["congestion"] == "MEDIUM" for z in zones)

    if avg_delay < 2 and not any_high and not any_medium:
        status  = "GREEN"
        label   = "Flowing smoothly"
        message = "All zones operating normally. No bottlenecks."
    elif avg_delay < 5 and not any_high:
        status  = "YELLOW"
        label   = "Zone bottlenecks"
        message = f"Avg delay {round(avg_delay,1)} min adding ₹{round(avg_cost,2)}/order in cost."
    else:
        status  = "RED"
        label   = "Operations disrupted"
        message = f"HIGH congestion. Avg delay {round(avg_delay,1)} min. Intervene immediately."

    return json.dumps({
        "signal"              : "02 - Fulfillment Flow",
        "status"              : status,
        "label"               : label,
        "avg_delay_minutes"   : round(avg_delay, 1),
        "avg_extra_cost"      : round(avg_cost, 2),
        "message"             : message,
        "zone_breakdown"      : zones
    }, indent=2)