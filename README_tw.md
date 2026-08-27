# 🌐 AI-Powered Enterprise Data Analytics & Reporting Platform
### 企業級 AI 智慧數據分析、決策報告與安全治理平台

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
[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20MIT-blue?style=flat-square)](#)

---

## 📖 專案概述 (Project Overview)

**AI-Powered Enterprise Data Analytics & Reporting Platform** 是一套專為現代企業設計的 **高可靠、確定性安全邊界（Deterministic Security Boundaries）與多租戶隔離** 之 AI 智慧數據分析與報告平台。

傳統 Text-to-SQL 或 AI 數據代理人往往面臨「LLM 幻覺」、「非受控的資料庫寫入/破壞風險」、「租戶數據越權洩漏」以及「未經事實驗證的虛假商業推論」。本平台的核心設計原則為：

> 🔒 **核心設計哲學：The LLM is an Untrusted Planner（LLM 僅作為不可信的查詢規劃器）**  
> 大型語言模型（LLM）僅負責將使用者的業務自然語言轉換為候選查詢。所有的 SQL 執行、租戶隔離、欄位遮蔽、Python 腳本分析與商業洞察，均受到 **嚴格的 AST 語意安全政策（SQL AST Policy）**、**強制行級安全（RLS）**、**動態列級敏感數據遮蔽（CLS）** 與 **雙層隔離沙箱（Execution Sandbox）** 的保護。

---

## 🏛️ 系統架構圖 (System Architecture)

```mermaid
graph TD
    User([👤 企業使用者 / 分析師]) -->|自然語言業務問題| UI[Next.js 14 現代化深色 UI]
    UI -->|REST API / Bearer JWT| Gateway[FastAPI API 網關]
    
    subgraph Security_Gate [🛡️ 第一層：安全防禦與意圖路由]
        Gateway --> Scanner[Prompt Injection 多階安全掃描]
        Scanner --> Clarifier[歧義檢測與主動澄清引擎]
        Clarifier --> DomainRouter[6 大真實領域意圖路由器]
    end

    subgraph Agent_Core [🧠 第二層：AI 分析師與 Text-to-SQL]
        DomainRouter --> Gemini[Google Gemini 3.6 Flash]
        Gemini --> CandidateSQL[產出 DuckDB 候選唯讀 SQL]
    end

    subgraph Deterministic_Guard [⚙️ 第三層：確定性安全與治理邊界]
        CandidateSQL --> ASTPolicy[sqlglot AST 語法樹政策審查<br/>(阻斷 DDL/DML/系統表/危險函數)]
        ASTPolicy --> RLSEngine[強制 RLS 行級多租戶重寫器<br/>(自動注入 WHERE tenant_id = :id)]
        RLSEngine --> CLSMasker[動態 CLS 列級遮蔽<br/>(SSN/Email/Phone 脫敏)]
        CLSMasker --> CostEstimator[EXPLAIN 成本評估與笛卡兒積防護]
    end

    subgraph Engine_Execution [⚡ 第四層：唯讀分析引擎與安全沙箱]
        CostEstimator --> ReadOnlyDuckDB[(DuckDB 唯讀分析引擎)]
        ReadOnlyDuckDB --> DQEngine[5-維度數據品質評估引擎]
        DQEngine --> PySandbox[雙重隔離 Python 數據視覺化沙箱]
        PySandbox --> Matplotlib[Matplotlib 圖表渲染 (Base64)]
    end

    subgraph Grounding_Reporting [📊 第五層：事實驗證與報告產出]
        Matplotlib --> Grounding[數值事實 Grounding 交叉驗證]
        Grounding --> Insights[Gemini 全繁體中文商業決策洞察]
        Insights --> ReportGen[報告生成器 (PDF / Excel / CSV)]
        ReportGen --> AuditLog[(不可篡改審計日誌與血緣追蹤)]
    end

    AuditLog --> UI
```

---

## 🚀 6 大真實世界企業級治理資料集 (Governed Datasets)

系統預載並完整整合了 **6 大跨行業標準真實公開數據集**，總計超過 24,000+ 筆結構化數據，儲存於高效能 DuckDB 唯讀分析引擎中：

| # | 業務領域 | 資料集名稱與來源 | 規模與表數 | 安全級別 | 涵蓋資料表與重點分析維度 |
|---|---|---|---|---|---|
| **01** | **零售與電商** | [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | 10,600+ 筆<br/>(6 張表) | `PUBLIC` | `olist_orders`, `olist_order_items`, `olist_products`, `olist_customers`, `olist_order_payments`, `olist_order_reviews`<br/>*GMV 營收趨勢、AOV、運費跨州分佈、交付延遲率、滿意度評分* |
| **02** | **城市交通** | [NYC TLC Taxi & Mobility](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) | 2,538+ 筆<br/>(2 張表) | `PUBLIC` | `nyc_taxi_trips`, `taxi_zones`<br/>*24小時車資與里程分佈、熱門上車區、機場 vs 市區行程、每英里收益效率、小費比例* |
| **03** | **航空營運** | [U.S. DOT BTS Airline On-Time](https://www.transtats.bts.gov/ONTIME/) | 2,535+ 筆<br/>(3 張表) | `PUBLIC` | `bts_flights`, `bts_airlines`, `bts_airports`<br/>*準點到達率 (On-Time Rate)、延誤成因 (天氣/航空/空管)、樞紐機場取消率、最差航線排行* |
| **04** | **醫療臨床** | [PhysioNet MIMIC-IV Clinical Demo](https://physionet.org/content/mimiciv/) | 3,700+ 筆<br/>(4 張表) | `RESTRICTED`<br/>*(附醫療免責)* | `mimic_patients`, `mimic_admissions`, `mimic_icu_stays`, `mimic_diagnoses`<br/>*ICU 住院天數 (LOS)、ICD-10 診斷代碼分佈、急診 vs 常規住院、保險類型與醫療資源利用* |
| **05** | **公共安全** | [City of Chicago Reported Crimes](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2) | 2,522+ 筆<br/>(2 張表) | `PUBLIC`<br/>*(附市政規範)* | `chicago_crimes`, `chicago_districts`<br/>*22 警察轄區報案量、犯罪類型 (THEFT/BATTERY)、執法逮捕率、時段熱力分佈、案發地點分類* |
| **06** | **金融市場** | [U.S. SEC EDGAR & Public Markets](https://www.sec.gov/edgar/searchedgar/companysearch) | 2,400+ 筆<br/>(3 張表) | `PUBLIC`<br/>*(附投資免責)* | `market_securities`, `market_daily_prices`, `market_financial_facts`<br/>*美股歷史價格、30日波動率、50日均線、SEC 10-Q/10-K 財務事實、自由現金流 (FCF)、板塊利潤率* |

---

## ✨ 核心功能模組 (Key Features)

### 1. 🤖 AI 智能數據分析師 (AI Analyst Interface)
- **自然語言查詢**：支援中文與英文輸入複雜業務問題。
- **智慧領域路由器 (Domain Intent Router)**：可選擇 `Auto Detect` 由 AI 自動識別問題領域，亦可指定特定資料集查詢。
- **主動澄清機制 (Clarification)**：當遇到語意模糊或缺乏必要維度（如未指定時間或計算指標）時，主動給予引導式選項。
- **結構化分析流水線**：透明展示安全掃描、意圖解析、SQL 生成、AST 審查、資料庫執行、沙箱繪圖與事實 Grounding 完整 10 步狀態。

### 2. 🛡️ SQL 安全檢驗器與策略模擬沙盒 (SQL Inspector)
- **AST 語法樹剖析**：基於 `sqlglot` 深入解析 Projections、Joins、Where 條件與語法結構。
- **角色與租戶模擬 (Persona Simulation)**：即時切換 `ORG_ADMIN`、`ANALYST`、`VIEWER` 或 `DPO`，驗證不同角色之 RLS 與 CLS 脫敏效果。
- **合規清單檢查**：自動評估 `SOC2 Type II`、`ISO 27001`、`HIPAA / PCI`、`GDPR / CCPA` 合規要求。
- **EXPLAIN 執行計劃與成本估算**：即時預估掃描行數、偵測未帶 WHERE 之全表掃描與笛卡兒積（Cartesian Product）風險。
- **內建 5 大安全預設場景**：標準分析、PII 提取脫敏、破壞性 DDL 阻斷、高成本查詢、系統表越權防護。

### 3. 📂 資料集探索器 (Dataset Explorer)
- **資料總覽與中英對照**：即時展示資料發布者、許可證協議 (License)、校驗碼 (Checksum) 與品質評分。
- **表結構與動態分頁瀏覽**：即時從 DuckDB 查詢真實記錄，支援全欄位即時關鍵字搜尋（Live Filter）。
- **欄位特徵分析 (Column Profiling)**：展示各欄位型態與前 3 筆樣本資料。
- **一鍵跳轉 AI 分析**：每個資料集內建 4 組典型業務範例問題，點擊直接代入分析師對話框。
- **即時 CSV 下載**：支援將各資料集快速匯出為 CSV 檔案。

### 4. 📈 雙重沙箱視覺化與 5-維度數據品質評估
- **安全 Python 執行沙箱**：利用 AST 靜態分析封鎖危險系統呼叫，在隔離作用域內利用 `matplotlib` 與 `pandas` 動態渲染圖表，輸出乾淨的高解析度 Base64 圖片。
- **數據品質評分 (Data Quality Engine)**：自動檢測查詢結果之空值率 (Null Ratio)、重複資料數 (Duplicates)、時效性與完整性評分。

### 5. 🎯 數據事實 Grounding 與商業決策報告
- **100% 數值事實錨定 (Grounded Claims)**：自動將 LLM 產生的每一句推論與資料庫實際返回的數值進行交叉驗證，標註 `SUPPORTED` 或 `UNSUPPORTED`，根絕 AI 幻覺。
- **專業全繁體中文輸出**：依據高階商業顧問標準輸出「執行摘要」、「核心數據發現」與「策略行動建議」。
- **多格式報告導出**：支援產出專業排版的 **PDF 報告 (ReportLab)**、**Excel 試算表 (OpenPyXL)** 與 **CSV 格式**。

### 6. 🔍 數據血緣與不可篡改審計 (Data Provenance & Audit Logs)
- **完整血緣追蹤圖 (Lineage Graph)**：追溯從來源表、語義層指標定義、AST 重寫條件、執行時間到生成報告的端到端過程。
- **合規審計日誌 (Audit Log Viewer)**：詳實記錄每一次查詢的時間戳、使用者、租戶、SQL 語句、攔截事件與風險等級。

### 7. 🧪 180+ 基準測試與評估儀表板 (Evaluation Benchmark Suite)
- 系統內建整合式生產級評估套件：
  - **90 項多領域業務分析題**（涵蓋 L1 ~ L10 不同難度等級）
  - **30 項安全攻擊防禦測試**（Prompt Injection、SQL Injection、破壞性 DDL、越權存取、DoS）
  - **30 項數值事實 Grounding 驗證**
  - **30 項歧義主動澄清情境**
- 支援在前端 UI 一鍵點擊運行，即時產出綜合準確率與分項 KPI。

---

## 🛠️ 技術棧 (Tech Stack)

### 後端架構 (Backend)
- **核心框架**：Python 3.10+ / FastAPI 0.110.0
- **數據分析引擎**：DuckDB 0.10.0 (唯讀內嵌分析引擎)
- **應用數據庫**：PostgreSQL 16 / SQLite (via SQLAlchemy 2.0 & aiosqlite)
- **SQL AST 解析與轉換**：`sqlglot` 23.0+
- **AI / LLM 網關**：Google Gemini (`gemini-3.6-flash`) / OpenAI / Mock Provider
- **數據處理與視覺化**：Pandas, NumPy, Matplotlib, Seaborn
- **報告產出引擎**：ReportLab (PDF), OpenPyXL (Excel), CSV
- **認證與安全**：JWT (python-jose), Argon2 / BCrypt (passlib)
- **可觀測性**：OpenTelemetry SDK, Prometheus Metrics

### 前端架構 (Frontend)
- **核心框架**：Next.js 14 (App Router) / React 18
- **程式語言**：TypeScript 5.0
- **UI 樣式與元件**：Tailwind CSS 3.4, Lucide React
- **國際化 (i18n)**：內建雙語上下文切換（繁體中文 `zh-TW` / 英文 `en`）

---

## 📁 專案目錄結構 (Directory Structure)

```plaintext
.
├── backend/
│   ├── app/
│   │   ├── ai/                      # AI 核心：Agent 狀態機、Prompts、Providers、Tools
│   │   │   ├── agent/               # 分析師 Agent、歧義檢測、狀態管理
│   │   │   ├── providers/           # Gemini / OpenAI / Mock LLM 提供者
│   │   │   └── tools/               # 語義、架構、SQL、視覺化工具註冊表
│   │   ├── analytics/               # 數據品質評估、事實 Grounding、數據血緣
│   │   ├── api/v1/                  # REST API 路由 (queries, datasets, security, reports 等)
│   │   ├── core/                    # 設定 (config)、資料庫連線、RBAC 權限、租戶隔離
│   │   ├── evaluation/              # 180+ 基準測試執行引擎
│   │   ├── ingestion/               # 6 大資料集載入與 DuckDB 轉換管道
│   │   ├── query_engine/            # AST 政策引擎、RLS 重寫、CLS 遮蔽、成本估算、自動修復
│   │   ├── reporting/               # PDF / Excel / CSV 報告生成器
│   │   ├── sandbox/                 # Python 執行沙箱與 AST 安全驗證器
│   │   ├── security/                # Prompt 注入掃描器、動態遮蔽、審計日誌
│   │   ├── semantic/                # 數據集目錄 (Catalog)、語義層與指標定義
│   │   └── main.py                  # FastAPI 主入口與生命週期初始化
│   ├── seed/
│   │   └── seed_data.py             # 6 大真實資料集自動合成與 DuckDB 建表腳本
│   └── requirements.txt             # 後端相依套件清單
│
├── frontend/
│   ├── src/
│   │   ├── app/                     # Next.js 頁面與佈局 (page.tsx, layout.tsx)
│   │   ├── components/              # 核心 UI 元件
│   │   │   ├── AIAnalystInterface.tsx     # AI 分析師主介面與對話卡片
│   │   │   ├── DatasetExplorer.tsx        # 6 大資料集探索器與即時預覽
│   │   │   ├── SQLInspector.tsx           # SQL AST 安全檢驗與策略沙盒
│   │   │   ├── DataProvenanceView.tsx     # 數據血緣端到端可視化
│   │   │   ├── DataDictionary.tsx         # 企業數據字典與安全分類
│   │   │   ├── AuditLogViewer.tsx         # 安全與合規審計日誌
│   │   │   ├── EvaluationDashboard.tsx    # 180+ 基準評估儀表板
│   │   │   └── LanguageSelector.tsx       # 繁中 / 英文切換器
│   │   ├── lib/api.ts               # 前端 API 客戶端呼叫庫
│   │   ├── locales/                 # 雙語語系檔案 (zh-TW.ts, en.ts, LanguageContext.tsx)
│   │   └── types/index.ts           # 前端 TypeScript 型別定義
│   ├── package.json
│   └── tailwind.config.js
│
├── docs/                            # 架構、安全模型與威脅分析文件
├── tests/                           # 自動化測試套件 (e2e, security, tenancy)
├── analytics_demo.duckdb            # 本地 DuckDB 分析資料庫
├── docker-compose.yml               # Docker Compose 多容器編排設定
├── Dockerfile.backend               # 後端映像檔構建設定
├── Dockerfile.frontend              # 前端映像檔構建設定
├── Makefile                         # 快捷開發與自動化維運指令
└── README.md                        # 本專案說明文件
```

---

## ⚡ 快速開始指南 (Quick Start Guide)

### 📋 環境要求 (Prerequisites)
- **Python**: 3.10 或更高版本
- **Node.js**: 18.0 或更高版本 (搭配 npm 或 pnpm)
- **Docker & Docker Compose** (可選，容器化啟動使用)

---

### 方法一：使用 Docker Compose（推薦，一鍵啟動）

1. **複製環境設定檔**：
   ```bash
   cp .env.example .env
   ```

2. **構建並啟動所有容器服務**：
   ```bash
   docker compose up -d --build
   ```

3. **存取各服務門戶**：
   - 💻 **前端管理儀表板**：`http://localhost:3300` (或 `http://localhost:3000`)
   - 🔌 **後端 FastAPI 文件 (Swagger UI)**：`http://localhost:8000/docs`
   - 🩺 **健康檢查端點**：`http://localhost:8000/health`

---

### 方法二：本機開發模式 (Local Development)

#### 1. 後端服務啟動
```bash
# 1. 進入後端目錄
cd backend

# 2. 建立並啟用虛擬環境 (可選)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# 3. 安裝後端相依套件
pip install -r requirements.txt

# 4. 初始化 DuckDB 數據庫與種子資料 (若尚未存在)
python -m seed.seed_data

# 5. 啟動 FastAPI 開發伺服器
uvicorn app.main:app --reload --port 8000
```

#### 2. 前端服務啟動
```bash
# 1. 打開另一個終端，進入前端目錄
cd frontend

# 2. 安裝 Node.js 相依模組
npm install

# 3. 啟動 Next.js 開發伺服器
npm run dev
```
瀏覽器打開 `http://localhost:3000` 即可體驗完整系統。

---

## 🔑 預設登入帳號與角色 (Demo Accounts)

系統內建展示用 JWT 認證身分，可直接用於 API 測試：

| 帳號 Email | 預設密碼 | 系統角色 (Role) | 權限範圍說明 |
|---|---|---|---|
| `admin@acme.com` | `password123` | `ORG_ADMIN` | 最高管理員，具備所有查詢、導出、審計日誌與基準評估權限，不受 RLS 地區限制 |
| `analyst@acme.com` | `password123` | `ANALYST` | 企業數據分析師，可執行 Text-to-SQL、查詢資料集與生成報告，受 RLS 地區/租戶隔離限制 |
| `viewer@acme.com` | `password123` | `VIEWER` | 檢視者身分，具備唯讀權限，禁止執行高風險資料導出 |

---

## 📡 核心 API 端點一覽 (API Reference)

| 模組 | HTTP 方法 | 路徑 | 功能說明 | 權限等級 |
|---|---|---|---|---|
| **認證** | `POST` | `/api/v1/auth/login` | 使用者登入並取得 JWT Bearer Token | Public |
| **認證** | `GET` | `/api/v1/auth/me` | 取得當前使用者角色、租戶與授權地區資訊 | Authenticated |
| **查詢** | `POST` | `/api/v1/queries` | 執行 AI 數據分析完整管道 (Text-to-SQL + Grounding) | `QUERY_EXECUTE` |
| **查詢** | `GET` | `/api/v1/queries/history`| 獲取歷史查詢紀錄與執行狀態 | `QUERY_HISTORY` |
| **資料集** | `GET` | `/api/v1/datasets` | 獲取 6 大真實資料集目錄與元數據 | `DATASOURCE_VIEW` |
| **資料集** | `GET` | `/api/v1/datasets/{id}` | 分頁獲取特定資料集之結構、數據與欄位特徵統計 | `DATASOURCE_VIEW` |
| **資料集** | `GET` | `/api/v1/datasets/{id}/download` | 即時下載該資料集為 CSV 格式 | `QUERY_EXPORT` |
| **安全沙盒** | `POST`| `/api/v1/security/inspect-sql` | 執行 SQL AST 分析、RLS/CLS 重寫與成本預估 | Public / Demo |
| **安全沙盒** | `GET` | `/api/v1/security/presets` | 獲取 5 大預設安全測試場景 | Public |
| **報告** | `POST` | `/api/v1/reports` | 根據查詢結果生成 PDF / Excel / CSV 報告 | `REPORT_CREATE` |
| **報告** | `GET` | `/api/v1/reports/{id}/download` | 下載已產出之報告檔案 | `REPORT_DOWNLOAD` |
| **審計** | `GET` | `/api/v1/audit` | 查詢多租戶合規審計日誌與攔截紀錄 | `AUDIT_VIEW` |
| **評估** | `POST` | `/api/v1/evaluation/run` | 執行 180+ 項生產級基準評估測試 | `EVALUATION_RUN` |

---

## 🧪 測試與驗證指南 (Testing & Benchmarks)

本專案具備完整的自動化測試套件，涵蓋單元測試、E2E 管道、SQL AST 安全性與多租戶隔離：

```bash
# 1. 運行全部測試套件
make test
# 或
pytest tests/ -v --tb=short

# 2. 運行專屬安全與 Prompt 注入防禦測試
make security-test
# 或
pytest tests/security/ -v --tb=short

# 3. 運行端到端 (E2E) 數據管道測試
make e2e
# 或
pytest tests/e2e/ -v --tb=short

# 4. 運行 180+ 基準測試評估框架 (Text-to-SQL + Grounding)
make evaluate
# 或
python -m app.evaluation.eval_runner
```

---

## 🛡️ 安全、隱私與合規設計 (Security & Compliance)

- **SQL 注入防禦**：完全由 `sqlglot` 建立語法樹，所有輸入均不採字串拼接，非 SELECT 指令（`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `CREATE`）在 AST 階段即刻拒絕。
- **多租戶硬隔離**：RLS 重寫器在 AST 層強制植入 `tenant_id = :tenant_id` 條件，確保各企業資料完全隔離。
- **動態 PII 脫敏 (CLS)**：針對 `ssn`, `email`, `phone`, `credit_card` 等機敏欄位，自動於 SQL 查詢層進行雜湊與遮蔽替換。
- **雙重沙箱防護**：靜態 AST 審查禁用 `os`, `sys`, `subprocess`, `socket`, `eval`, `exec` 等高危模組，並限定執行時間與記憶體。
- **合規就緒 (Compliance Ready)**：設計嚴格符合 SOC2 Type II（最小權限原則）、ISO 27001（機密隔離）、HIPAA / PCI-DSS（敏感數據脫敏）與 GDPR / CCPA 規範。

---

## 📄 授權條款 (License)

本專案之程式原始碼採用 [MIT License](LICENSE) 授權。  
所整合之 6 大公開數據集遵循各原始發布單位之開放資料條款（如 Olist CC BY-NC-SA 4.0、NYC Open Data Terms of Use、USDOT Public Domain、PhysioNet Open Access 等）。

---

<p align="center">
  <b>Enterprise AI Data Analytics & Reporting Platform</b><br/>
  <i>Empowering Trusted Executive Intelligence with Deterministic Security Boundaries.</i>
</p>
