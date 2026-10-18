"""FastAPI entrypoint for the CDSCO regulatory intelligence API."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import analytics, batches, drugs, entities, events, manufacturers, search, sources, usage
from backend.app.database.session import create_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_database()
    yield

app = FastAPI(
    title="CDSCO Regulatory Intelligence API",
    description="Provenance-preserving research API backed by extracted CDSCO regulatory rows.",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

for router in (search.router, drugs.router, manufacturers.router, batches.router, events.router, analytics.router, sources.router, entities.router, usage.router):
    app.include_router(router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data_scope": "indexed-regulatory-corpus"}
