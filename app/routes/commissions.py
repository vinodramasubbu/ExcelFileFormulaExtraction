"""Commission API routes – replicate the Commissions & Tables sheets."""

from fastapi import APIRouter

from app.schemas import (
    BulkCommissionRequest,
    CommissionRequest,
    CommissionResult,
    CommissionSummaryResponse,
)
from app.services.commission_service import calculate_bulk_summary, calculate_commission

router = APIRouter(prefix="/api/commissions", tags=["Commissions"])


@router.post(
    "/calculate",
    response_model=CommissionResult,
    summary="Calculate commission for a single agent",
    description=(
        "Replicates Commissions!F (XLOOKUP bonus rate) and Commissions!G "
        "(sales + sales*rate) for one agent row."
    ),
)
def single_commission(req: CommissionRequest) -> CommissionResult:
    return calculate_commission(req)


@router.post(
    "/summary",
    response_model=CommissionSummaryResponse,
    summary="Bulk commission calculation with summary statistics",
    description=(
        "Processes multiple agents and returns per-agent results plus "
        "branch totals (SUMIF), grand total (SUM), average, mode, and median "
        "– mirroring the full Commissions sheet output."
    ),
)
def bulk_summary(req: BulkCommissionRequest) -> CommissionSummaryResponse:
    return calculate_bulk_summary(req.agents)
