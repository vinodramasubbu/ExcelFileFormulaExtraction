# Commission & Policy API

A FastAPI application that replicates the business logic from the
`test-datafile-with formula.xlsx` spreadsheet as a set of JSON APIs.

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
