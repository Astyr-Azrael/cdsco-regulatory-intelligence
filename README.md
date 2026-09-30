# CDSCO Regulatory Intelligence

Entity-Centric Drug Regulatory Intelligence from Fragmented CDSCO Alerts is an academic data-engineering project that reconstructs regulator-published drug records as canonical drugs, manufacturers, batches and time-linked events while preserving source provenance.

The current frontend is a working research-interface demo. It contains six manually checked sample rows from official CDSCO March–May 2025 NSQ alert PDFs. The crawler, extraction, NLP, entity-resolution, PostgreSQL and API folders follow the planned architecture and are clearly scaffolded where implementation still requires data audit and evaluation.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

## API scaffold

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

## Important interpretation rule

This project organizes information published by authorized regulators. It does not determine whether a medicine or manufacturer is safe or unsafe, and it does not provide medical advice.
