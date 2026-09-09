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

---

## 6. 靜態資料加密架構 (Encryption at Rest Architecture)

為全面防範實體磁碟外洩、未授權快照與備份遺失風險，本平台針對不同儲存組件規劃分層靜態加密策略：

| 儲存組件 | 本機 POC / Demo 現狀 | 生產環境加密演進路徑 (Production At-Rest Encryption) |
|---|---|---|
| **DuckDB 分析庫** (`analytics_demo.duckdb`) | 檔案明文儲存於本機目錄 | 1. 儲存卷層級加密：掛載於 Linux LUKS / dm-crypt 加密磁碟卷，或雲端 AWS EBS / GCP Persistent Disk（預設啟用 KMS 加密）。<br/>2. 外部 Parquet 倉儲：使用 AWS S3 / GCS Server-Side Encryption (SSE-KMS) 搭配客戶端託管金鑰 (CMK)。 |
| **應用關聯庫** (PostgreSQL / SQLite) | 本機 SQLite 明文儲存 | 1. PostgreSQL 啟用 Transparent Data Encryption (TDE) 或使用 `pgcrypto` 針對特定欄位（如用戶敏感憑證）進行加密儲存。<br/>2. 雲端託管 RDS / Cloud SQL：強制啟用硬碟級 KMS 加密與 Automated Backup Snapshot 加密。 |
| **審計日誌與血緣** (`Audit Logs`) | SQLite / 檔案日誌串流 | 1. 審計資料寫入 Write-Once-Read-Many (WORM) 儲存桶（如 AWS S3 Object Lock in Compliance Mode）。<br/>2. 串流加密至 SIEM 平台（Splunk, Datadog），傳輸與靜態均採用 TLS 1.3 + AES-256。 |
| **報表匯出與備份檔案** (PDF / Excel / CSV) | 臨時存放於本機物件目錄 | 1. 產出檔案存入隔離暫存區，下載完成後自動排程 TTL 刪除。<br/>2. 離線備份檔案透過 GPG / OpenSSL 進行 AES-256-GCM 流式加密後再上傳異地災難備援。 |

---

## 7. 企業級單一登入與身分聯邦 (Enterprise SSO & OIDC / SAML 2.0)

### 認證架構演進
- **現行 POC 模式**：本地 JWT Bearer Token 認證，支援 `ORG_ADMIN`、`ANALYST`、`VIEWER`、`DPO` 快速角色切換以利安全策略驗證與模擬。
- **企業生產模式 (OIDC / SAML 2.0 Federation)**：
  - 整合企業級 IdP（Identity Provider），如 **Keycloak**、**Okta**、**Microsoft Entra ID (Azure AD)** 或 **Auth0**。
  - 後端提供標準 OAuth2 Authorization Code Flow 與 OpenID Connect (OIDC) 端點 (`/api/v1/auth/sso/oidc/callback`)。
  - **Claims 對應至 Multi-Tenant 治理上下文**：
    ```
    IdP JWT Claims:
      - iss (Issuer URL)        --> 驗證企業 IdP 信任鏈
      - sub (Unique User ID)    --> mapped to TenantContext.user_id
      - tid (Tenant Claim)      --> mapped to TenantContext.tenant_id
      - groups / roles          --> mapped to TenantContext.user_role
      - custom:regions          --> mapped to TenantContext.authorized_regions
      - custom:departments      --> mapped to TenantContext.authorized_departments
    ```
  - 支援 SCIM 2.0 協定自動化同步用戶進出（Joiner-Mover-Leaver）與群組權限撤銷，確保零殘留越權風險。
