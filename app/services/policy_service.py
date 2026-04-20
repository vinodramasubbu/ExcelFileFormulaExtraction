"""
Policy classification service.

Replicates the logic from the 'By Policy' sheet:

  Personal-line flag  (F7:F27)
    Spreadsheet formula: IF(E7="Business Policy","No","Yes")
    Logic: a policy is a personal line unless its type is "Business Policy".
"""

from app.schemas import PolicyClassifyRequest, PolicyClassifyResult


def classify_policy(req: PolicyClassifyRequest) -> PolicyClassifyResult:
    """Replicate IF(E="Business Policy","No","Yes")."""
    is_personal = req.policy_type != "Business Policy"
    return PolicyClassifyResult(
        policy_type=req.policy_type,
        is_personal_line=is_personal,
        label="Yes" if is_personal else "No",
    )


def classify_bulk(requests: list[PolicyClassifyRequest]) -> list[PolicyClassifyResult]:
    return [classify_policy(r) for r in requests]
