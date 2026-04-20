"""
Pydantic models for request / response payloads.

Mapping from spreadsheet columns to API fields:
  Commissions tab
    A -> agent_id          (ID)
    B -> last_name         (Last Name)
    C -> first_name        (First Name)
    D -> branch            (Branch)
    E -> sales_amount      (Sales)
    F -> bonus_rate         [calculated]
    G -> total_with_bonus   [calculated]

  By Policy tab
    E -> policy_type       (Type of Policy)
    F -> is_personal_line   [calculated]
"""

from pydantic import BaseModel, Field


# ── Commission calculation ──────────────────────────────────────────

class CommissionRequest(BaseModel):
    """Single agent commission input.  Mirrors one row of the Commissions sheet."""
    agent_id: int = Field(..., description="Agent ID (Commissions!A)")
    first_name: str = Field(..., description="First name (Commissions!C)")
    last_name: str = Field(..., description="Last name (Commissions!B)")
    branch: str = Field(..., description="Branch office (Commissions!D)")
    sales_amount: float = Field(..., ge=0, description="Sales amount (Commissions!E)")


class CommissionResult(BaseModel):
    """Calculated result for one agent – replaces columns F & G."""
    agent_id: int
    first_name: str
    last_name: str
    branch: str
    sales_amount: float
    bonus_rate: float = Field(..., description="Looked-up bonus rate (Commissions!F) – from XLOOKUP")
    total_with_bonus: float = Field(..., description="sales + sales*bonus_rate (Commissions!G)")
    display_name: str = Field(..., description="'First Last, Branch' (Tables!D) – from CONCAT")


class BulkCommissionRequest(BaseModel):
    agents: list[CommissionRequest]


class BranchSummary(BaseModel):
    """Mirrors SUMIF rows (Commissions!E18:E20)."""
    branch: str
    total: float


class CommissionSummaryResponse(BaseModel):
    """Mirrors the summary block (Commissions!E18:E24)."""
    agent_results: list[CommissionResult]
    branch_totals: list[BranchSummary]
    grand_total: float = Field(..., description="SUM of branch totals (Commissions!E21)")
    average: float = Field(..., description="AVERAGE of totals (Commissions!E22)")
    mode: float | None = Field(None, description="MODE.SNGL of totals (Commissions!E23)")
    median: float = Field(..., description="MEDIAN of totals (Commissions!E24)")


# ── Policy classification ───────────────────────────────────────────

class PolicyClassifyRequest(BaseModel):
    policy_type: str = Field(..., description="Type of Policy (By Policy!E)")


class PolicyClassifyResult(BaseModel):
    policy_type: str
    is_personal_line: bool = Field(
        ..., description="True unless policy_type is 'Business Policy' (By Policy!F)"
    )
    label: str = Field(..., description="'Yes' or 'No' string for display")


class BulkPolicyRequest(BaseModel):
    policies: list[PolicyClassifyRequest]


# ── Reference data responses ────────────────────────────────────────

class CommissionTier(BaseModel):
    threshold: float
    rate: float


class ReferenceDataResponse(BaseModel):
    commission_tiers: list[CommissionTier]
    policy_types: list[str]
    branches: list[str]
