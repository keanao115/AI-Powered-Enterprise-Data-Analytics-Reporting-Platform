# AI-Powered Enterprise Data Analytics & Reporting Platform
## 改進追蹤文檔 v2 (Improvement Tracking Document)

> 本文件為第一版「已知限制與改進路線圖」的更新版。第一部分標注上一版提出、現已在 README / 架構中處理的項目；第二部分詳列目前仍待改進的內容，依優先度排序。

---

## 一、已解決項目 (Resolved)

以下項目在上一輪分析中提出，現已反映在 README、測試套件與架構實作中：

| # | 原問題 | 落地現況 | 核心檔案 / 機制 |
|---|---|---|---|
| 1 | "Enterprise-grade" 用詞與實際資料規模不符 | 重新定位為「Architectural Reference Implementation」，並附 Sizing Note 明確說明 governance layer 與儲存層解耦，可遷移到 Snowflake/BigQuery/ClickHouse | `README.md`<br/>`README_tw.md`<br/>`docs/architecture.md` |
| 2 | "100% Fact-Checked Claims" 缺乏量測方法論 | 改為正則數值抽取 + 浮點容差比對 (±0.5%)，分類 `SUPPORTED` / `UNSUPPORTED` / `APPROXIMATED`，並附審計軌跡 | `backend/app/analytics/grounding.py`<br/>`tests/security/test_resilience_and_grounding.py` |
| 3 | Multi-tenant isolation 強度未明確說明 | Known Limitations 表格已明確標注目前為共享程序邏輯 RLS，並列出 schema-per-tenant / database-per-tenant 的演進路徑與 HIPAA 考量 | `docs/security.md`<br/>`docs/architecture.md` |
| 4 | LLM API 呼叫缺乏成本/濫用治理 | 已加入 Token Budget 控制器、每分鐘請求速率限制 (RPM)、滑動窗口防重放機制 | `backend/app/security/token_governance.py`<br/>`tests/security/test_token_governance.py` |
| 5 | LLM API 故障容錯機制未說明 | 已加入熔斷器模式 (Circuit Breaker) + 指數退避重試，失敗時平滑降級，測試套件耗時由 117s 驟降至 14s | `backend/app/ai/resilience.py`<br/>`backend/app/ai/providers/gemini_provider.py` |
| 6 | 依賴/映像檔弱點掃描缺失 (SCA) | CI/CD 已整合 `pip-audit` 弱點掃描與 Dependabot 自動化補丁機制，清理預設明文 API Key | `.github/workflows/ci.yml`<br/>`.github/dependabot.yml`<br/>`backend/app/core/config.py` |
| 7 | 語意層指標定義版本控管未描述 | Metric Registry 已納入版本號、責任人、審計歷程 metadata 與變更管理方法 | `backend/app/semantic/semantic_layer.py` |

這些項目的共同特徵是：不一定需要完美解決，而是**誠實揭露設計取捨並說明演進路徑**——這正是上一版建議的核心精神，也是目前 README「Known Limitations & Architectural Roadmap」章節在做的事。

---

## 二、待改進項目與落地策略 (Remaining & Action Plan)

### 高優先 (High Priority)

#### 2.1 靜態加密 (Encryption at Rest)
- **問題**：DuckDB 分析資料庫檔案、PostgreSQL 應用資料庫、備份檔案，是否啟用加密皆未在文件中提及。
- **重要性**：即使查詢層有 RLS/CLS 防護，若底層儲存檔案未加密，實體外洩（備份誤傳、磁碟鏡像存取）仍會造成資料外流。
- **落地改進**：
  1. 在 `README.md`、`README_tw.md` 與 `docs/known-limitations-and-roadmap.md` 的 Known Limitations 表格新增「靜態資料加密 (Encryption at Rest)」條目，誠實標注 POC 選型與生產環境方案。
  2. 在 `docs/security.md` 專闢「儲存與備份靜態加密架構」專節，詳述 Linux LUKS / AWS EBS KMS 卷加密、S3/GCS SSE-KMS 伺服器端託管金鑰 (CMK) 與備份 AES-256 自動加密方案。

#### 2.2 企業 SSO / OIDC 整合
- **問題**：目前認證僅有本地 JWT + 帳號密碼，沒有整合 SAML / OIDC 等企業級 IAM 協定。
- **重要性**：企業內部系統通常要求統一 SSO 治理，獨立帳密系統在正式導入企業環境時是常見阻力點。
- **落地改進**：
  1. 在 Known Limitations 表格揭露目前為本機 JWT + RBAC 角色模擬，並標記 OIDC / SAML 2.0 演進路徑。
  2. 在後端 `app/api/v1/auth.py` 與 `app/core/config.py` 實作標準企業 SSO / OIDC 整合介面與 Mock IdP 轉換邏輯，示範如何將 Keycloak / Okta / Azure AD 的 ID Token claims 對應至 `TenantContext`。

---

### 中優先 (Medium Priority)

#### 2.3 併發/效能測試數據未公開
- **問題**：`concurrency_benchmark.py` 已存在於程式碼中，但 README 沒有放上實際的 P50/P95/P99 延遲數據。
- **重要性**：工具存在但沒展示結果，無法證明系統實際效能表現，說服力打折——這是「做了」跟「證明做了」之間的落差。
- **落地改進**：
  - 將實測數據（1 ~ 50 執行緒之 QPS 33.3 ~ 1,750.7、P50 延遲 8.81ms ~ 20.72ms、P99 < 55ms、0 錯誤）製作為完整表格，置入 `README.md` 與 `README_tw.md`。

#### 2.4 CI/CD 實際運作狀態無法從外部驗證
- **問題**：README 聲稱 CI 已整合 pip-audit 與 Dependabot，但沒有可見的 CI status badge，外部審查者難以直接確認是否真的在運作。
- **重要性**：「文件裡寫有做」跟「看得到證據」是兩回事，面試官或審查者通常會直接點開 Actions 查看實際執行紀錄。
- **落地改進**：
  - 在 `README.md` 與 `README_tw.md` 頂部加入 GitHub Actions workflow 的 CI/CD build badge 與 SCA 掃描 Badge。

---

### 加分項 (Bonus & High ROI)

#### 2.5 缺乏可直接訪問的 Live Demo
- **問題**：目前只能透過 clone + 本機啟動來體驗系統，沒有部署好的公開 demo 連結。
- **重要性**：對求職/作品集展示而言，面試官點開連結就能互動，遠比要求對方 clone、裝環境、跑 docker compose 的體驗與說服力高出許多。
- **落地改進**：
  - 在 README 顯著位置提供「🌐 Live Demo & Cloud Deployment Guide」，包含 Render / Railway / Fly.io 免費層一鍵部署配置、展示用帳號密碼與架構說明。
