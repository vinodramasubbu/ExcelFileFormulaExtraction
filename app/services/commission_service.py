"""
Commission calculation service.

Replicates the business logic from the Commissions sheet:

  Bonus rate lookup  (F5:F14)
    Spreadsheet formula: XLOOKUP(E5, Commission_Level, Bonus_Rate, , -1)
    Logic: find the largest commission threshold that is <= sales_amount,
           then return the corresponding bonus rate.  Returns 0 if sales
           are below the lowest tier.

  Total with bonus   (G5:G14)
    Spreadsheet formula: E5 + (E5 * F5)
    Logic: total = sales_amount + sales_amount * bonus_rate

  Branch totals      (E18:E20)
    Spreadsheet formula: SUMIF($D$5:$D$14, C18, $G$5:$G$14)
    Logic: sum total_with_bonus for each branch

  Grand total        (E21)
    Spreadsheet formula: SUM(E18:E20)

  Statistics         (E22:E24)
    AVERAGE, MODE.SNGL, MEDIAN over G5:G14

  Display name       (Tables!D2:D11)
    Spreadsheet formula: CONCAT(Commissions!C5," ",Commissions!B5,", ",Commissions!D5)
    Logic: "FirstName LastName, Branch"
"""

from collections import Counter
from statistics import mean, median

from app.data.reference_data import COMMISSION_TIERS
from app.schemas import (
    BranchSummary,
    CommissionRequest,
    CommissionResult,
    CommissionSummaryResponse,
)


def lookup_bonus_rate(sales_amount: float) -> float:
    """Replicate XLOOKUP(sales, Commission_Level, Bonus_Rate, , -1).

    Finds the largest threshold <= sales_amount.
    Returns 0.0 when sales_amount is below the lowest tier.
    """
    matched_rate = 0.0
    for tier in COMMISSION_TIERS:
        if sales_amount >= tier["threshold"]:
            matched_rate = tier["rate"]
        else:
            break  # tiers are sorted ascending; no need to continue
    return matched_rate


def calculate_total_with_bonus(sales_amount: float, bonus_rate: float) -> float:
    """Replicate Commissions!G = E + (E * F)."""
    return sales_amount + (sales_amount * bonus_rate)


def format_display_name(first_name: str, last_name: str, branch: str) -> str:
    """Replicate Tables!D CONCAT formula: 'First Last, Branch'."""
    return f"{first_name} {last_name}, {branch}"


def calculate_commission(agent: CommissionRequest) -> CommissionResult:
    """Process a single agent row through the full formula chain."""
    bonus_rate = lookup_bonus_rate(agent.sales_amount)
    total = calculate_total_with_bonus(agent.sales_amount, bonus_rate)
    display = format_display_name(agent.first_name, agent.last_name, agent.branch)

    return CommissionResult(
        agent_id=agent.agent_id,
        first_name=agent.first_name,
        last_name=agent.last_name,
        branch=agent.branch,
        sales_amount=agent.sales_amount,
        bonus_rate=bonus_rate,
        total_with_bonus=total,
        display_name=display,
    )


def calculate_bulk_summary(agents: list[CommissionRequest]) -> CommissionSummaryResponse:
    """Replicate the full Commissions sheet: per-agent results + summary block."""
    results = [calculate_commission(a) for a in agents]
    totals = [r.total_with_bonus for r in results]

    # SUMIF by branch  (E18:E20)
    branch_map: dict[str, float] = {}
    for r in results:
        branch_map[r.branch] = branch_map.get(r.branch, 0.0) + r.total_with_bonus
    branch_summaries = [
        BranchSummary(branch=b, total=t) for b, t in sorted(branch_map.items())
    ]

    # Grand total  (E21)
    grand_total = sum(t.total for t in branch_summaries)

    # Statistics  (E22:E24)
    avg = mean(totals) if totals else 0.0
    med = median(totals) if totals else 0.0

    # MODE.SNGL – most frequent value; None when no value repeats
    counts = Counter(totals)
    most_common = counts.most_common()
    mode_val = most_common[0][0] if most_common and most_common[0][1] > 1 else None

    return CommissionSummaryResponse(
        agent_results=results,
        branch_totals=branch_summaries,
        grand_total=grand_total,
        average=avg,
        mode=mode_val,
        median=med,
    )
