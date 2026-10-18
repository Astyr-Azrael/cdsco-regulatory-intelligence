# Installation and deployment guide

## Local demonstration

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r requirements.txt
backend\.venv\Scripts\python.exe scripts\load_database.py
backend\.venv\Scripts\python.exe scripts\restore_portal_snapshot.py
backend\.venv\Scripts\python.exe scripts\run_entity_resolution.py
backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

In a second terminal:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\frontend.ps1 install
powershell -ExecutionPolicy Bypass -File scripts\frontend.ps1 dev
```

Open `http://127.0.0.1:5173`. Node 20.19 or Node 22.12 and newer is required. The helper can use the bundled Node 24 runtime on this computer. The frozen database/evidence must be supplied in the submission bundle. Live current-source acquisition remains an optional separate command.

## PostgreSQL and migrations

For a new database:

```powershell
$env:DATABASE_URL="postgresql+psycopg://cdsco:password@localhost:5432/cdsco"
backend\.venv\Scripts\python.exe -m alembic upgrade head
```

For an existing pre-Alembic demo database whose tables already match the baseline:

```powershell
backend\.venv\Scripts\python.exe -m alembic stamp 20261004_0001
```

Frequently searched raw, normalized, status, type and relationship fields carry database indexes. `pgvector` is not installed because embedding matching was not retained.

## Docker Compose

Copy `.env.example` to `.env`, replace the password and trusted origin, then run:

```powershell
docker compose up --build -d
# After the API is ready, load the preserved corpus into PostgreSQL:
docker compose exec api python scripts/load_database.py
docker compose exec api python scripts/restore_portal_snapshot.py
docker compose exec api python scripts/run_entity_resolution.py
```

Docker and PostgreSQL execution are not verified on this machine. The following describes configured behavior only. The stack exposes the frontend on `http://localhost:8080`, the API on `http://localhost:8000`, and PostgreSQL on port 5432. The API waits for a healthy database and applies Alembic migrations before startup.

The compose file is production-oriented configuration, but local HTTP is not a public HTTPS deployment. Put a TLS-terminating reverse proxy or managed load balancer in front of the frontend, restrict `CORS_ORIGINS` to the final HTTPS origin, keep secrets outside source control, and configure backups before public deployment.

## Administrative ingestion

Ingestion scripts are not exposed through the web application. Run them in an administrative job/container with bounded source parameters. Persist `data/raw` and database storage, capture exit status and retain ingestion-run records.

## Verification

```powershell
backend\.venv\Scripts\python.exe -m pytest -q
powershell -ExecutionPolicy Bypass -File scripts\frontend.ps1 build
```

Verify `/health`, entity search, entity histories, official links, empty/error states and repeated ingestion before release.
