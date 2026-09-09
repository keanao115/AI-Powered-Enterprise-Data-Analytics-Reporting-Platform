# AI-Powered Enterprise Data Analytics & Reporting Platform
## 已知限制與改進路線圖 (Known Limitations & Improvement Roadmap)

> 本文件整理此專案在架構、安全、工程成熟度三個面向上的改進建議與權衡考量，依優先度排序。目的是讓專案的說法 (claims) 與實際工程能力對齊，並明確記錄邁向大規模生產環境時所需的架構演進路徑。

---

## 一、用詞與斷言問題 (Claims & Positioning)

### 1.1 "Enterprise-grade" 用詞與實際規模不符
- **現況問題**：預載的 6 個真實公開資料集規模在 2,400 ~ 10,600 筆之間（總量約 24,000+ 筆），屬於展示與架構概念驗證 (POC) 等級，而非真實大型企業通常面對的千萬至億級資料量。
- **重要性**：在嚴謹的架構審查中，資料量與技術選型密切相關。用詞過度宣稱會稀釋底層安全性設計（如 AST 重寫與 RLS）的說服力。
- **改進落實**：
  1. 將定位精準明確化為「**企業級治理層架構參考實作 (Architectural Reference Implementation / Security-First Framework)**」。
  2. 明確說明：「安全治理層（RLS / CLS / AST Policy / Double-Sandboxed Runner）為通用確定性設計，可直接沿用到真實企業規模資料倉儲；目前內建資料庫係為本機開箱即用與 CI/CD 測試所選用的輕量級展示引擎」。
  3. 提供併發與延遲壓測工具 (`benchmarks/concurrency_benchmark.py`)，量化 DuckDB 在併發分析查詢下的真實 P50/P95/P99 延遲與瓶頸點。

### 1.2 "100% Fact-Checked Claims" 缺乏量測方法論佐證
- **現況問題**：「100%」屬於行銷式絕對斷言，未完整揭示驗證演算法、數值比對公差、樣本規模及已知邊界情況。
- **重要性**：生產級工程文件需嚴謹交代評測方法論，避免「過度承諾」引發對幻覺抑制機制的質疑。
- **改進落實**：
  1. 升級 `backend/app/analytics/grounding.py`：引入數值提取正則 (Numeric Extraction) 與公差校驗演算法（允許 ±0.5% 或捨入誤差），產出結構化證據與標籤 (`SUPPORTED` / `UNSUPPORTED` / `APPROXIMATED`)。
  2. 補足方法論文件與評測基準：在 180 組評測情境中，針對數值斷言進行精確統計（數值主張檢驗通過率達 95%+），並如實標註已知邊界（例如多表複雜加權聚合或 LLM 生成的複合百分比計算）。

---

## 二、安全與治理 (Security & Governance)

### 2.1 Multi-tenant isolation 強度與架構取捨
- **現況問題**：目前依賴 SQL AST 動態改寫注入 `WHERE tenant_id = :id` 進行行級安全 (RLS)，屬於共用資料庫 (Shared-Process Logical Isolation)。
- **架構取捨考量**：
  | 隔離等級 | 實作方式 | 優勢 | 限制 / 成本 | 適用場景 |
  |---|---|---|---|---|
  | **邏輯 RLS (當前架構)** | AST 語法樹注入 `WHERE tenant_id = :id` | 基礎架構成本極低、資源利用率高、部署極簡 | 共享底層儲存與記憶體，依賴查詢改寫器無漏洞 | 展示、內部系統、一般 SaaS |
  | **Schema-per-tenant** | 獨立 Schema + 專屬連線權限 | 儲存層具體隔離、支援獨立備份 | 連線池管理較複雜、Schema Migration 成本高 | B2B 中型企業、金融分析 |
  | **Database-per-tenant** | 獨立實體資料庫實例 | 實體最高等級隔離、無跨租戶外洩途徑、符合 HIPAA/PCI 硬性要求 | 維運成本高昂、跨租戶資源彙總困難 | 醫療高敏感 (如 MIMIC 原始病歷)、高資安合規 |
- **演進路徑**：高敏感度資料集（如 MIMIC-IV）建議支援獨立實體資料庫或專用唯讀複本，隔離政策引擎則抽象出 Driver 介面以支援不同層級。

### 2.2 LLM API 呼叫成本與防濫用治理
- **現況問題**：雖然底層 SQL 具備 EXPLAIN Cost Estimator，但上游 LLM 呼叫缺乏租戶層級的 Token 預算限制與防爆破機制。
- **改進落實**：
  1. 實作 `backend/app/security/token_governance.py`：
     - **Per-Tenant / Per-User Token Budget**：追蹤租戶每日累計花費與 Token 用量，超標即拋出 `BudgetExceededException`。
     - **Sliding Window Rate Limiter**：限制每租戶/用戶每分鐘最大查詢次數 (RPM)。
     - **重複查詢濫用偵測 (Replay Detector)**：偵測短時間內高頻重複請求，提供快取或直接阻斷。

### 2.3 軟體供應鏈安全與依賴掃描 (SCA)
- **現況問題**：缺乏自動化相依性弱點掃描與映像檔安全檢查。
- **改進落實**：
  1. 在 `.github/workflows/ci.yml` 中整合 `pip-audit`，於 PR 時自動掃描已知 Python CVE 漏洞。
  2. 新增 `.github/dependabot.yml`，啟用每週自動依賴版本更新與漏洞 PR。
  3. 加入程式碼品質與風格檢查（`ruff check`）。

### 2.4 Secrets 管理最佳化
- **現況問題**：依賴本機 `.env` 檔案管理，程式碼預設配置存在示範金鑰。
- **改進落實**：
  1. 清理 `backend/app/core/config.py` 中的預設金鑰字串，全面改由環境變數動態讀取。
  2. 在安全架構文件中明定生產環境接入雲端原生密鑰管理（AWS Secrets Manager、GCP Secret Manager 或 HashiCorp Vault），並加入定期輪替 (Key Rotation) 機制指引。

### 2.5 靜態資料加密 (Encryption at Rest)
- **現況問題**：DuckDB 檔案、PostgreSQL 應用資料庫與導出備份未在單機層級預設加密。
- **改進落實**：
  1. 在架構文檔中詳列分層靜態加密策略：底層儲存卷掛載 Linux LUKS 或雲端 AWS EBS / GCP Persistent Disk（預設啟用 KMS 加密）。
  2. 雲端 Parquet / Object 儲存全面啟用 SSE-KMS 託管密鑰，離線備份檔案實施 GPG / AES-256 流式加密。

### 2.6 企業級 SSO / OIDC 身分聯邦 (Enterprise IAM)
- **現況問題**：目前認證為本地 JWT + 帳號密碼，尚未串接 SAML / OIDC 企業身分服務。
- **改進落實**：
  1. 在後端新增 `/auth/sso/providers` 與 `/auth/sso/oidc/callback` 抽象整合介面。
  2. 規劃企業級 IdP（Keycloak / Okta / Azure AD / Auth0）之 JWT Claims 到 `TenantContext` 的對應架構，支援 SCIM 2.0 自動化目錄同步。

---

## 三、可靠性與容錯 (Reliability & Resilience)

### 3.1 LLM API 故障容錯與熔斷機制
- **現況問題**：外部 LLM Provider 發生逾時、限流 (429) 或憑證異常時，過長等待時間會造成系統懸掛。
- **改進落實**：
  1. 實作 `backend/app/ai/resilience.py`：
     - **Circuit Breaker (熔斷器)**：外部 API 連續失敗達閾值時進入 OPEN 狀態，冷卻期內直接快速失敗。
     - **Exponential Backoff with Jitter**：暫時性網路錯誤自動指數退避重試。
     - **優雅降級**：當雲端 LLM 不可用時，即時切換至本機確定性分析引擎或備援 Provider，確保核心數據查詢不中斷。

### 3.2 負載與併發測試實測數據
- **現況問題**：原 180+ Benchmark 主要針對功能、安全性與 Grounding 正確性，缺乏併發讀取延遲數據。
- **改進落實**：
  - 建立獨立壓測模組 `benchmarks/concurrency_benchmark.py`，實測 DuckDB 在多執行緒併發讀取下的效能數據：

| 併發執行緒 (Threads) | 總查詢數 (Queries) | 執行耗時 (Duration) | 吞吐量 (QPS) | P50 延遲 (ms) | P95 延遲 (ms) | P99 延遲 (ms) | 錯誤數 (Errors) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1**  | 12  | 0.360s | **33.3**   | 27.90ms | 40.16ms | 40.16ms | 0 |
| **5**  | 60  | 0.162s | **370.2**  | 8.81ms  | 27.84ms | 39.80ms | 0 |
| **10** | 120 | 0.203s | **589.7**  | 10.12ms | 25.32ms | 38.89ms | 0 |
| **25** | 300 | 0.190s | **1,577.1** | 9.40ms  | 26.85ms | 37.04ms | 0 |
| **50** | 600 | 0.343s | **1,750.7** | 20.72ms | 42.99ms | 53.36ms | 0 |

  - **結論**：單機 DuckDB 在 50 併發下可維持高達 1,750 QPS 吞吐，P50 < 21ms，P99 < 55ms，完美證明單節點展示效能。大於 100 併發與 PB 級資料建議無縫過渡至 Snowflake / BigQuery。

---

## 四、工程流程成熟度 (DevOps / Engineering Maturity)

### 4.1 CI/CD Pipeline 強化
- **改進落實**：
  1. 更新 `.github/workflows/ci.yml`：
     - 代碼風格分析 (`ruff`)
     - 供應鏈安全掃描 (`pip-audit`)
     - 全自動單元、整合、安全性測試與 180 題 Benchmark 運行
     - Docker 鏡像建置驗證

---

## 五、資料與擴展性 (Data & Scale)

### 5.1 DuckDB 單機引擎擴展性邊界與雲端倉儲遷移
- **現況說明**：DuckDB 是高效能內嵌式單機 OLAP 引擎，非常適合單節點、中小型分析與展示部署，但在跨節點分散式儲存與數萬並行連線下有其物理限制。
- **架構解耦設計**：
  - 本專案核心為「**安全與治理中介層 (Security & Governance Middleware)**」：
    - `AST Security Policy Engine`
    - `Mandatory RLS Query Rewriter`
    - `Dynamic CLS Data Masker`
    - `Fact Grounding Engine`
  - 這一層完全獨立於底層 SQL 引擎。若遷移至雲端企業級資料倉儲（如 Snowflake、Google BigQuery 或 ClickHouse），只需抽換 SQL Dialect（`sqlglot` 原生支援）與資料庫驅動程式，所有安全邊界與治理機制均可直接繼承。

---

## 六、語意層治理 (Semantic Layer Governance)

### 6.1 指標定義版本控管與變更追溯
- **現況問題**：指標清單定義於程式碼中，缺乏版本歷程與變更審查元數據。
- **改進落實**：
  1. 為 `MetricDefinition` 新增元數據欄位：`version`、`owner`、`change_history`。
  2. 記錄指標修訂時間戳、修改者與修改理由，防範指標定義漂移 (Metric Drift) 與業務歧義。

---

## 七、總結：面試與架構展示指引

1. **主動揭示限制**：在展示中主動指出「DuckDB 是展示選型，但治理中介層具備 Snowflake/BigQuery 可移植性」，能立刻展現出成熟工程師對架構邊界與取捨的深度認知。
2. **安全縱深防禦**：著重展示 LLM 作為「不可信規劃器」的核心設計理念，即便 LLM 被惡意 Prompt 繞過，AST 政策層、RLS 重寫器與 Double Sandbox 仍能保證資料庫不受威脅。
3. **有數據有真相**：使用 Grounding 方法論與 Concurrency Benchmark 的量化數據，取代籠統的「100%」與「Enterprise-grade」口號。
