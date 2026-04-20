"""
Reference data extracted from the 'Tables' sheet of the workbook.

Source: test-datafile-with formula.xlsx -> Tables tab
- Commission_Level named range: Tables!$A$2:$A$6
- Bonus_Rate named range:       Tables!$B$2:$B$6
- Policy Types list:            Tables!A10:A15
"""

# Commission lookup table (sorted ascending by threshold).
# XLOOKUP with match_mode=-1 finds the largest threshold <= the sales value.
# Spreadsheet cells: Tables!A2:A6 (Commission_Level), Tables!B2:B6 (Bonus_Rate)
COMMISSION_TIERS: list[dict] = [
    {"threshold": 3_000,  "rate": 0.015},   # 1.5 %
    {"threshold": 6_000,  "rate": 0.0175},  # 1.75 %
    {"threshold": 9_000,  "rate": 0.019},   # 1.9 %
    {"threshold": 12_000, "rate": 0.0225},  # 2.25 %
    {"threshold": 15_000, "rate": 0.025},   # 2.5 %
]

# Valid policy types from Tables!A10:A15
POLICY_TYPES: list[str] = [
    "Automobile",
    "Business Policy",
    "Health",
    "Homeowners",
    "Life",
    "Renters",
]

# Branches appearing in the Commissions sheet
BRANCHES: list[str] = [
    "Cameron Park",
    "Folsom",
    "Granite Bay",
]
