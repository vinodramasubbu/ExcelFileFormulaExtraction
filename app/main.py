"""
Central Sierra Insurance – Commission & Policy API

Reconstructs the business logic from test-datafile-with formula.xlsx
as a set of JSON APIs.
"""

from fastapi import FastAPI

from app.routes.commissions import router as commissions_router
from app.routes.policies import router as policies_router
from app.routes.reference import router as reference_router

app = FastAPI(
    title="Central Sierra Insurance – Commission API",
    description=(
        "API that replicates the spreadsheet formulas from "
        "test-datafile-with formula.xlsx.  "
        "Covers commission calculation, policy classification, "
        "and reference data lookups."
    ),
    version="1.0.0",
)

app.include_router(commissions_router)
app.include_router(policies_router)
app.include_router(reference_router)


@app.get("/health", tags=["Health"])
def health() -> dict:
    return {"status": "ok"}
