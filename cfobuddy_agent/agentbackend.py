# =========================================================
# ENHANCED CFO AGENT
# =========================================================

import json
import requests

from types import SimpleNamespace
from collections import defaultdict

from prompts.cfo_buddy import CFO_SYSTEM_PROMPT

# =========================================================
# DASHBOARD
# =========================================================

from signals.dashboard import render_signal_board

# =========================================================
# TOOLS
# =========================================================

from tools.discount_impact_analysis import (
    discount_impact_analysis
)

from tools.unit_economics_quality import (
    calculate_unit_economics
)

from tools.cv_engine import (
    get_cv_operational_signals
)

from tools.metrics import (
    calculate_growth_metrics
)

from tools.cash_usage import (
    calculate_monthly_burn as calculate_cash_usage
)

# =========================================================
# CONFIG
# =========================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "llama3.2:3b"

# =========================================================
# THREAD MEMORY
# =========================================================

conversation_memory = defaultdict(
    lambda: {
        "growth_context": {},
        "last_tool_used": None,
        "last_response": None,
    }
)

# =========================================================
# OLLAMA CALL
# =========================================================


def call_ollama(prompt: str) -> str | None:

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,

        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.2,
        }
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        if response.status_code == 200:

            data = response.json()

            return data.get("response", "").strip()

        return None

    except Exception as e:

        print(f"[OLLAMA ERROR]: {e}")

        return None

# =========================================================
# GENERIC SAFE TOOL EXECUTOR
# =========================================================


def safe_tool_call(tool_func, payload=None, tool_name="tool"):

    payload = payload or {}

    if hasattr(tool_func, "func"):
        tool_func = tool_func.func

    try:

        if isinstance(payload, dict):
            result = tool_func(**payload)
        else:
            result = tool_func(payload)

        if isinstance(result, str):

            return json.loads(result)

        return result

    except Exception as e:

        print(f"[Tool Error - {tool_name}]: {e}")

        return None

# =========================================================
# TOOL WRAPPERS
# =========================================================


def get_unit_economics_data():

    return safe_tool_call(
        calculate_unit_economics,
        {},
        "unit_economics"
    )


def get_discount_data(percent: float):

    return safe_tool_call(
        discount_impact_analysis,
        {
            "new_discount_pct": percent
        },
        "discount_impact"
    )


def get_fulfillment_data():

    return safe_tool_call(
        get_cv_operational_signals,
        {},
        "cv_engine"
    )


def get_growth_data(
    aov,
    cogs,
    churn,
    spend,
    customers,
    cohort="[]"
):

    return safe_tool_call(
        calculate_growth_metrics,
        {
            "aov": float(aov),
            "cogs": float(cogs),
            "monthly_churn_pct": float(churn),
            "total_marketing_spend": float(spend),
            "new_customers_acquired": int(customers),
            "cohort_data": cohort
        },
        "growth_metrics"
    )


def get_cash_usage_data():

    return safe_tool_call(
        calculate_cash_usage,
        {},
        "cash_usage"
    )


# =========================================================
# FORMATTERS
# =========================================================


def format_unit_economics(data):

    total = data.get("total_orders_analyzed", "N/A")
    positive = data.get("cm2_positive_orders", "N/A")
    avg_cm2 = data.get("average_CM2", "N/A")
    health = data.get("overall_health", "N/A")

    pct = "N/A"

    if isinstance(total, int) and total > 0:

        pct = round((positive / total) * 100, 1)

    return f"""
Unit Economics Analysis

Orders analyzed     : {total}
CM2-positive orders : {positive} ({pct}%)
Average CM2         : ₹{avg_cm2}
Overall health      : {health}

CM1 = AOV - Discount - COGS
CM2 = CM1 - Delivery - Platform Fee
CM3 = CM2 - Dark Store Overhead
""".strip()


def format_discount(data, percent):

    return f"""
Discount Impact Analysis — {percent}%

Total Orders       : {data.get('total_orders', 'N/A')}
Still Profitable   : {data.get('still_cm2_positive', 'N/A')}
Turned Negative    : {data.get('gone_cm2_negative', 'N/A')}
New Avg CM2        : ₹{data.get('average_new_CM2', 'N/A')}

Recommendation:
{data.get('recommendation', '')}
""".strip()


def format_fulfillment(data):

    return f"""
Fulfillment Operations

Status                 : {data.get('status', 'N/A')}
Average Delay          : {data.get('avg_delay_minutes', 'N/A')} mins
Extra Cost Per Order   : ₹{data.get('avg_extra_cost', 'N/A')}

{data.get('message', '')}
""".strip()


def format_growth_metrics(data):

    gm = data.get("gross_margin", {})
    cac = data.get("cac", {})
    ltv = data.get("ltv", {})
    payback = data.get("cac_payback", {})
    ratio = data.get("ltv_cac_ratio", {})

    return f"""
Growth Metrics Analysis

Gross Margin:
  ₹{gm.get('amount', 'N/A')}
  {gm.get('percentage', 'N/A')}

CAC:
  ₹{cac.get('value', 'N/A')}

LTV:
  ₹{ltv.get('value', 'N/A')}

CAC Payback:
  {payback.get('months', 'N/A')} months

LTV:CAC Ratio:
  {ratio.get('ratio', 'N/A')}x
""".strip()


def format_cash_usage(data):

    return f"""
Cash Usage Analysis

Monthly Burn      : ₹{data.get('monthly_burn', 'N/A')}
Cash Remaining    : ₹{data.get('cash_remaining', 'N/A')}
Runway            : {data.get('runway_months', 'N/A')} months

Status:
{data.get('status', 'N/A')}
""".strip()


def format_dashboard(data):

    signals = data.get("signals", [])

    text = "CEO Pulse Dashboard\n\n"

    for signal in signals:

        text += (
            f"{signal.get('metric', '')}: "
            f"{signal.get('status', '')} — "
            f"{signal.get('message', '')}\n"
        )

    return text.strip()

# =========================================================
# HELPERS
# =========================================================


def extract_number(text: str):

    cleaned = (
        text
        .replace(",", "")
        .replace("₹", "")
        .replace("%", "")
    )

    for token in cleaned.split():

        try:

            return float(token)

        except:
            pass

    return None


def remove_duplicate_messages(messages):

    unique = []

    seen = set()

    for msg in messages:

        content = getattr(
            msg,
            "content",
            ""
        ).strip()

        if content not in seen:

            unique.append(msg)

            seen.add(content)

    return unique


def build_conversation(messages):

    conversation = ""

    for msg in messages:

        role = getattr(
            msg,
            "type",
            "human"
        )

        content = getattr(
            msg,
            "content",
            ""
        )

        if role in ["human", "user"]:

            conversation += f"User: {content}\n"

        elif role in ["ai", "assistant"]:

            conversation += f"Assistant: {content}\n"

    return conversation

# =========================================================
# INTENT DETECTOR
# =========================================================


def detect_intent(message: str):

    message = message.lower()

    intents = {

        "discount": [
            "discount",
            "offer",
            "promo",
            "%"
        ],

        "unit_economics": [
            "unit economics",
            "cm1",
            "cm2",
            "cm3",
            "margin"
        ],

        "growth": [
            "ltv",
            "cac",
            "growth",
            "churn",
            "retention",
            "cohort",
            "payback"
        ],

        "cash": [
            "cash",
            "burn",
            "runway",
            "months left"
        ],

        "operations": [
            "fulfillment",
            "packing",
            "delay",
            "operations",
            "zone"
        ],

        "dashboard": [
            "dashboard",
            "pulse",
            "summary",
            "health"
        ]
    }

    scores = {}

    for intent, keywords in intents.items():

        score = 0

        for keyword in keywords:

            if keyword in message:
                score += 1

        scores[intent] = score

    best_intent = max(
        scores,
        key=scores.get
    )

    if scores[best_intent] == 0:
        return None

    return best_intent

# =========================================================
# GROWTH METRICS STATE MACHINE
# =========================================================


def handle_growth_conversation(
    user_text,
    thread_id
):

    ctx = conversation_memory[
        thread_id
    ]["growth_context"]

    number = extract_number(user_text)

    if "aov" not in ctx:

        if number:

            ctx["aov"] = number

            return (
                "Got it.\n"
                "What is your COGS per order in ₹?"
            )

        return (
            "Let's calculate growth metrics.\n\n"
            "What is your AOV in ₹?"
        )

    if "cogs" not in ctx:

        if number:

            ctx["cogs"] = number

            return (
                "Understood.\n"
                "What is your monthly churn rate %?"
            )

        return "What is your COGS per order in ₹?"

    if "churn" not in ctx:

        if number:

            ctx["churn"] = number

            return (
                "Got it.\n"
                "What was your marketing spend this month?"
            )

        return "What is your monthly churn rate %?"

    if "spend" not in ctx:

        if number:

            ctx["spend"] = number

            return (
                "Okay.\n"
                "How many new customers acquired?"
            )

        return "What was your marketing spend?"

    if "customers" not in ctx:

        if number:

            ctx["customers"] = int(number)

        else:

            return (
                "How many new customers acquired?"
            )

    data = get_growth_data(
        aov=ctx["aov"],
        cogs=ctx["cogs"],
        churn=ctx["churn"],
        spend=ctx["spend"],
        customers=ctx["customers"]
    )

    conversation_memory[
        thread_id
    ]["growth_context"] = {}

    if data:

        return format_growth_metrics(data)

    return "Unable to calculate growth metrics."

# =========================================================
# TOOL ROUTER
# =========================================================


def local_response(
    user_text,
    thread_id
):

    message = user_text.lower()

    # =====================================================
    # ACTIVE GROWTH FLOW ALWAYS CONTINUES
    # =====================================================

    growth_ctx = conversation_memory[
        thread_id
    ]["growth_context"]

    if growth_ctx:

        return handle_growth_conversation(
            user_text,
            thread_id
        )

    # =====================================================
    # NORMAL INTENT DETECTION
    # =====================================================

    intent = detect_intent(message)

    if not intent:

        return None

    conversation_memory[
        thread_id
    ]["last_tool_used"] = intent

    # =====================================================
    # GROWTH
    # =====================================================

    if intent == "growth":

        return handle_growth_conversation(
            user_text,
            thread_id
        )

    # =====================================================
    # UNIT ECONOMICS
    # =====================================================

    if intent == "unit_economics":

        data = get_unit_economics_data()

        if data:

            return format_unit_economics(data)

        return "Unable to fetch unit economics."

    # =====================================================
    # DISCOUNT
    # =====================================================

    if intent == "discount":

        percent = extract_number(message)

        if percent is not None:

            data = get_discount_data(percent)

            if data:

                return format_discount(
                    data,
                    percent
                )

        return (
            "What discount percentage "
            "would you like to test?"
        )

    # =====================================================
    # OPERATIONS
    # =====================================================

    if intent == "operations":

        data = get_fulfillment_data()

        if data:

            return format_fulfillment(data)

        return (
            "Unable to fetch operations data."
        )

    # =====================================================
    # CASH
    # =====================================================

    if intent == "cash":

        data = get_cash_usage_data()

        if data:

            return format_cash_usage(data)

        return "Unable to fetch cash data."

    return None


def build_agent():

    def invoke(payload):

        config = payload.get(
            "config",
            {}
        )

        thread_id = (
            config
            .get("configurable", {})
            .get("thread_id", "default")
        )

        messages = payload.get(
            "messages",
            []
        )

        if not messages:

            return {
                "messages": [
                    SimpleNamespace(
                        content="No user input received.",
                        type="ai"
                    )
                ]
            }

        # =================================================
        # REMOVE DUPLICATES
        # =================================================

        messages = remove_duplicate_messages(
            messages
        )

        # =================================================
        # USER MESSAGE
        # =================================================

        last_message = messages[-1]

        user_text = getattr(
            last_message,
            "content",
            ""
        )

        # =================================================
        # TOOL ROUTER FIRST
        # =================================================

        local_answer = local_response(
            user_text,
            thread_id
        )

        if local_answer:

            last_response = conversation_memory[
                thread_id
            ]["last_response"]

            if local_answer == last_response:

                local_answer += (
                    "\n\nWould you like a deeper analysis?"
                )

            conversation_memory[
                thread_id
            ]["last_response"] = local_answer

            return {
                "messages": [
                    SimpleNamespace(
                        content=local_answer,
                        type="ai"
                    )
                ]
            }

        # =================================================
        # FULL CONVERSATION
        # =================================================

        conversation = build_conversation(
            messages
        )

        # =================================================
        # LLM PROMPT
        # =================================================

        model_prompt = f"""
{CFO_SYSTEM_PROMPT}

You are CFOBuddy.

Rules:
- Avoid repeating previous answers
- Give concise but specific insights
- Use previous conversation context
- Do not repeat dashboards unless asked
- Answer differently if the question changes

Conversation History:

{conversation}

Current User Question:
{user_text}

Assistant:
"""

        model_answer = call_ollama(
            model_prompt
        )

        if model_answer:

            last_response = conversation_memory[
                thread_id
            ]["last_response"]

            if model_answer == last_response:

                model_answer += (
                    "\n\nWould you like a more detailed breakdown?"
                )

            conversation_memory[
                thread_id
            ]["last_response"] = model_answer

            return {
                "messages": [
                    SimpleNamespace(
                        content=model_answer,
                        type="ai"
                    )
                ]
            }

        # =================================================
        # FINAL FALLBACK
        # =================================================

        board = render_signal_board()

        fallback_text = (
            "Business Signal Board\n\n"
        )

        for key, value in board.items():

            fallback_text += (
                f"{key.upper()}: "
                f"{value.get('label', '')} — "
                f"{value.get('message', '')}\n"
            )

        return {
            "messages": [
                SimpleNamespace(
                    content=fallback_text,
                    type="ai"
                )
            ]
        }

    return SimpleNamespace(
        invoke=invoke
    )