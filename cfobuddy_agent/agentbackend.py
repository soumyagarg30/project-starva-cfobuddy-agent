import json
import requests
from types import SimpleNamespace

from signals.agent_tools import (
    calculate_unit_economics,
    discount_impact_analysis,
    get_cv_operational_signals,
)
from signals.dashboard import render_signal_board
from prompts.cfo_buddy import CFO_SYSTEM_PROMPT
from tools.metrics import calculate_growth_metrics

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"

# tracks growth metric inputs collected across conversation turns
_growth_context = {}


# -----------------------------------------
# OLLAMA CALL
# -----------------------------------------
def call_ollama(prompt: str) -> str | None:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "").strip()
        return None
    except Exception:
        return None


# -----------------------------------------
# SAFE TOOL CALLERS
# -----------------------------------------
def get_unit_economics_data() -> dict | None:
    try:
        raw = calculate_unit_economics.invoke({})
        return json.loads(raw)
    except Exception as e:
        print(f"[Tool Error - unit_economics]: {e}")
        return None


def get_discount_data(percent: float) -> dict | None:
    try:
        raw = discount_impact_analysis.invoke({"new_discount_pct": percent})
        return json.loads(raw)
    except Exception as e:
        print(f"[Tool Error - discount_impact]: {e}")
        return None


def get_fulfillment_data() -> dict | None:
    try:
        raw = get_cv_operational_signals.invoke({})
        return json.loads(raw)
    except Exception as e:
        print(f"[Tool Error - cv_signals]: {e}")
        return None


def get_growth_data(aov, cogs, churn, spend, customers, cohort="[]") -> dict | None:
    try:
        raw = calculate_growth_metrics.invoke({
            "aov"                   : float(aov),
            "cogs"                  : float(cogs),
            "monthly_churn_pct"     : float(churn),
            "total_marketing_spend" : float(spend),
            "new_customers_acquired": int(customers),
            "cohort_data"           : cohort
        })
        return json.loads(raw)
    except Exception as e:
        print(f"[Tool Error - growth_metrics]: {e}")
        return None


# -----------------------------------------
# FORMATTERS
# -----------------------------------------
def format_unit_economics(data: dict) -> str:
    total   = data.get("total_orders_analyzed", "N/A")
    cm2_pos = data.get("cm2_positive_orders", "N/A")
    avg_cm2 = data.get("average_CM2", "N/A")
    health  = data.get("overall_health", "N/A")

    pct = (
        round((cm2_pos / total) * 100, 1)
        if isinstance(total, int) and isinstance(cm2_pos, (int, float)) and total > 0
        else "N/A"
    )

    return f"""
Unit Economics Analysis:

  Orders analyzed     : {total}
  CM2-positive orders : {cm2_pos} ({pct}%)
  Average CM2         : ₹{avg_cm2}
  Overall health      : {health}

How to read this:
  CM1 = AOV - Discount - COGS           (covered product cost?)
  CM2 = CM1 - Delivery - Platform Fee   (viable per order?)
  CM3 = CM2 - Dark Store Overhead       (full picture)

{pct}% of orders are CM2-positive — avg margin ₹{avg_cm2}/order.

Want me to model a different scenario?
""".strip()


def format_discount(data: dict, percent: float) -> str:
    return f"""
Discount Impact at {percent}%:

  Total orders        : {data.get('total_orders', 'N/A')}
  Still CM2-positive  : {data.get('still_cm2_positive', 'N/A')}
  Gone CM2-negative   : {data.get('gone_cm2_negative', 'N/A')}
  New average CM2     : ₹{data.get('average_new_CM2', 'N/A')}

{data.get('recommendation', '')}

At {percent}% discount, {data.get('gone_cm2_negative', '?')} orders would burn money.
Will the extra volume from this promo offset that loss?

Want me to model a different scenario?
""".strip()


def format_fulfillment(data: dict) -> str:
    zones = data.get("zone_breakdown", [])
    return f"""
Fulfillment Flow — {data.get('label', 'N/A')} ({data.get('status', 'N/A')})

  Average packing delay : {data.get('avg_delay_minutes', 'N/A')} minutes
  Extra cost per order  : ₹{data.get('avg_extra_cost', 'N/A')}
  Zones monitored       : {len(zones)}

{data.get('message', '')}

Want me to model a different scenario?
""".strip()


def format_growth_metrics(data: dict) -> str:
    gm      = data.get("gross_margin", {})
    cac     = data.get("cac", {})
    ltv     = data.get("ltv", {})
    payback = data.get("cac_payback", {})
    ratio   = data.get("ltv_cac_ratio", {})
    churn   = data.get("churn", {})
    cohorts = data.get("cohort_analysis", [])

    cohort_text = ""
    if isinstance(cohorts, list) and cohorts:
        cohort_text = "\nCohort Analysis:\n"
        for c in cohorts:
            cohort_text += (
                f"  {c['cohort_month']} — "
                f"{c['customers']} customers, "
                f"avg {c['avg_orders']} orders, "
                f"LTV ₹{c['cohort_gross_ltv']} — "
                f"CAC recovered: {c['recovered_cac']}\n"
            )

    return f"""
Growth Metrics Analysis:

  Gross Margin      : ₹{gm.get('amount', 'N/A')} ({gm.get('percentage', 'N/A')})
  CAC               : ₹{cac.get('value', 'N/A')}  (₹{cac.get('spend', 'N/A')} spend / {cac.get('new_customers', 'N/A')} customers)
  LTV               : ₹{ltv.get('value', 'N/A')}
  LTV formula       : {ltv.get('formula', 'N/A')}
  CAC Payback       : {payback.get('months', 'N/A')} months — {payback.get('health', '')}
  LTV:CAC Ratio     : {ratio.get('ratio', 'N/A')}x — {ratio.get('health', '')}

Churn:
  Monthly churn     : {churn.get('monthly_pct', 'N/A')}%
  Annual churn      : {churn.get('annual_pct', 'N/A')}%
  Avg customer life : {churn.get('avg_customer_life_months', 'N/A')} months
{cohort_text}
Want me to model a different scenario?
""".strip()


# -----------------------------------------
# GROWTH METRICS CONVERSATION HANDLER
# -----------------------------------------
def handle_growth_conversation(user_text: str) -> str:
    """
    Collects 5 required inputs one by one across turns,
    then runs the tool once all are available.
    """
    global _growth_context

    # extract first number found in user message
    number = None
    for token in user_text.replace(",", "").replace("₹", "").split():
        try:
            number = float(token)
            break
        except ValueError:
            continue

    if "aov" not in _growth_context:
        if number:
            _growth_context["aov"] = number
            return f"Got it — AOV ₹{int(number)}. What is your COGS (product cost) per order in ₹?"
        return (
            "To calculate LTV, CAC and growth metrics I need a few numbers.\n\n"
            "Let's start — what is your AOV (Average Order Value) in ₹?"
        )

    if "cogs" not in _growth_context:
        if number:
            _growth_context["cogs"] = number
            return f"Got it — COGS ₹{int(number)}. What is your monthly churn rate? (e.g. type 5 for 5%)"
        return "What is your COGS (product cost) per order in ₹?"

    if "churn" not in _growth_context:
        if number:
            _growth_context["churn"] = number
            return f"Got it — {number}% monthly churn. How much did you spend on marketing this month in ₹?"
        return "What is your monthly churn rate? (e.g. type 5 for 5%)"

    if "spend" not in _growth_context:
        if number:
            _growth_context["spend"] = number
            return f"Got it — ₹{number:,.0f} marketing spend. How many new customers did you acquire this month?"
        return "How much did you spend on marketing this month in ₹?"

    if "customers" not in _growth_context:
        if number:
            _growth_context["customers"] = int(number)
        else:
            return "How many new customers did you acquire this month?"

    # all inputs collected — run tool and reset context
    ctx             = _growth_context.copy()
    _growth_context = {}

    data = get_growth_data(
        aov       = ctx["aov"],
        cogs      = ctx["cogs"],
        churn     = ctx["churn"],
        spend     = ctx["spend"],
        customers = ctx["customers"]
    )

    if data:
        return format_growth_metrics(data)
    return "Something went wrong calculating growth metrics. Please try again."


# -----------------------------------------
# GENERAL EXPLANATIONS
# -----------------------------------------
GENERAL_EXPLANATIONS = {
    "what is unit economics": """
Unit Economics = financial performance of ONE order.

  CM1 = AOV - Discount - COGS           (covered product cost?)
  CM2 = CM1 - Delivery - Platform Fee   (viable per order?)
  CM3 = CM2 - Dark Store Overhead       (full picture)

If CM2 > 0 → you make money on each order ✅
If CM2 < 0 → you lose money on each order ❌

Want me to run the actual numbers?
""",
    "what is ltv": """
LTV (Lifetime Value) = total revenue a customer generates before they churn.

Formula: LTV = (AOV × Gross Margin %) ÷ Monthly Churn Rate

Example: AOV ₹400, Gross Margin 30%, Churn 5%
  LTV = (400 × 0.30) ÷ 0.05 = ₹2,400

Golden rule: LTV:CAC should be at least 3:1.
""",
    "what is cac": """
CAC (Customer Acquisition Cost) = what you spend to get one new customer.

Formula: CAC = Total Marketing Spend ÷ New Customers Acquired

CAC Payback = CAC ÷ (AOV × Gross Margin %)
→ how many months to recover what you spent acquiring them.

Healthy benchmarks:
  Under 6 months  → Excellent
  6–12 months     → Acceptable
  Over 12 months  → Too high
""",
    "what is churn": """
Churn Rate = % of customers who stop ordering each month.

Formula: Monthly Churn = Lost Customers ÷ Total Customers × 100

5% monthly churn  → avg customer life of 20 months
10% monthly churn → avg customer life of only 10 months

Annual churn = 1 - (1 - monthly_churn)^12
5% monthly → ~46% annual (you lose nearly half your base every year!)
""",
    "what is gross margin": """
Gross Margin = revenue left after paying for the product itself.

Formula:
  Gross Margin ₹ = AOV - COGS
  Gross Margin % = (AOV - COGS) / AOV × 100

Example: AOV ₹400, COGS ₹280
  Gross Margin = ₹120 = 30%

This is the ceiling on every other margin — if gross margin is low,
nothing downstream can save you.
""",
    "what is runway": """
Runway = how many months your company can survive at current burn.

Formula: Runway = Cash in Bank ÷ Monthly Burn

  GREEN  → 6+ months  → Calm, focus on growth
  YELLOW → 3–6 months → Start fundraising now
  RED    → <3 months  → Emergency mode
""",
}


def check_general_question(user_text: str) -> str | None:
    lowered = user_text.lower()
    for key, answer in GENERAL_EXPLANATIONS.items():
        if all(word in lowered for word in key.split()):
            return answer.strip()
    return None


# -----------------------------------------
# LOCAL TOOL RESPONSES
# -----------------------------------------
def local_response(user_text: str) -> str:
    global _growth_context
    message = user_text.lower()

    # 1. general explanation questions
    general = check_general_question(user_text)
    if general:
        return general

    # 2. growth metrics — LTV / CAC / churn / gross margin / cohort
    growth_keywords = [
        "ltv", "cac", "churn", "lifetime value", "payback",
        "gross margin", "cohort", "acquisition cost", "growth metrics",
        "growth", "retention"
    ]
    if any(kw in message for kw in growth_keywords) or _growth_context:
        return handle_growth_conversation(user_text)

    # 3. unit economics
    if any(kw in message for kw in ["unit economics", "unit econ", "cm1", "cm2", "cm3", "margins"]):
        data = get_unit_economics_data()
        if data:
            return format_unit_economics(data)
        return "Could not fetch unit economics data right now."

    # 4. discount what-if
    if any(kw in message for kw in ["discount", "promo", "offer"]):
        percent = None
        for token in message.replace("%", "").split():
            try:
                percent = float(token)
                break
            except ValueError:
                continue
        if percent is not None:
            data = get_discount_data(percent)
            if data:
                return format_discount(data, percent)
        return "Sure — what discount percentage do you want to test? (e.g. '15% discount')"

    # 5. fulfillment / operations
    if any(kw in message for kw in ["fulfillment", "delay", "zone", "operations", "packing", "congestion"]):
        data = get_fulfillment_data()
        if data:
            return format_fulfillment(data)
        return "Could not fetch fulfillment data right now."

    # 6. cash / runway / burn
    if any(kw in message for kw in ["runway", "burn", "cash", "survive", "months left"]):
        board       = render_signal_board()
        cash_signal = board.get("cash", {})
        context = (
            f"Cash signal status: {cash_signal.get('status', 'N/A')}\n"
            f"Message: {cash_signal.get('message', 'N/A')}\n"
            f"Months left: {cash_signal.get('months_left', 'N/A')}\n"
            f"User question: {user_text}"
        )
        prompt = f"{CFO_SYSTEM_PROMPT}\n\nContext:\n{context}\n\nAnswer as CFOBuddy:"
        answer = call_ollama(prompt)
        if answer:
            return answer
        return (
            f"Cash Health:\n"
            f"  Status  : {cash_signal.get('status', 'N/A')}\n"
            f"  Runway  : {cash_signal.get('months_left', 'N/A')} months\n"
            f"  Message : {cash_signal.get('message', 'N/A')}"
        )

    # 7. dashboard / summary
    if any(kw in message for kw in ["dashboard", "summary", "signal", "overview", "how is business", "how are we"]):
        board      = render_signal_board()
        board_text = "\n".join([
            f"  {k.upper()}: {v.get('label', '')} — {v.get('message', '')}"
            for k, v in board.items()
        ])
        return (
            f"CEO Pulse Dashboard:\n\n{board_text}\n\n"
            f"Ask me about unit economics, discounts, fulfillment, or growth metrics."
        )

    # 8. everything else → ollama then dashboard fallback
    prompt = f"{CFO_SYSTEM_PROMPT}\nUser: {user_text}\nAssistant:"
    answer = call_ollama(prompt)
    if answer:
        return answer

    board      = render_signal_board()
    board_text = "\n".join([
        f"  {k}: {v.get('label', '')} - {v.get('message', '')}"
        for k, v in board.items()
    ])
    return (
        f"Current Signal Board:\n\n{board_text}\n\n"
        f"Ask me about unit economics, discounts, fulfillment, or growth metrics."
    )


# -----------------------------------------
# BUILD AGENT
# -----------------------------------------
def build_agent():
    def invoke(payload):
        messages = payload.get("messages", [])
        if messages:
            last      = messages[-1]
            user_text = getattr(last, "content", "")
        else:
            user_text = ""

        # ollama first, local fallback
        model_prompt = f"{CFO_SYSTEM_PROMPT}\nUser: {user_text}\nAssistant:"
        model_answer = call_ollama(model_prompt)
        if model_answer:
            return {"messages": [SimpleNamespace(content=model_answer)]}

        answer = local_response(user_text)
        return {"messages": [SimpleNamespace(content=answer)]}

    return SimpleNamespace(invoke=invoke)