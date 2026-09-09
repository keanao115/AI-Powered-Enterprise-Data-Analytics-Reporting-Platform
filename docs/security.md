# Security & Governance Architecture

## 1. Core Security Principles

1. **The LLM is an Untrusted Planner**: The LLM NEVER determines access authorization, SQL validity, or execution permissions. All generated SQL queries are validated against AST security policies before execution.
2. **Deterministic AST Policy Enforcement**: Every candidate SQL query is parsed into a syntax tree using `sqlglot`. Non-analytical statements (DDL/DML, system tables, file I/O) are blocked fail-closed.
3. **Mandatory Row-Level Security (RLS)**: Queries are automatically rewritten to inject tenant and region isolation predicates (`WHERE tenant_id = :tenant_id`).
4. **Data Minimization & Dynamic PII Firewall**: Column-level security (CLS) masks sensitive attributes (SSN, credit cards, emails, phone numbers) before data is returned to users or exposed to external AI providers.
5. **Double-Sandboxed Python Execution**: Code execution for chart generation is protected by static AST inspection (blocking `import os`, `subprocess`, `open`, `eval`) and process isolation with hard limits on CPU, memory, execution duration, and zero network access.

---

## 2. Multi-Tenant Isolation & Compliance Alignment

### Isolation Model Trade-Offs
- **Current Reference Implementation**: Logical Row-Level Security (RLS) via AST injection. Ideal for resource-efficient SaaS deployments.
- **HIPAA & Regulated Data Considerations**: For highly sensitive datasets (such as MIMIC-IV clinical demo data), enterprise compliance frameworks (HIPAA Security Rule, PCI-DSS Requirement 3) frequently mandate physical schema or database isolation:
  - **Schema Isolation**: Isolates catalog metadata and permissions while sharing the compute engine.
  - **Database / Cluster Isolation**: Physically isolated storage and compute, eliminating noisy-neighbor effects and cross-tenant leakage vectors.

---

## 3. Secrets Management & Production Hardening

### Local Development vs. Production Lifecycle
- **Development & POC**: Environment variables are defined via `.env.example` with local variables. No hardcoded production credentials exist in the source code.
- **Enterprise Production Architecture**:
  - **Cloud Secret Stores**: AWS Secrets Manager, GCP Secret Manager, or HashiCorp Vault must be used to inject API keys, database credentials, and JWT signing keys at runtime.
  - **Key Rotation**: Cryptographic keys (JWT `SECRET_KEY`) and LLM API keys must follow an automated 90-day rotation policy with dual-key validation during transition windows.
  - **Least Privilege IAM**: The analytical engine execution role operates with read-only permissions on analytics tables and zero access to system metadata.

---

## 4. Software Supply Chain Security (SCA)

To ensure supply-chain integrity, the platform enforces:
1. **Automated Vulnerability Scanning (SCA)**:
   - CI pipeline incorporates `pip-audit` to detect known Common Vulnerabilities and Exposures (CVEs) across all Python dependencies.
   - Dependabot is configured (`.github/dependabot.yml`) for automated weekly dependency tracking and security patch pull requests.
2. **Container Security**:
   - Multi-stage minimal base Docker images (`python:3.11-slim`, `node:18-alpine`).
   - Running containerized backend processes as non-root users (`uid 10001`).

---

## 5. LLM Abuse Prevention & Cost Governance

1. **Tenant Token Quotas**: Hard daily and monthly token limits per tenant preventing runaway billing.
2. **Sliding-Window Rate Limiting**: Enforces request-per-minute (RPM) ceilings per user and per tenant.
3. **Replay & Anomaly Detection**: Hashes incoming query prompts to detect automated high-frequency polling, redirecting identical queries to semantic cache.
