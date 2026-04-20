"""
Unit tests that verify the API produces the same results as the spreadsheet.

Test data is taken directly from the workbook rows to ensure parity.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.commission_service import (
    calculate_commission,
    format_display_name,
    lookup_bonus_rate,
    calculate_total_with_bonus,
    calculate_bulk_summary,
)
from app.services.policy_service import classify_policy
from app.schemas import CommissionRequest, PolicyClassifyRequest

client = TestClient(app)


# ── lookup_bonus_rate (XLOOKUP with -1 match mode) ─────────────────

class TestBonusRateLookup:
    """Spreadsheet: XLOOKUP(sales, Commission_Level, Bonus_Rate, , -1)"""

    def test_below_lowest_tier(self):
        # Sales < 3000 → no matching tier → 0
        assert lookup_bonus_rate(2000) == 0.0

    def test_exact_tier_boundary(self):
        # Sales == 3000 → tier 1 → 1.5 %
        assert lookup_bonus_rate(3000) == 0.015

    def test_between_tiers(self):
        # 3000 < 4000 < 6000 → still tier 1
        assert lookup_bonus_rate(4000) == 0.015

    def test_mid_tier(self):
        # 6000 <= 7000 < 9000 → tier 2
        assert lookup_bonus_rate(7000) == 0.0175

    def test_top_tier(self):
        # 15000 → tier 5 → 2.5 %
        assert lookup_bonus_rate(15000) == 0.025

    def test_above_top_tier(self):
        # 20000 > 15000 → still tier 5
        assert lookup_bonus_rate(20000) == 0.025


# ── calculate_total_with_bonus (G = E + E*F) ───────────────────────

class TestTotalWithBonus:
    """Spreadsheet: Commissions!G5 = E5 + (E5 * F5)"""

    def test_known_row(self):
        # Agent 101: sales=8000, rate=0.0175 → 8000+140 = 8140
        assert calculate_total_with_bonus(8000, 0.0175) == 8140.0

    def test_zero_rate(self):
        assert calculate_total_with_bonus(1000, 0.0) == 1000.0


# ── format_display_name (CONCAT) ───────────────────────────────────

class TestDisplayName:
    """Spreadsheet: Tables!D2 = CONCAT(C5," ",B5,", ",D5)"""

    def test_format(self):
        assert format_display_name("Bob", "Lingle", "Cameron Park") == "Bob Lingle, Cameron Park"


# ── Full single-agent calculation (end-to-end) ─────────────────────

class TestSingleCommission:
    """Verify with actual spreadsheet row data."""

    def test_agent_101_sales_8000(self):
        # Row 5: Lingle Bob, Cameron Park, sales=8000
        result = calculate_commission(CommissionRequest(
            agent_id=101, first_name="Bob", last_name="Lingle",
            branch="Cameron Park", sales_amount=8000,
        ))
        assert result.bonus_rate == 0.0175
        assert result.total_with_bonus == 8140.0
        assert result.display_name == "Bob Lingle, Cameron Park"

    def test_agent_with_low_sales(self):
        # sales=4000 → tier 1 (0.015) → total = 4060
        result = calculate_commission(CommissionRequest(
            agent_id=119, first_name="Juan", last_name="Taylor",
            branch="Granite Bay", sales_amount=4000,
        ))
        assert result.bonus_rate == 0.015
        assert result.total_with_bonus == 4060.0

    def test_agent_with_high_sales(self):
        # sales=12000 → tier 4 (0.0225) → total = 12270
        result = calculate_commission(CommissionRequest(
            agent_id=125, first_name="Cheryl", last_name="Nevens",
            branch="Cameron Park", sales_amount=12000,
        ))
        assert result.bonus_rate == 0.0225
        assert result.total_with_bonus == 12270.0


# ── Bulk summary with branch totals & statistics ───────────────────

class TestBulkSummary:
    """Replicate the summary block (E18:E24) from the Commissions sheet."""

    @pytest.fixture
    def sample_agents(self) -> list[CommissionRequest]:
        return [
            CommissionRequest(agent_id=1, first_name="A", last_name="X",
                              branch="Cameron Park", sales_amount=4000),
            CommissionRequest(agent_id=2, first_name="B", last_name="Y",
                              branch="Cameron Park", sales_amount=4000),
            CommissionRequest(agent_id=3, first_name="C", last_name="Z",
                              branch="Folsom", sales_amount=8000),
        ]

    def test_branch_totals(self, sample_agents):
        summary = calculate_bulk_summary(sample_agents)
        branch_map = {b.branch: b.total for b in summary.branch_totals}
        # Cameron Park: 2 × 4060 = 8120
        assert branch_map["Cameron Park"] == 8120.0
        # Folsom: 8140
        assert branch_map["Folsom"] == 8140.0

    def test_grand_total(self, sample_agents):
        summary = calculate_bulk_summary(sample_agents)
        assert summary.grand_total == 8120.0 + 8140.0

    def test_average(self, sample_agents):
        summary = calculate_bulk_summary(sample_agents)
        expected_avg = (4060 + 4060 + 8140) / 3
        assert abs(summary.average - expected_avg) < 0.01

    def test_mode_with_repeat(self, sample_agents):
        summary = calculate_bulk_summary(sample_agents)
        # 4060 appears twice → mode = 4060
        assert summary.mode == 4060.0

    def test_median(self, sample_agents):
        summary = calculate_bulk_summary(sample_agents)
        # sorted: [4060, 4060, 8140] → median = 4060
        assert summary.median == 4060.0


# ── Policy classification (IF formula) ─────────────────────────────

class TestPolicyClassify:
    """Spreadsheet: IF(E="Business Policy","No","Yes")"""

    def test_business_policy(self):
        result = classify_policy(PolicyClassifyRequest(policy_type="Business Policy"))
        assert result.is_personal_line is False
        assert result.label == "No"

    def test_automobile(self):
        result = classify_policy(PolicyClassifyRequest(policy_type="Automobile"))
        assert result.is_personal_line is True
        assert result.label == "Yes"

    def test_health(self):
        result = classify_policy(PolicyClassifyRequest(policy_type="Health"))
        assert result.is_personal_line is True


# ── HTTP endpoint smoke tests ──────────────────────────────────────

class TestEndpoints:
    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200

    def test_single_commission_endpoint(self):
        r = client.post("/api/commissions/calculate", json={
            "agent_id": 101, "first_name": "Bob", "last_name": "Lingle",
            "branch": "Cameron Park", "sales_amount": 8000,
        })
        assert r.status_code == 200
        assert r.json()["bonus_rate"] == 0.0175

    def test_policy_classify_endpoint(self):
        r = client.post("/api/policies/classify", json={"policy_type": "Automobile"})
        assert r.status_code == 200
        assert r.json()["is_personal_line"] is True

    def test_reference_data_endpoint(self):
        r = client.get("/api/reference/")
        assert r.status_code == 200
        data = r.json()
        assert len(data["commission_tiers"]) == 5
        assert "Automobile" in data["policy_types"]
