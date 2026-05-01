from fastapi import APIRouter

from .schemas import (
    FinancialStrategistRequest,
    FinancialStrategistResponse,
    FormulaCalculationRequest,
    FormulaCalculationResponse,
    RagQueryRequest,
    RagQueryResponse,
)
from .service import CFOBuddyService

router = APIRouter(prefix="/cfobuddy", tags=["CFOBuddy"])
service = CFOBuddyService()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "module": "CFOBuddy"}


@router.post("/rag/query", response_model=RagQueryResponse)
async def rag_query(payload: RagQueryRequest) -> RagQueryResponse:
    return service.rag_answer(payload.query)


@router.post(
    "/financial-strategist/evaluate",
    response_model=FinancialStrategistResponse,
)
async def evaluate_financials(
    payload: FinancialStrategistRequest,
) -> FinancialStrategistResponse:
    return service.evaluate_financials(payload)


@router.post(
    "/formula/calculate",
    response_model=FormulaCalculationResponse,
)
async def calculate_formula(
    payload: FormulaCalculationRequest,
) -> FormulaCalculationResponse:
    return service.calculate_formula(payload)
