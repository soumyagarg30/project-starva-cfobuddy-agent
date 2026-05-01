from .models import UnitEconomicsInput, UnitEconomicsOutput

def calculate_unit_economics(inputs: UnitEconomicsInput) -> UnitEconomicsOutput:
    """Day 1: Unit Economics - Foundation for quick commerce strategy"""
    cm = inputs.price_per_order - inputs.variable_cost_per_order
    cm_pct = (cm / inputs.price_per_order * 100) if inputs.price_per_order > 0 else 0.0
    
    if cm_pct >= 35:
        status = "Healthy"
    elif cm_pct >= 20:
        status = "Warning"
    else:
        status = "Critical"
    
    return UnitEconomicsOutput(
        contribution_margin=round(cm, 2),
        contribution_margin_pct=round(cm_pct, 1),
        status=status,
        explanation=f"Contribution margin is {cm_pct:.1f}% → {status} (Quick commerce target: >35%)"
    )