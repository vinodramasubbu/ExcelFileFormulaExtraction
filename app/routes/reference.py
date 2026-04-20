"""Reference data routes – expose the lookup tables from the Tables sheet."""

from fastapi import APIRouter

from app.data.reference_data import BRANCHES, COMMISSION_TIERS, POLICY_TYPES
from app.schemas import CommissionTier, ReferenceDataResponse

router = APIRouter(prefix="/api/reference", tags=["Reference Data"])


@router.get(
    "/",
    response_model=ReferenceDataResponse,
    summary="Return all reference / lookup data",
    description=(
        "Exposes the commission tier table (Tables!A2:B6), "
        "the valid policy types (Tables!A10:A15), and known branches."
    ),
)
def get_reference_data() -> ReferenceDataResponse:
    return ReferenceDataResponse(
        commission_tiers=[CommissionTier(**t) for t in COMMISSION_TIERS],
        policy_types=POLICY_TYPES,
        branches=BRANCHES,
    )
