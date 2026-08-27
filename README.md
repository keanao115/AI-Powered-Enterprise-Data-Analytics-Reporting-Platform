# 🌐 AI-Powered Enterprise Data Analytics & Reporting Platform
### Enterprise-Grade AI Analyst Agent with Deterministic Security Boundaries & Governed Business Intelligence

<p align="center">
  <a href="README.md"><b>繁體中文</b></a> |
  <a href="README_en.md"><b>English</b></a>
</p>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.0-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.10.0-FFF000?style=flat-square&logo=duckdb&logoColor=black)](https://duckdb.org)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-3.6%20Flash-4285F4?style=flat-square&logo=google)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)](https://www.docker.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com)
[![Pytest](https://img.shields.io/badge/Pytest-Passing-brightgreen?style=flat-square&logo=pytest)](https://pytest.org)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

---

## 📖 Executive Summary

**AI-Powered Enterprise Data Analytics & Reporting Platform** is a full-stack, enterprise-ready decision intelligence and automated reporting system. It is engineered from the ground up with **deterministic security boundaries**, **multi-tenant isolation**, and **mathematical fact grounding**.

Traditional Text-to-SQL solutions and LLM data agents suffer from critical enterprise vulnerabilities: prompt injection attacks, accidental schema destructions, cross-tenant data leaks, unmasked PII exposure, and ungrounded hallucinations.

This platform solves these challenges through a strict architectural principle:

> 🔒 **Core Architectural Philosophy: The LLM is an Untrusted Planner**  
> Large Language Models (LLMs) are treated strictly as untrusted proposal generators. The LLM NEVER determines access authorization, query execution permissions, or tenant scopes. All generated SQL queries, Python visualization scripts, and analytical inferences are deterministically validated, rewritten, and executed within **SQL AST Policy Engines**, **Mandatory Row-Level Security (RLS)**, **Dynamic Column-Level Security (CLS)**, and **Double-Sandboxed Execution Environments**.

---

## 🏛️ System Architecture

```mermaid
graph TD
    User([👤 Business User / Analyst]) -->|Natural Language Query| UI[Next.js 14 Modern Dark UI]
    UI -->|REST API / Bearer JWT| Gateway[FastAPI API Gateway]
    
    subgraph Security_Gate [🛡️ Layer 1: Security Screening & Intent Routing]
        Gateway --> Scanner[Multi-Stage Prompt Injection Scanner]
        Scanner --> Clarifier[Ambiguity & Clarification Detector]
        Clarifier --> DomainRouter[6-Domain Intent Router]
    end

    subgraph Agent_Core [🧠 Layer 2: AI Analyst Agent & Text-to-SQL]
        DomainRouter --> Gemini[Google Gemini 3.6 Flash]
        Gemini --> CandidateSQL[DuckDB Candidate Read-Only SQL]
    end

    subgraph Deterministic_Guard [⚙️ Layer 3: Deterministic Security & Governance Boundary]
        CandidateSQL --> ASTPolicy[sqlglot AST Security Policy Engine<br/>(Blocks DDL/DML/System Tables/Unsafe Functions)]
        ASTPolicy --> RLSEngine[Mandatory RLS Query Rewriter<br/>(Injects WHERE tenant_id = :id)]
        RLSEngine --> CLSMasker[Dynamic CLS Column Masker<br/>(SSN / Email / Phone Redaction)]
        CLSMasker --> CostEstimator[EXPLAIN Cost Estimator & Cartesian Guardrail]
    end

    subgraph Engine_Execution [⚡ Layer 4: Read-Only Analytical Engine & Sandbox]
        CostEstimator --> ReadOnlyDuckDB[(DuckDB Read-Only Engine)]
        ReadOnlyDuckDB --> DQEngine[5-Dimension Data Quality Evaluation Engine]
        DQEngine --> PySandbox[Isolated Python Execution Sandbox]
        PySandbox --> Matplotlib[Matplotlib Chart Renderer (Base64)]
    end

    subgraph Grounding_Reporting [📊 Layer 5: Fact Grounding & Artifact Generation]
        Matplotlib --> Grounding[Numerical Fact Grounding Cross-Verification]
        Grounding --> Insights[Gemini Executive Business Insights]
        Insights --> ReportGen[Report Generator (PDF / Excel / CSV)]
        ReportGen --> AuditLog[(Immutable Audit Log & Data Lineage Graph)]
    end

    AuditLog --> UI
```

---

## 🚀 6 Governed Real-World Enterprise Datasets

The platform comes pre-seeded with **6 curated real-world public enterprise datasets** comprising over 24,000+ structured records stored in DuckDB:

| # | Industry Domain | Dataset Name & Publisher | Volume & Tables | Security Classification | Included Tables & Key Analytical Dimensions |
|---|---|---|---|---|---|
| **01** | **E-Commerce & Retail** | [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | 10,600+ rows<br/>(6 tables) | `PUBLIC` | `olist_orders`, `olist_order_items`, `olist_products`, `olist_customers`, `olist_order_payments`, `olist_order_reviews`<br/>*GMV growth trends, AOV, freight costs across states (SP, RJ, MG), delivery delay rates, customer review scores.* |
| **02** | **Urban Mobility** | [NYC TLC Taxi & Limousine](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) | 2,538+ rows<br/>(2 tables) | `PUBLIC` | `nyc_taxi_trips`, `taxi_zones`<br/>*24-hour demand heatmaps, pickup zones, airport vs city trips, fare per mile efficiency, tips & surcharge patterns.* |
| **03** | **Airline Operations** | [U.S. DOT BTS Airline On-Time](https://www.transtats.bts.gov/ONTIME/) | 2,535+ rows<br/>(3 tables) | `PUBLIC` | `bts_flights`, `bts_airlines`, `bts_airports`<br/>*On-time arrival rate (USDOT standard), delay root-causes (Weather, Carrier, NAS, Late Aircraft), hub airport cancellations, worst-performing routes.* |
| **04** | **Healthcare Operations** | [PhysioNet MIMIC-IV Clinical Demo](https://physionet.org/content/mimiciv/) | 3,700+ rows<br/>(4 tables) | `RESTRICTED`<br/>*(w/ Clinical Disclaimer)* | `mimic_patients`, `mimic_admissions`, `mimic_icu_stays`, `mimic_diagnoses`<br/>*Hospital & ICU Length of Stay (LOS), ICD-10 diagnostic distributions, admission types (Emergent vs Elective), insurance coverage.* |
| **05** | **Public Safety** | [City of Chicago Reported Crimes](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2) | 2,522+ rows<br/>(2 tables) | `PUBLIC`<br/>*(w/ Municipal Note)* | `chicago_crimes`, `chicago_districts`<br/>*22 police districts, incident types (Theft, Battery, Assault), arrest rate percentages, temporal crime heatmaps, location descriptions.* |
| **06** | **Financial Markets** | [U.S. SEC EDGAR & Public Markets](https://www.sec.gov/edgar/searchedgar/companysearch) | 2,400+ rows<br/>(3 tables) | `PUBLIC`<br/>*(w/ Financial Disclaimer)* | `market_securities`, `market_daily_prices`, `market_financial_facts`<br/>*Daily equity OHLCV prices, 30-day realized volatility, 50-day moving averages, SEC 10-Q/10-K reported fundamentals, Free Cash Flow (FCF), sector operating margins.* |

---

## ✨ Key Platform Features

### 1. 🤖 AI Analyst Interface & Natural Language Pipeline
- **Autonomous Intent Routing**: `Auto Detect` automatically analyzes query semantics and routes to the appropriate dataset, or users can explicitly select any of the 6 domains.
- **Proactive Clarification**: Automatically triggers clarification dialogs when queries lack necessary dimensions, date ranges, or aggregation metrics.
- **10-Step Transparent Pipeline**: Real-time visualization of security screening, intent resolution, SQL drafting, AST rewriting, execution, sandboxed visualization, and grounding.

### 2. 🛡️ SQL Security Inspector & Policy Simulation Sandbox
- **AST Parsing with `sqlglot`**: Deep inspection of SELECT projections, JOIN hierarchies, WHERE filters, and subquery structures.
- **Persona & RBAC Simulation**: Live role-switching (`ORG_ADMIN`, `ANALYST`, `VIEWER`, `DPO`) to test dynamic RLS injection and CLS masking.
- **Compliance Matrix Checklist**: Automatic compliance readiness verification against `SOC2 Type II`, `ISO 27001`, `HIPAA / PCI-DSS`, and `GDPR / CCPA`.
- **EXPLAIN Cost & Cardinality Guardrails**: Detects unconstrained table scans and Cartesian cross-joins, estimating execution cost before hitting the database.
- **5 Security Presets**: Analytical baseline, PII extraction, destructive DDL injection (`DROP TABLE`), high-cost Cartesian product, and restricted system table access.

### 3. 📂 Governed Dataset Explorer
- **Provenance & Metadata**: Displays publisher details, terms of use, license, checksums, and quality scores.
- **Live Interactive Data Grid**: Dynamic server-side pagination with real-time multi-column search.
- **Column Profiling Statistics**: Data type classification and sample value inspection.
- **One-Click Analyst Prompt Dispatch**: Pre-configured sample questions that seamlessly populate the AI Analyst interface.
- **On-the-Fly CSV Export**: Direct dataset download capability with permission enforcement.

### 4. 📈 Sandboxed Python Visualizations & 5-Dimension Data Quality
- **Double-Sandboxed Python Engine**: Code analyzer validates AST nodes to prohibit `os`, `sys`, `subprocess`, `socket`, `eval`, or `exec`, rendering clean high-resolution Base64 charts with `matplotlib` and `pandas`.
- **Data Quality Engine**: Evaluates null ratios, duplicate records, data freshness, and structural completeness, assigning an automated quality score.

### 5. 🎯 Numerical Fact Grounding & Executive Report Export
- **100% Fact-Checked Claims**: Every numeric claim in the LLM's response is cross-referenced against the raw SQL query result set, flagging unsupported assertions.
- **Structured Executive Insights**: Formatted in executive-level Markdown with Executive Summary, Key Findings, and Actionable Recommendations.
- **Multi-Format Export**: Generates professional **PDF Reports (ReportLab)**, **Excel Spreadsheets (OpenPyXL)**, and **CSV Files**.

### 6. 🔍 Data Provenance & Immutable Audit Logging
- **End-to-End Lineage Graph**: Visualizes the journey from source tables and semantic definitions to AST mutations, execution timings, and final generated artifacts.
- **Compliance Audit Viewer**: Records all user queries, blocked attacks, risk ratings (`LOW`, `CRITICAL`), timestamps, and isolation outcomes.

### 7. 🧪 180+ Benchmark & Evaluation Suite
- Built-in comprehensive evaluation suite executing:
  - **90 Domain Analytical Scenarios** (Complexity L1 to L10)
  - **30 Security & Attack Defense Scenarios** (Prompt Injection, SQL Injection, Privilege Escalation, DoS)
  - **30 Fact-Grounding Verification Scenarios**
  - **30 Ambiguity & Clarification Scenarios**
- Single-click execution from the UI with instant accuracy scoring and KPI breakdown.

---

## 🛠️ Tech Stack

### Backend Architecture
- **Framework**: Python 3.10+ / FastAPI 0.110.0
- **Analytics Database Engine**: DuckDB 0.10.0 (High-performance embedded OLAP)
- **Application Database**: PostgreSQL 16 / SQLite (via SQLAlchemy 2.0 & aiosqlite)
- **SQL AST Engine**: `sqlglot` 23.0+
- **LLM Gateway**: Google Gemini (`gemini-3.6-flash`) / OpenAI / Mock Provider
- **Data & Visualization**: Pandas, NumPy, Matplotlib, Seaborn
- **Reporting Services**: ReportLab (PDF), OpenPyXL (Excel), CSV
- **Auth & Security**: JWT (python-jose), Argon2 / BCrypt (passlib)
- **Observability**: OpenTelemetry SDK, Prometheus Client

### Frontend Architecture
- **Framework**: Next.js 14 (App Router) / React 18
- **Language**: TypeScript 5.0
- **Styling & Components**: Tailwind CSS 3.4, Lucide React
- **Internationalization (i18n)**: Seamless bilingual switching (Traditional Chinese `zh-TW` / English `en`)

---

## 📁 Project Directory Structure

```plaintext
.
├── backend/
│   ├── app/
│   │   ├── ai/                      # AI Core: Agent State Machine, Prompts, Providers, Tools
│   │   │   ├── agent/               # Analyst Agent, Ambiguity Detector, State
│   │   │   ├── providers/           # Gemini / OpenAI / Mock LLM Gateways
│   │   │   └── tools/               # Semantic, Schema, SQL & Visualization Tool Registries
│   │   ├── analytics/               # Data Quality, Claim Grounding, Provenance Service
│   │   ├── api/v1/                  # REST API Routes (queries, datasets, security, reports, etc.)
│   │   ├── core/                    # Config, DB connections, RBAC permissions, Tenant context
│   │   ├── evaluation/              # 180+ Production Benchmark Runner
│   │   ├── ingestion/               # 6 Curated Dataset Ingestion & DuckDB Pipelines
│   │   ├── query_engine/            # AST Policy, RLS Enforcer, CLS Masker, Cost Estimator
│   │   ├── reporting/               # PDF / Excel / CSV Document Generators
│   │   ├── sandbox/                 # Sandboxed Python Runner & AST Static Validator
│   │   ├── security/                # Prompt Injection Scanner, Data Masking, Audit Logger
│   │   ├── semantic/                # Governed Dataset Catalog, Semantic Layer & Metric Registries
│   │   └── main.py                  # FastAPI Main Entrypoint & Lifecycle Initializer
│   ├── seed/
│   │   └── seed_data.py             # Automatic Synthetic Data & Table Seeder
│   └── requirements.txt             # Backend Python Dependencies
│
├── frontend/
│   ├── src/
│   │   ├── app/                     # Next.js Pages & Layouts (page.tsx, layout.tsx)
│   │   ├── components/              # Core UI Components
│   │   │   ├── AIAnalystInterface.tsx     # AI Analyst Main Dialog & Step Pipeline
│   │   │   ├── DatasetExplorer.tsx        # 6-Dataset Explorer & Live Preview
│   │   │   ├── SQLInspector.tsx           # SQL AST Security & Policy Sandbox
│   │   │   ├── DataProvenanceView.tsx     # Data Lineage Visualizer
│   │   │   ├── DataDictionary.tsx         # Enterprise Data Dictionary & Classifications
│   │   │   ├── AuditLogViewer.tsx         # Compliance Audit Logs
│   │   │   ├── EvaluationDashboard.tsx    # 180+ Evaluation Benchmark Suite
│   │   │   └── LanguageSelector.tsx       # Bilingual Language Switcher
│   │   ├── lib/api.ts               # Frontend API Client
│   │   ├── locales/                 # i18n Dictionaries (zh-TW.ts, en.ts, LanguageContext.tsx)
│   │   └── types/index.ts           # TypeScript Interfaces & Types
│   ├── package.json
│   └── tailwind.config.js
│
├── docs/                            # System Architecture, Threat Model, Backup & Restore
├── tests/                           # Automated Test Suite (e2e, security, tenancy)
├── analytics_demo.duckdb            # Pre-seeded DuckDB Analytics Database
├── docker-compose.yml               # Multi-container Docker Orchestration
├── Dockerfile.backend               # Backend Container Build
├── Dockerfile.frontend              # Frontend Container Build
├── Makefile                         # Developer CLI & Automation Shortcuts
└── README.md                        # Documentation (Traditional Chinese)
```

---

## ⚡ Quick Start Guide

### 📋 Prerequisites
- **Python**: 3.10+
- **Node.js**: 18.0+ (with npm or pnpm)
- **Docker & Docker Compose** (Optional, for containerized deployment)

---

### Option 1: Docker Compose (Recommended)

1. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   ```

2. **Build and Launch Containers**:
   ```bash
   docker-compose up -d --build
   ```

3. **Access Services**:
   - 💻 **Web Application**: `http://localhost:3300` (or `http://localhost:3000`)
   - 🔌 **FastAPI Interactive Docs (Swagger UI)**: `http://localhost:8000/docs`
   - 🩺 **Health Check**: `http://localhost:8000/health`

---

### Option 2: Local Development Setup

#### 1. Start the Backend Service
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (Optional)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the DuckDB database (if not already seeded)
python -m seed.seed_data

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

#### 2. Start the Frontend Service
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🔑 Demo User Accounts & Roles

The platform provides pre-configured JWT authentication for testing different RBAC tiers:

| Account Email | Password | Role | Permissions & Scope |
|---|---|---|---|
| `admin@acme.com` | `password123` | `ORG_ADMIN` | Full superuser access: queries, exports, audit logs, benchmark suite, and global multi-region scope. |
| `analyst@acme.com` | `password123` | `ANALYST` | Business analyst access: Text-to-SQL queries, dataset exploration, report creation. Subject to tenant and regional RLS scoping. |
| `viewer@acme.com` | `password123` | `VIEWER` | Read-only access: data viewing. Export and report creation are restricted. |

---

## 📡 REST API Reference

| Module | Method | Endpoint | Description | Required Permission |
|---|---|---|---|---|
| **Auth** | `POST` | `/api/v1/auth/login` | Authenticate user and issue JWT Bearer Token | Public |
| **Auth** | `GET` | `/api/v1/auth/me` | Fetch active user identity, role, tenant, and regions | Authenticated |
| **Queries** | `POST` | `/api/v1/queries` | Execute end-to-end AI analytics pipeline (Text-to-SQL + Grounding) | `QUERY_EXECUTE` |
| **Queries** | `GET` | `/api/v1/queries/history` | Retrieve historical query records and execution statuses | `QUERY_HISTORY` |
| **Datasets** | `GET` | `/api/v1/datasets` | Retrieve catalog metadata for all 6 governed enterprise datasets | `DATASOURCE_VIEW` |
| **Datasets** | `GET` | `/api/v1/datasets/{id}` | Fetch paginated table rows, columns, and profiling statistics | `DATASOURCE_VIEW` |
| **Datasets** | `GET` | `/api/v1/datasets/{id}/download` | Download dataset directly as a CSV file | `QUERY_EXPORT` |
| **Security** | `POST` | `/api/v1/security/inspect-sql` | Perform SQL AST validation, RLS/CLS simulation, and cost analysis | Public / Demo |
| **Security** | `GET` | `/api/v1/security/presets` | Retrieve 5 standard security attack and governance scenarios | Public |
| **Reports** | `POST` | `/api/v1/reports` | Generate executive PDF, Excel, or CSV report artifacts | `REPORT_CREATE` |
| **Reports** | `GET` | `/api/v1/reports/{id}/download` | Download generated report file | `REPORT_DOWNLOAD` |
| **Audit** | `GET` | `/api/v1/audit` | Fetch multi-tenant immutable audit logs | `AUDIT_VIEW` |
| **Evaluation**| `POST` | `/api/v1/evaluation/run` | Execute the 180+ enterprise benchmark evaluation suite | `EVALUATION_RUN` |

---

## 🧪 Testing & Verification

The repository includes a comprehensive automated test suite covering unit tests, E2E pipelines, SQL AST security policies, and tenant isolation:

```bash
# 1. Run all test suites
make test
# or
pytest tests/ -v --tb=short

# 2. Run dedicated Security & Prompt Injection tests
make security-test
# or
pytest tests/security/ -v --tb=short

# 3. Run End-to-End (E2E) pipeline tests
make e2e
# or
pytest tests/e2e/ -v --tb=short

# 4. Run the 180+ Benchmark Evaluation Framework
make evaluate
# or
python -m app.evaluation.eval_runner
```

---

## 🛡️ Security, Privacy & Governance Architecture

- **Deterministic AST SQL Policy**: Built with `sqlglot`. Non-SELECT queries (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `CREATE`) and unsafe functions (`pg_read_file`, `eval`, `exec`) are hard-blocked before execution.
- **Mandatory Multi-Tenant RLS**: Programmatically injects tenant boundaries (`WHERE tenant_id = :tenant_id`) into query syntax trees.
- **Dynamic CLS Redaction**: Sensitive attributes (`ssn`, `email`, `phone`, `credit_card`) are automatically rewritten with dynamic masking expressions.
- **Double-Sandboxed Python Engine**: Code execution is protected by static AST inspection and process-level isolation.
- **Compliance-Ready**: Designed in alignment with **SOC2 Type II** (Least Privilege), **ISO 27001** (Credential Isolation), **HIPAA / PCI-DSS** (PII Protection), and **GDPR / CCPA**.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).  
The 6 curated datasets comply with their respective open data terms and licensing agreements (Olist CC BY-NC-SA 4.0, NYC Open Data Terms, USDOT Public Domain, PhysioNet Open Access).

---

<p align="center">
  <b>Enterprise AI Data Analytics & Reporting Platform</b><br/>
  <i>Empowering Trusted Executive Intelligence with Deterministic Security Boundaries.</i>
</p>
