def get_fullfilement_signal(zones: list):
    avg_delay = sum(z["packing_delay_minutes"] for z in zones) / len(zones)
    avg_high_delay = any(z.get("congestion", "").upper() == "HIGH" for z in zones)
    avg_medium_delay = any(z.get("congestion", "").upper() == "MEDIUM" for z in zones)

    if avg_delay < 5 and not avg_high_delay and not avg_medium_delay:
        status = "GREEN"
        label = "HEALTHY"
        message = "All the zones are operating without any abnormal delay."
    elif avg_delay < 10 and not avg_high_delay:
        status = "YELLOW"
        label = "WARNING"
        message = "Some zones are experiencing medium congestion delay. Monitor closely and consider optimizing packing processes."
    else:
        status = "RED"
        label = "CRITICAL"
        message = "Zones are experiencing high congestion and delays. Immediate action required."

    return {
        "signal": "FULFILLMENT_HEALTH",
        "status": status,
        "label": label,
        "avg_delay": round(avg_delay, 1),
        "avg_high_delay": avg_high_delay,
        "avg_medium_delay": avg_medium_delay,
        "message": message,
    }
