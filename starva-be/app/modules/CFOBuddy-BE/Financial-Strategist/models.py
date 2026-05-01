from pydantic import BaseModel
from typing import Literal

# Shared Pydantic models used across files

class UnitEconomicsInput(BaseModel):
    price_per_order: float
    variable_cost_per_order: float  # delivery + packaging + COGS + discount

class UnitEconomicsOutput(BaseModel):
    contribution_margin: float
    contribution_margin_pct: float
    status: Literal["Healthy", "Warning", "Critical"]
    explanation: str

class BreakEvenInput(BaseModel):
    monthly_fixed_costs: float
    price_per_order: float
    variable_cost_per_order: float

class BreakEvenOutput(BaseModel):
    break_even_orders: int
    monthly_revenue_needed: float
    explanation: str

class CashRunwayInput(BaseModel):
    cash_balance: float
    monthly_revenue: float
    monthly_fixed_costs: float
    monthly_variable_costs: float

class CashRunwayOutput(BaseModel):
    runway_months: float
    monthly_burn_rate: float
    health_status: Literal["Green", "Amber", "Red"]
    explanation: str

class VarianceInput(BaseModel):
    actual_revenue: float
    budget_revenue: float
    actual_margin_pct: float
    budget_margin_pct: float

class VarianceOutput(BaseModel):
    revenue_variance: float
    margin_variance: float
    total_impact: float
    bridge_explanation: str

class ScenarioInput(BaseModel):
    current_runway_months: float
    discount_increase_pct: float          # e.g., 5 for 5%
    expected_order_growth_pct: float      # e.g., 15 for 15%
    current_contribution_margin_pct: float

class ScenarioOutput(BaseModel):
    new_runway_months: float
    margin_impact_pct: float
    recommendation: str
    explanation: str