import json
from langchain_core.tools import tool


@tool
def calculate_growth_metrics(
    aov: float,
    cogs: float,
    monthly_churn_pct: float,
    total_marketing_spend: float,
    new_customers_acquired: int,
    cohort_data: str = "[]"
) -> str:
    """
    Calculates LTV, Gross Margin, CAC, CAC Payback Period, and Churn Rate.

    Args:
        aov: Average Order Value in rupees
        cogs: Cost of Goods Sold per order in rupees
        monthly_churn_pct: Monthly churn rate as percentage (e.g. 5 means 5%)
        total_marketing_spend: Total marketing + sales spend this month in rupees
        new_customers_acquired: Number of new customers acquired this month
        cohort_data: Optional JSON string of cohort breakdown
                     e.g. '[{"month":"Jan","customers":200,"avg_orders":3.2},...]'
    """

    # ── Gross Margin ────────────────────────────────────────────
    gross_margin_amt = aov - cogs
    gross_margin_pct = (gross_margin_amt / aov) * 100

    # ── CAC ─────────────────────────────────────────────────────
    cac = total_marketing_spend / new_customers_acquired if new_customers_acquired > 0 else 0

    # ── LTV ─────────────────────────────────────────────────────
    # LTV = (AOV × Gross Margin %) / Monthly Churn Rate
    churn_rate   = monthly_churn_pct / 100
    ltv          = (aov * (gross_margin_pct / 100)) / churn_rate if churn_rate > 0 else 0

    # ── CAC Payback Period ───────────────────────────────────────
    monthly_margin_per_customer = aov * (gross_margin_pct / 100)
    payback_months = cac / monthly_margin_per_customer if monthly_margin_per_customer > 0 else 0

    # ── LTV:CAC Ratio ────────────────────────────────────────────
    ltv_cac_ratio = ltv / cac if cac > 0 else 0

    # ── LTV:CAC Health ───────────────────────────────────────────
    if ltv_cac_ratio >= 3:
        ltv_cac_health = "✅ HEALTHY — LTV:CAC above 3x. Good unit economics."
    elif ltv_cac_ratio >= 1:
        ltv_cac_health = "⚠️ WATCH — LTV:CAC between 1-3x. Improve margins or reduce CAC."
    else:
        ltv_cac_health = "❌ CRITICAL — LTV:CAC below 1x. Spending more to acquire than you earn."

    # ── Cohort Analysis ──────────────────────────────────────────
    cohort_summary = []
    try:
        cohorts = json.loads(cohort_data)
        for c in cohorts:
            cohort_ltv = c.get("avg_orders", 1) * gross_margin_amt
            cohort_summary.append({
                "cohort_month"      : c.get("month", "N/A"),
                "customers"         : c.get("customers", 0),
                "avg_orders"        : c.get("avg_orders", 0),
                "cohort_gross_ltv"  : round(cohort_ltv, 2),
                "recovered_cac"     : "✅ YES" if cohort_ltv >= cac else "❌ NO"
            })
    except Exception:
        cohort_summary = []

    # ── Payback health ───────────────────────────────────────────
    if payback_months <= 6:
        payback_health = "✅ Excellent — recovered in under 6 months"
    elif payback_months <= 12:
        payback_health = "⚠️ Acceptable — but aim for under 6 months"
    else:
        payback_health = "❌ Too long — taking over a year to recover CAC"

    result = {
        "gross_margin": {
            "amount"     : round(gross_margin_amt, 2),
            "percentage" : f"{round(gross_margin_pct, 1)}%"
        },
        "cac": {
            "value"      : round(cac, 2),
            "spend"      : total_marketing_spend,
            "new_customers": new_customers_acquired
        },
        "ltv": {
            "value"      : round(ltv, 2),
            "formula"    : f"(₹{aov} × {round(gross_margin_pct,1)}%) ÷ {monthly_churn_pct}% churn"
        },
        "cac_payback": {
            "months"     : round(payback_months, 1),
            "health"     : payback_health
        },
        "ltv_cac_ratio": {
            "ratio"      : round(ltv_cac_ratio, 2),
            "health"     : ltv_cac_health
        },
        "churn": {
            "monthly_pct"   : monthly_churn_pct,
            "annual_pct"    : round(1 - (1 - churn_rate) ** 12, 3) * 100,
            "avg_customer_life_months": round(1 / churn_rate, 1) if churn_rate > 0 else "∞"
        },
        "cohort_analysis"   : cohort_summary if cohort_summary else "No cohort data provided"
    }

    return json.dumps(result, indent=2)