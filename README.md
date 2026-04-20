# Commission & Policy API

A FastAPI application that replicates the business logic from the
`test-datafile-with formula.xlsx` spreadsheet as a set of JSON APIs.

## How This App Was Built

This application was built entirely by GitHub Copilot, guided by a custom
[`.github/copilot-instructions.md`](.github/copilot-instructions.md) file that
defines a structured workflow for turning spreadsheets into APIs.

### Step 1 – Spreadsheet Analysis (Formula Extraction)

Copilot parsed the `.xlsx` file directly by reading its internal XML
(`xl/worksheets/*.xml`, `xl/workbook.xml`, `xl/sharedStrings.xml`). For each
of the 3 sheets it identified:

- **Cell references** and their values
- **58 formulas** (27 normal, 31 shared/drag-filled)
- **Named ranges**: `Commission_Level` → `Tables!$A$2:$A$6`,
  `Bonus_Rate` → `Tables!$B$2:$B$6`
- **Cross-sheet dependencies**: Tables sheet feeds lookups into Commissions;
  Commissions data feeds CONCAT formulas back into Tables
- **Functions used**: `XLOOKUP`, `CONCAT`, `IF`, `SUMIF`, `SUM`, `AVERAGE`,
  `MODE.SNGL`, `MEDIAN`

### Step 2 – Business Logic Interpretation

Following the copilot instructions' *Formula Interpretation Rules*, each
formula was translated from Excel syntax into plain-English business rules:

| Excel Formula | Business Meaning |
|---|---|
| `XLOOKUP(E5, Commission_Level, Bonus_Rate, , -1)` | Look up the bonus rate tier for this agent's sales amount (largest threshold ≤ sales) |
| `E5 + (E5 * F5)` | Total compensation = sales + bonus |
| `SUMIF($D$5:$D$14, C18, $G$5:$G$14)` | Sum all agent totals for a given branch |
| `SUM(E18:E20)` | Grand total across all branches |
| `AVERAGE(G5:G14)` | Average agent compensation |
| `MODE.SNGL(G5:G14)` | Most common compensation value |
| `MEDIAN(G5:G14)` | Median agent compensation |
| `IF(E7="Business Policy","No","Yes")` | Flag whether a policy is a personal line |
| `CONCAT(C5," ",B5,", ",D5)` | Build display name: "First Last, Branch" |

### Step 3 – API Reconstruction

Following the copilot instructions' *API Reconstruction Principles* and
*Preferred API Design Style*, the formulas were grouped into business
capabilities and mapped to API endpoints:

- **Lookup tables** → externalized into `app/data/reference_data.py`
- **Commission formulas** → deterministic functions in
  `app/services/commission_service.py`
- **Policy classification** → `app/services/policy_service.py`
- **Pydantic models** → `app/schemas.py` with field-level traceability back to
  spreadsheet columns (e.g. `sales_amount` ← `Commissions!E`)
- **FastAPI routes** → `app/routes/` with one router per business domain
- **Unit tests** → 24 tests using actual spreadsheet values to verify parity

### Step 4 – Validation

Tests were run to confirm the API produces the same outputs as the spreadsheet
for every formula. Sample API responses are captured in the
[Sample API Test Results](#sample-api-test-results) section below.

## What the Spreadsheet Does

The workbook tracks insurance agents, calculates tiered commission bonuses on
sales, classifies policy types, and produces branch-level summary statistics.

| Sheet | Purpose |
|---|---|
| **Commissions** | Agent roster with sales amounts. Calculates a tiered bonus rate (XLOOKUP), computes total-with-bonus, then summarises by branch (SUMIF) with AVERAGE, MODE, and MEDIAN. |
| **By Policy** | Lists agents by policy type. An IF formula flags each row as a personal line or business line. |
| **Tables** | Reference data: 5-tier commission lookup table, valid policy types, and CONCAT formulas that build agent display names. |

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/api/reference/` | GET | Commission tiers, policy types, branches |
| `/api/commissions/calculate` | POST | Bonus rate + total for a single agent |
| `/api/commissions/summary` | POST | Bulk calculation with branch totals and statistics |
| `/api/policies/classify` | POST | Classify a single policy type as personal or business |
| `/api/policies/classify/bulk` | POST | Classify multiple policy types |

## Project Structure

```
app/
  main.py                          # FastAPI entry point
  schemas.py                       # Pydantic request/response models
  data/
    reference_data.py              # Lookup tables from the Tables sheet
  services/
    commission_service.py          # XLOOKUP, bonus calc, SUMIF, stats
    policy_service.py              # IF-based policy classification
  routes/
    commissions.py                 # Commission endpoints
    policies.py                    # Policy endpoints
    reference.py                   # Reference data endpoint
tests/
  test_commissions.py              # 24 unit + HTTP tests
test.http                          # REST Client manual test file
.env                               # Local environment config
requirements.txt                   # Python dependencies
```

## Prerequisites

- Python 3.11+

## Setup

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.  
Interactive Swagger docs are at `http://127.0.0.1:8000/docs`.

## Run the Tests

```bash
python -m pytest tests/ -v
```

Expected output: **24 passed**.

## Manual Testing with REST Client

Open `test.http` in VS Code with the
[REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
extension installed. Make sure the server is running, then click
**Send Request** above any request block.

The file includes ready-made requests for every endpoint using real data from
the spreadsheet.

## Sample API Test Results

The following responses were captured by calling each endpoint with real spreadsheet data.

### `GET /health`

```json
{
  "status": "ok"
}
```

### `GET /api/reference/`

```json
{
  "commission_tiers": [
    { "threshold": 3000.0, "rate": 0.015 },
    { "threshold": 6000.0, "rate": 0.0175 },
    { "threshold": 9000.0, "rate": 0.019 },
    { "threshold": 12000.0, "rate": 0.0225 },
    { "threshold": 15000.0, "rate": 0.025 }
  ],
  "policy_types": ["Automobile", "Business Policy", "Health", "Homeowners", "Life", "Renters"],
  "branches": ["Cameron Park", "Folsom", "Granite Bay"]
}
```

### `POST /api/commissions/calculate`

**Request:**
```json
{
  "agent_id": 101, "first_name": "Bob", "last_name": "Lingle",
  "branch": "Cameron Park", "sales_amount": 8000
}
```

**Response:**
```json
{
  "agent_id": 101,
  "first_name": "Bob",
  "last_name": "Lingle",
  "branch": "Cameron Park",
  "sales_amount": 8000.0,
  "bonus_rate": 0.0175,
  "total_with_bonus": 8140.0,
  "display_name": "Bob Lingle, Cameron Park"
}
```

### `POST /api/commissions/summary`

**Request:** 10 agents from the spreadsheet (see `test.http` for full payload).

**Response (summary section):**
```json
{
  "branch_totals": [
    { "branch": "Cameron Park", "total": 36686.0 },
    { "branch": "Folsom", "total": 21480.0 },
    { "branch": "Granite Bay", "total": 19322.5 }
  ],
  "grand_total": 77488.5,
  "average": 7748.85,
  "mode": 8140.0,
  "median": 7631.25
}
```

### `POST /api/policies/classify`

**Request:**
```json
{ "policy_type": "Automobile" }
```

**Response:**
```json
{
  "policy_type": "Automobile",
  "is_personal_line": true,
  "label": "Yes"
}
```

**Request:**
```json
{ "policy_type": "Business Policy" }
```

**Response:**
```json
{
  "policy_type": "Business Policy",
  "is_personal_line": false,
  "label": "No"
}
```

### `POST /api/policies/classify/bulk`

**Request:**
```json
{
  "policies": [
    { "policy_type": "Automobile" }, { "policy_type": "Business Policy" },
    { "policy_type": "Health" }, { "policy_type": "Homeowners" },
    { "policy_type": "Life" }, { "policy_type": "Renters" }
  ]
}
```

**Response:**
```json
[
  { "policy_type": "Automobile", "is_personal_line": true, "label": "Yes" },
  { "policy_type": "Business Policy", "is_personal_line": false, "label": "No" },
  { "policy_type": "Health", "is_personal_line": true, "label": "Yes" },
  { "policy_type": "Homeowners", "is_personal_line": true, "label": "Yes" },
  { "policy_type": "Life", "is_personal_line": true, "label": "Yes" },
  { "policy_type": "Renters", "is_personal_line": true, "label": "Yes" }
]
```
