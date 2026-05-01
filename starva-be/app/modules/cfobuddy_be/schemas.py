from typing import Dict, List, Literal

from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    query: str = Field(..., min_length=3)


class RagQueryResponse(BaseModel):
    query: str
    context_snippets: List[str]
    metrics: Dict[str, float | str]
    insight: str
    recommendation: str
    answer: str


class FinancialStrategistRequest(BaseModel):
    price: float
    variable_cost: float
    cash_balance: float
    revenue: float
    fixed_cost: float
    monthly_variable_cost: float
    discount_pct: float
    orders: float
    growth_rate: float


class FinancialStrategistResponse(BaseModel):
    unit_economics: Dict[str, float]
    cash_runway: Dict[str, float]
    break_even: Dict[str, float]
    discount_impact: Dict[str, float]
    scenario: Dict[str, float]
    insight: str
    recommendation: str


class FormulaCalculationRequest(BaseModel):
    formula_name: Literal[
        "calculate_unit_economics",
        "calculate_cash_runway",
        "calculate_break_even",
        "calculate_discount_impact",
    ]
    inputs: Dict[str, float]


class FormulaCalculationResponse(BaseModel):
    formula_name: str
    formula_expression: str
    result: Dict[str, float]
