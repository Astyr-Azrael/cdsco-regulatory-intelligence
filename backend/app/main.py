"""FastAPI entrypoint for the CDSCO regulatory intelligence API scaffold."""

from fastapi import FastAPI

from backend.app.api.routes import analytics, batches, drugs, events, manufacturers, search, sources

app = FastAPI(
    title="CDSCO Regulatory Intelligence API",
    description="Provenance-preserving research API. Current endpoints are scaffolding for the verified sample dataset.",
    version="0.2.0",
)

for router in (search.router, drugs.router, manufacturers.router, batches.router, events.router, analytics.router, sources.router):
    app.include_router(router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data_scope": "verified-sample"}
