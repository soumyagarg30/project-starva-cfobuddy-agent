def getcash_health_signal(cash_instorage: float, cash_usage: float):
    if cash_usage <= 0:
        return {
            "signal": "CASH_FLOW_HEALTH",
            "status": "GRAY",
            "label": "Invalid inputs",
            "months_left": 0,
            "cash_usage": cash_usage,
            "message": "Cash usage must be greater than zero to calculate runway.",
        }

    months_left = cash_instorage / cash_usage

    if months_left > 5:
        status = "GREEN"
        label = "HEALTHY"
        message = f"Cash in storage is enough for {months_left:.2f} months. No immediate action required."
    elif months_left >= 3:
        status = "YELLOW"
        label = "WARNING"
        message = f"Cash in storage is enough for {months_left:.2f} months. Monitor closely and consider cost-saving measures."
    else:
        status = "RED"
        label = "CRITICAL"
        message = f"Cash in storage is only enough for {months_left:.2f} months. Immediate action required to secure additional funding or reduce expenses."

    return {
        "signal": "CASH_FLOW_HEALTH",
        "status": status,
        "label": label,
        "months_left": round(months_left, 2),
        "cash_usage": cash_usage,
        "message": message,
    }
        

