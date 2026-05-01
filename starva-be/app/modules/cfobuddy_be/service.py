from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .schemas import (
    FinancialStrategistRequest,
    FinancialStrategistResponse,
    FormulaCalculationRequest,
    FormulaCalculationResponse,
    RagQueryResponse,
)


@dataclass
class KnowledgeDoc:
    topic: str
    text: str


class CFOBuddyService:
    """POC-only hard-coded service for demo use."""

    def __init__(self) -> None:
        self._knowledge_base: List[KnowledgeDoc] = [
            KnowledgeDoc(
                topic="runway",
                text="Runway is healthiest when burn is controlled under 65% of gross margin.",
            ),
            KnowledgeDoc(
                topic="unit economics",
                text="Healthy quick-commerce contribution margin is typically above 25%.",
            ),
            KnowledgeDoc(
                topic="discount",
                text="Discounting is a direct margin risk and should only be used when order growth or retention offsets the loss.",
            ),
            KnowledgeDoc(
                topic="operations",
                text="Congestion and late deliveries increase variable costs and silently reduce net LTV.",
            ),
        ]

    def retrieve_context(self, query: str, top_k: int = 3) -> List[str]:
        query_tokens = set(query.lower().split())
        scored: List[tuple[int, str]] = []

        for doc in self._knowledge_base:
            topic_tokens = set(doc.topic.lower().split())
            text_tokens = set(doc.text.lower().split())
            overlap = len(query_tokens.intersection(topic_tokens.union(text_tokens)))
            scored.append((overlap, doc.text))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [text for score, text in scored[:top_k] if score > 0] or [
            "Prioritize contribution margin, burn control, and retention as the first CFO triad."
        ]

    def rag_answer(self, query: str) -> RagQueryResponse:
        context = self.retrieve_context(query)

        # Demo metrics are intentionally static to keep the POC deterministic.
        metrics: Dict[str, float | str] = {
            "gross_margin_pct": 31.2,
            "burn_rate_inr": 1450000,
            "runway_months": 8.4,
            "repeat_rate_pct": 46.0,
            "risk_flag": "Medium",
        }

        insight = (
            "Margins are healthy but runway is below a 12-month comfort band, "
            "so discounting is a clear risk and must stay tightly managed alongside fulfillment efficiency."
        )
        recommendation = (
            "Reduce discount intensity on low-retention cohorts, and only allow discounts where retention or growth can offset margin pressure. "
            "Reinvest 20% of savings into high-repeat micro-markets to improve runway by ~1.5 months."
        )

        answer = (
            "📊 Metrics\n"
            f"- Gross Margin: {metrics['gross_margin_pct']}%\n"
            f"- Burn Rate: INR {metrics['burn_rate_inr']:,}/month\n"
            f"- Runway: {metrics['runway_months']} months\n"
            f"- Repeat Rate: {metrics['repeat_rate_pct']}%\n\n"
            "📉 Insight\n"
            f"{insight}\n\n"
            "🚀 Recommendation\n"
            f"{recommendation}"
        )

        return RagQueryResponse(
            query=query,
            context_snippets=context,
            metrics=metrics,
            insight=insight,
            recommendation=recommendation,
            answer=answer,
        )

    def calculate_unit_economics(
        self, price: float, variable_cost: float
    ) -> Dict[str, float]:
        cm = price - variable_cost
        cm_percent = (cm / price) * 100 if price else 0.0
        return {
            "contribution_margin": round(cm, 2),
            "cm_percent": round(cm_percent, 2),
        }

    def calculate_cash_runway(
        self,
        cash_balance: float,
        revenue: float,
        fixed_cost: float,
        variable_cost: float,
    ) -> Dict[str, float]:
        burn_rate = fixed_cost + variable_cost - revenue
        runway = cash_balance / burn_rate if burn_rate > 0 else float("inf")
        return {
            "burn_rate": round(burn_rate, 2),
            "runway_months": round(runway, 2) if runway != float("inf") else runway,
        }

    def calculate_break_even(
        self, fixed_cost: float, contribution_margin: float
    ) -> Dict[str, float]:
        break_even_orders = (
            fixed_cost / contribution_margin if contribution_margin > 0 else 0.0
        )
        return {"break_even_orders": round(break_even_orders, 2)}

    def calculate_discount_impact(
        self, price: float, discount_pct: float, cost: float
    ) -> Dict[str, float]:
        new_price = price * (1 - discount_pct)
        new_cm = new_price - cost
        return {
            "new_price": round(new_price, 2),
            "new_cm": round(new_cm, 2),
        }

    def simulate_scenario(
        self,
        price: float,
        cost: float,
        orders: float,
        growth_rate: float,
    ) -> Dict[str, float]:
        new_orders = orders * (1 + growth_rate)
        revenue = new_orders * price
        total_cost = new_orders * cost
        return {
            "new_orders": round(new_orders, 2),
            "revenue": round(revenue, 2),
            "cost": round(total_cost, 2),
            "profit": round(revenue - total_cost, 2),
        }

    def evaluate_financials(
        self, payload: FinancialStrategistRequest
    ) -> FinancialStrategistResponse:
        unit = self.calculate_unit_economics(payload.price, payload.variable_cost)
        runway = self.calculate_cash_runway(
            payload.cash_balance,
            payload.revenue,
            payload.fixed_cost,
            payload.monthly_variable_cost,
        )
        break_even = self.calculate_break_even(
            payload.fixed_cost, unit["contribution_margin"]
        )
        discount = self.calculate_discount_impact(
            payload.price,
            payload.discount_pct,
            payload.variable_cost,
        )
        scenario = self.simulate_scenario(
            payload.price,
            payload.variable_cost,
            payload.orders,
            payload.growth_rate,
        )

        insight = (
            f"Current CM is {unit['cm_percent']}%, with runway at {runway['runway_months']} months. "
            "Discounting pressure can reduce CM quickly unless order growth compensates."
        )
        recommendation = (
            "Target CM >= 25%, keep burn under control, and run discount experiments only in "
            "high-retention cohorts to protect runway."
        )

        return FinancialStrategistResponse(
            unit_economics=unit,
            cash_runway=runway,
            break_even=break_even,
            discount_impact=discount,
            scenario=scenario,
            insight=insight,
            recommendation=recommendation,
        )

    def calculate_formula(
        self, payload: FormulaCalculationRequest
    ) -> FormulaCalculationResponse:
        formula_expressions = {
            "calculate_unit_economics": (
                "contribution_margin = price - variable_cost; "
                "cm_percent = (contribution_margin / price) * 100"
            ),
            "calculate_cash_runway": (
                "burn_rate = fixed_cost + variable_cost - revenue; "
                "runway_months = cash_balance / burn_rate"
            ),
            "calculate_break_even": "break_even_orders = fixed_cost / contribution_margin",
            "calculate_discount_impact": (
                "new_price = price * (1 - discount_pct); new_cm = new_price - cost"
            ),
        }

        inputs = payload.inputs

        if payload.formula_name == "calculate_unit_economics":
            result = self.calculate_unit_economics(
                inputs.get("price", 0.0),
                inputs.get("variable_cost", 0.0),
            )
        elif payload.formula_name == "calculate_cash_runway":
            result = self.calculate_cash_runway(
                inputs.get("cash_balance", 0.0),
                inputs.get("revenue", 0.0),
                inputs.get("fixed_cost", 0.0),
                inputs.get("variable_cost", 0.0),
            )
        elif payload.formula_name == "calculate_break_even":
            result = self.calculate_break_even(
                inputs.get("fixed_cost", 0.0),
                inputs.get("contribution_margin", 0.0),
            )
        else:
            result = self.calculate_discount_impact(
                inputs.get("price", 0.0),
                inputs.get("discount_pct", 0.0),
                inputs.get("cost", 0.0),
            )

        return FormulaCalculationResponse(
            formula_name=payload.formula_name,
            formula_expression=formula_expressions[payload.formula_name],
            result=result,
        )
