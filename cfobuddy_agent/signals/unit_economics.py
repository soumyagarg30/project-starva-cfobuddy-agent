def get_unit_econ_signal(orders: list) -> dict:
    cm2_positive = 0
    for o in orders:
        aov = o["aov"]
        cm1 = aov - o["discount"] - o["cogs"]
        cm2 = cm1 - o["delivery_cost"] - (aov * o["platform_fee_pct"])
        if cm2 > 0:
            cm2_positive += 1

    pct = (cm2_positive / len(orders)) * 100

    if pct >= 80:
        status = "BLUE"
        label = "Margin quality"
        message = f"{pct:.0f}% of orders are CM2-positive. Margins are healthy."
    elif pct >= 50:
        status = "YELLOW"
        label = "Margin under pressure"
        message = f"Only {pct:.0f}% of orders CM2-positive. Review discount strategy."
    else:
        status = "RED"
        label = "Margin crisis"
        message = f"Only {pct:.0f}% of orders CM2-positive. Burning badly."

    return {
        "signal": "03 - Unit Economics Quality",
        "status": status,
        "label": label,
        "cm2_positive_pct": round(pct, 1),
        "message": message
    }