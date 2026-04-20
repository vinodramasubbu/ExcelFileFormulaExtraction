"""Policy classification routes – replicate the 'By Policy' sheet."""

from fastapi import APIRouter

from app.schemas import (
    BulkPolicyRequest,
    PolicyClassifyRequest,
    PolicyClassifyResult,
)
from app.services.policy_service import classify_bulk, classify_policy

router = APIRouter(prefix="/api/policies", tags=["Policies"])


@router.post(
    "/classify",
    response_model=PolicyClassifyResult,
    summary="Classify a single policy type",
    description=(
        "Replicates By Policy!F: IF(type='Business Policy','No','Yes'). "
        "Returns whether the policy is a personal line."
    ),
)
def single_classify(req: PolicyClassifyRequest) -> PolicyClassifyResult:
    return classify_policy(req)


@router.post(
    "/classify/bulk",
    response_model=list[PolicyClassifyResult],
    summary="Classify multiple policy types",
)
def bulk_classify(req: BulkPolicyRequest) -> list[PolicyClassifyResult]:
    return classify_bulk(req.policies)
