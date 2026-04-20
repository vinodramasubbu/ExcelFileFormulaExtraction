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
