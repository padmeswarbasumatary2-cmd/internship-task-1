# Project Plan

**Status**: In Progress
**Created**: 2026-09-29
**Mode**: NEW
**Execution Mode**: auto

---

## 1. Project Overview

**Goal**: Build an independently testable resume-to-role analysis platform with document text extraction, structured profile hints, canonical skill matching, and transparent fit scoring. The local implementation is a deterministic baseline; trained NLP/NER, embedding search, external storage, and audited hiring models require separate data/services and are not represented as implemented.

**App Type**: SPA + API

**API Login**: No

**Mode**: NEW

**Deployment Plan**: No deployment plan found

---

## 2. Backend — Azure Functions

| Component | Technology |
|-----------|-----------|
| **Language** | Python |
| **Runtime** | CPython |
| **Package Manager** | pip |
| **Test Runner** | pytest |
| **Mocking Library** | unittest.mock |
| **Test Command** | pytest |
| **Orchestration** | docker-compose |

---

## 3. Frontend — Web App

| Component | Technology |
|-----------|-----------|
| **Language** | TypeScript |
| **Framework** | React + Vite |
| **Package Manager** | npm |
| **Test Runner** | vitest |
| **Mocking Library** | vi.mock |
| **Test Command** | npm test |

---

## 4. Services Required

| Azure Service | Role in App | Environment Variable | Default Value (Local) | Classification |
|---------------|------------|---------------------|----------------------|----------------|
| Blob Storage | Store uploaded document files and generated artifacts | STORAGE_CONNECTION_STRING | UseDevelopmentStorage=true | Essential |
| PostgreSQL | Primary data store for resume, job, and analysis records | DATABASE_URL | postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/appdb | Essential |

---

## 5. Prerequisites

### Run

| Tool | Service(s) | Installed | Version |
|------|------------|-----------|---------|
| Python 3.12 | Backend | ❓ | Unknown |
| pip | Backend | ❓ | Unknown |
| Node.js | Frontend | ❓ | Unknown |
| npm | Frontend | ❓ | Unknown |
| Azure CLI | Backend, Frontend | ❓ | Unknown |
| Docker | Backend, Frontend | ❓ | Unknown |
| Docker Compose | Backend, Frontend | ❓ | Unknown |

### Debug

| Tool | Service(s) | Installed | Version |
|------|------------|-----------|---------|
| ms-python.python | Backend | ❓ | Unknown |
| ms-vscode.vscode-typescript-next | Frontend | ❓ | Unknown |
| ms-azuretools.vscode-docker | Backend, Frontend | ❓ | Unknown |

---

## 6. Design System & UI

**Component Library**: Fluent UI v9
**Style Direction**: Modern, low-friction recruiting dashboard with subtle elevation, rounded 8px corners, and scannable summary cards for fast screening decisions.
**Typography**: Inter, system-ui

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#2563eb` | Brand color for primary actions, active navigation, and candidate scoring CTAs |
| `accent` | `#14b8a6` | Secondary highlights for positive fit signals and focus states |
| `surface` | `#f8fafc` | Page and card backgrounds for a clean recruiting workspace |
| `text` | `#111827` | Body and heading text across dashboard views |
| `muted` | `#64748b` | Secondary text, timestamps, and supporting metadata |
| `border` | `#dbe2ea` | Dividers, table borders, and input surfaces |

### Pages

| Page | Route | Purpose | Layout |
|------|-------|---------|--------|
| Dashboard | `/` | Overview of recent resume submissions and job fit summaries | `header + nav + grid + card-list` |
| Results | `/results` | View a detailed resume-to-job analysis and recommendations | `two-column(media+meta) + action-bar` |
| History | `/history` | Review previous analyses and saved candidate records | `table + actions` |
| Settings | `/settings` | Configure workplace defaults and analysis preferences | `form + sidebar` |

### Sample Content

```
Dashboard — candidate summary:
| Candidate | Role | Score | Status |
| A. Patel | Senior Product Designer | 92 | Strong match |
| L. Chen | Frontend Engineer | 84 | Good match |
| S. Ivanov | Data Analyst | 68 | Needs review |

Results — analysis details: Match score: 92 · Missing skills: GraphQL, accessibility audits · Recommended next step: Add quantifiable product impact metrics

History — saved analysis:
| ID | Job Title | Candidate | Score |
| 1042 | Senior Product Designer | A. Patel | 92 |
| 1047 | Frontend Engineer | L. Chen | 84 |
| 1051 | Data Analyst | S. Ivanov | 68 |
```

---

## 7. Project Structure

```
.
├── apps/
│   ├── api/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── app.py
│   └── web/
│       ├── src/
│       ├── public/
│       ├── package.json
│       └── vite.config.ts
├── infra/
│   ├── bicep/
│   └── scripts/
├── docker-compose.yml
├── README.md
├── .azure/
│   ├── project-plan.md
│   └── .preview-temp/
└── package.json
```

---

## 8. Route Definitions

| # | Method | Path | Description | Request Body | Response Body | Status Codes |
|---|--------|------|-------------|-------------|--------------|-------------|
| 1 | GET | `/api/health` | Health check | — | `{ status, services }` | 200, 503 |
| 2 | POST | `/api/upload` | Upload resume file and job description | `{ file, jobDescription }` | `{ resumeId, analysisId }` | 200, 400, 413 |
| 2a | POST | `/api/upload-file` | Upload a PDF, DOCX, TXT, or image resume with a job description | multipart `resume`, `job_description` | `{ resumeId, jobId, analysisId }` | 201, 400 |
| 3 | GET | `/api/resumes/{id}` | Fetch stored resume metadata | — | `{ resume }` | 200, 404 |
| 4 | POST | `/api/analyze` | Run candidate-to-job analysis | `{ resumeId, jobId }` | `{ score, matchedSkills, missingSkills, recommendations }` | 200, 400, 422 |
| 5 | GET | `/api/analyses/{id}` | Fetch detailed analysis result | — | `{ analysis }` | 200, 404 |

---

## 9. Next Steps

1. Run **azure-project-scaffold** to execute this plan
2. Run **azure-project-integrate** to wire the frontend to live data, smoke-test the backend, and create the migrations
3. Run **azure-debug-plan** → **azure-debug-generate** for Docker emulators and VS Code debugging
4. Run the **azure-deploy** agent when ready; it uses **azure-app-onboard** for architecture, cost estimation, IaC generation, provisioning, and health verification
