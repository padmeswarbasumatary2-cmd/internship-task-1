# Integration Handoff

## Backend
- Project folder: `backend/`
- Run command: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Build command: `python -m pytest backend/tests/test_analysis_engine.py -q`
- Health endpoint: `GET /api/health`
- API routes:
  - `GET /api/health`
  - `POST /api/upload`
  - `POST /api/upload-file` (multipart document upload)
  - `GET /api/resumes/{id}`
  - `POST /api/analyze`
  - `GET /api/analyses` (live saved-analysis list for the dashboard)
  - `GET /api/analyses/{id}`

## Frontend
- Project folder: `frontend/`
- Dev command: `npm --prefix frontend run dev`
- Build command: `npm --prefix frontend run build`
- API seam: `frontend/src/api/index.ts` (typed live client)
- Mock files removed during live wiring: `frontend/src/api/mockClient.ts`, `frontend/src/mocks/data.ts`; the prior placeholder `frontend/src/api/liveClient.ts` was replaced by typed `frontend/src/api/client.ts`
- Shared types: `frontend/src/api/types.ts`

## Database
- Type: PostgreSQL
- Migration tool: Alembic
- Directory: `backend/migrations/`
- Connection env vars: `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- Requirement: no seed data during scaffold or migrations

## Service classification
- Essential: resume analysis, health checks, file upload, database persistence, storage access
- Enhancement: case history exports, job recommendation tuning, analytics dashboards

## Shared implementation notes
- Live-data wiring should replace the mock client in `frontend/src/api/index.ts` without rewriting page components.
- No test-only or debug-only data should be committed beyond the approved mock state.

## Integration work recorded
- Added Alembic schema migration for `jobs`, `resumes`, and `analyses`, with foreign keys, score constraint, uniqueness, and query indexes. No row-insertion migration or persisted sample content was added.
- Added follow-up Alembic migration for stored extracted profile and transparent score-factor/recommendation columns.
- Added SQLAlchemy persistence for upload and analysis routes; `DATABASE_URL` selects PostgreSQL, with SQLite as an unconfigured local fallback.
- Added multipart PDF/DOCX/TXT/image ingestion, OCR routes and parsing, regular-expression profile extraction, skill aliases, and the explicit weighted scoring baseline.
- Replaced demo dashboard content with typed requests through `/api`; Vite proxies to `http://localhost:8000`.
- Added API route smoke coverage in `backend/tests/test_api.py`.
- Feature behavior, prerequisites, and non-implemented ML ambitions are documented in `docs/analysis-scope.md`.
- Custom/fine-tuned NER, transformer embeddings, a true skill knowledge graph, vector search, blob storage, and validated fairness auditing remain out of scope because no model, training data, or service credentials were supplied. Scores are heuristic decision support and not an automated hiring recommendation.
- OCR needs a Tesseract system binary on the API host in addition to Python dependencies.
- **Verification pending:** this VS Code session reports no attached task terminal. Alembic migration application, pytest/frontend build, backend route probes, and concurrent browser verification have not run. Keep `.azure/project-plan.md` status as `In Progress` until those checks pass.
- To apply schema from the repository root: `python -m alembic -c backend/alembic.ini upgrade head`.
- Backend run command from the `backend/` directory: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`.
