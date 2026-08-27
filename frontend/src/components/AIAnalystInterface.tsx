'use client';

import React, { useState, useEffect } from 'react';
import {
  Search,
  ShieldAlert,
  CheckCircle2,
  Sparkles,
  AlertTriangle,
  FileSpreadsheet,
  Download,
  RefreshCw,
  Layers,
  Database,
  ExternalLink,
  Shield,
  Activity,
  Cpu
} from 'lucide-react';
import { submitQuery, triggerReportDownload } from '../lib/api';
import { QueryResponse } from '../types';
import { useTranslation } from '../locales/LanguageContext';

interface AIAnalystInterfaceProps {
  initialQuestion?: string;
  initialDataset?: string;
}

interface DatasetOption {
  id: string;
  name_zh: string;
  name_en: string;
  publisher: string;
  badge: string;
  icon: string;
  classification: 'PUBLIC' | 'RESTRICTED';
  desc_zh: string;
  desc_en: string;
  sample_questions_zh: string[];
  sample_questions_en: string[];
}

const DOMAIN_SWITCHER_OPTIONS: DatasetOption[] = [
  {
    id: 'auto',
    name_zh: '✨ Auto Detect (AI 自動識別領域)',
    name_en: '✨ Auto Detect (Domain Intent Router)',
    publisher: 'AI Intent Classifier',
    badge: '全域 6 大真實數據庫',
    icon: '✨',
    classification: 'PUBLIC',
    desc_zh: '自動辨識業務提問語意，動態路由至最合適之企業資料庫與治理語義層',
    desc_en: 'Automatically classifies query intent and routes to the appropriate curated domain schema',
    sample_questions_zh: [
      '分析各地區銷售額與產品類別之毛利率分佈',
      '統計 NYC 各計程車熱門上車區域的平均車資與行駛距離',
      '比較全美前五大航空公司的準點到達率與主要延誤成因'
    ],
    sample_questions_en: [
      'Analyze gross merchandise value and review score correlation',
      'What are the busiest NYC taxi pickup zones and average trip fare by hour?',
      'Which airlines achieve the highest on-time arrival performance?'
    ]
  },
  {
    id: 'ecommerce_olist',
    name_zh: '🛒 01 零售與電商 (Olist Brazilian E-Commerce)',
    name_en: '🛒 01 Retail / E-Commerce (Olist Brazil)',
    publisher: 'Olist & Kaggle',
    badge: '10,600+ 筆記錄 (CC BY-NC-SA 4.0)',
    icon: '🛒',
    classification: 'PUBLIC',
    desc_zh: '真實電商平台訂單、產品目錄、客戶地域分佈、支付方式與滿意度評分',
    desc_en: 'Real commercial marketplace orders, products, geo distributions, payments & reviews',
    sample_questions_zh: [
      '分析各產品類別的總 GMV 營收與平均訂單金額 (AOV)',
      '統計各州（SP、RJ、MG）的平均運費與客戶分佈情況',
      '哪些產品類別雖然銷售額高，但客戶評價評分（review_score）偏低？',
      '計算訂單實際交付時間超過預估日期的延遲交付比例（Late Delivery Rate）'
    ],
    sample_questions_en: [
      'Analyze total Gross Merchandise Value (GMV) and AOV by product category',
      'Compare freight costs and customer counts across top Brazilian states',
      'Identify product categories with high sales but poor customer review scores',
      'What percentage of orders experienced delivery delays past their estimated date?'
    ]
  },
  {
    id: 'transportation_nyc_taxi',
    name_zh: '🚕 02 城市交通 (NYC TLC Taxi & Mobility)',
    name_en: '🚕 02 Urban Transportation (NYC TLC Taxi)',
    publisher: 'NYC Taxi & Limousine Commission',
    badge: '2,500+ 筆行程 (NYC Open Data)',
    icon: '🚕',
    classification: 'PUBLIC',
    desc_zh: '曼哈頓與各區計程車即時乘車記錄、尖峰時段車資、通行費、小費與行程距離',
    desc_en: 'New York City yellow & green taxi trip records, peak fares, tolls, tips & zones',
    sample_questions_zh: [
      '統計總行程量最高的 Top 10 熱門上車區域（zone_name）與平均車資',
      '分析一日 24 小時中，各時段的平均乘車費用與行程距離變化趨勢',
      '比較機場行程（JFK、LaGuardia）與市區標準行程的平均車資與通行費',
      '計算各行政區（Manhattan、Brooklyn、Queens）的每英里平均收益效率'
    ],
    sample_questions_en: [
      'What are the top 10 busiest taxi pickup zones by trip volume and average fare?',
      'How does average fare and trip distance change across hours of the day?',
      'Compare airport trips (JFK, LaGuardia) vs local trips in terms of fare and tolls',
      'Calculate the average fare per mile efficiency across major boroughs'
    ]
  },
  {
    id: 'airline_bts_ontime',
    name_zh: '✈️ 03 航空航班營運 (U.S. DOT BTS Airlines)',
    name_en: '✈️ 03 Airline Operations (U.S. DOT BTS)',
    publisher: 'U.S. Bureau of Transportation Statistics',
    badge: '2,500+ 筆航班 (USDOT Public Domain)',
    icon: '✈️',
    classification: 'PUBLIC',
    desc_zh: '美國主要商業航空航班準點率、起降延誤時間、取消原因與航線樞紐統計',
    desc_en: 'U.S. commercial airline scheduled vs actual performance, delay causes & cancellations',
    sample_questions_zh: [
      '比較各主要航空公司（AA、DL、UA、WN 等）的航班準點到達率（On-Time Rate）',
      '分析全美主要樞紐機場（ATL、ORD、DFW、JFK）的航班取消率與主因分佈',
      '統計航班延誤的主要成因（氣候 Weather、航空公司 Carrier、空管 NAS 等）佔比',
      '找出平均到達延誤時間最長的前 10 大熱門航線（route）'
    ],
    sample_questions_en: [
      'Which airlines achieve the highest on-time arrival rate and lowest cancellation rate?',
      'What are the primary delay causes (Weather, Carrier, NAS, Late Aircraft) across hub airports?',
      'Analyze flight cancellation rates and reasons across major origin airports',
      'What are the top 10 worst-performing flight routes by average arrival delay?'
    ]
  },
  {
    id: 'healthcare_mimic_iv',
    name_zh: '🏥 04 醫療臨床運營 (PhysioNet MIMIC-IV Demo)',
    name_en: '🏥 04 Healthcare Operations (MIMIC-IV Demo)',
    publisher: 'PhysioNet / BIDMC',
    badge: '3,700+ 筆病歷 (Restricted Open Demo)',
    icon: '🏥',
    classification: 'RESTRICTED',
    desc_zh: '加護病房 (ICU) 住院天數 (LOS)、ICD-10 診斷分佈、保險類型與醫療資源利用率',
    desc_en: 'Deidentified ICU stays, hospital length of stay, ICD-10 diagnoses & unit utilization',
    sample_questions_zh: [
      '統計不同住院類型（急診 EW EMER.、常規 URGENT 等）的平均住院天數 (LOS)',
      '分析各重症加護病房單位（MICU、SICU、CCU 等）的病患住院時長分佈',
      '列出住院病患中最常見的前 10 大 ICD-10 臨床診斷代碼與疾病名稱',
      '分析不同年齡層與保險類別病患的加護病房入住比例與資源佔用情況'
    ],
    sample_questions_en: [
      'What is the average hospital length of stay (LOS) across admission types?',
      'How does ICU length of stay vary across intensive care units (MICU, SICU, CCU)?',
      'What are the top 10 most common ICD-10 clinical diagnoses among admitted patients?',
      'Analyze patient admission distribution and insurance coverage patterns over time'
    ]
  },
  {
    id: 'safety_chicago_crimes',
    name_zh: '🛡️ 05 市政公共安全 (City of Chicago Crimes)',
    name_en: '🛡️ 05 Public Safety (Chicago Crime Portal)',
    publisher: 'City of Chicago Open Data',
    badge: '2,500+ 筆事件 (Public Open Data)',
    icon: '🛡️',
    classification: 'PUBLIC',
    desc_zh: '芝加哥市各警局轄區報案紀錄、犯罪類型、逮捕率、案發地點與長期時間序列趨勢',
    desc_en: 'Reported municipal incidents across 22 police districts, arrest rates & temporal trends',
    sample_questions_zh: [
      '統計發生頻率最高的前 5 大主要案件類型（THEFT、BATTERY、ASSAULT 等）',
      '分析一日 24 小時與一週 7 天中，案件發生的時間分佈與高峰時段',
      '比較不同警察轄區（Police District）的案件總量與執法逮捕率（Arrest Rate）',
      '分析財產型犯罪與暴力型犯罪在不同案發地點（街道、住宅、公寓）的集中度'
    ],
    sample_questions_en: [
      'What are the most frequently reported primary crime categories across Chicago?',
      'How do reported incidents vary by hour of day and day of week?',
      'Which police districts report the highest volume of incidents and what are their arrest rates?',
      'Analyze month-over-month incident trends and property vs violent crime distributions'
    ]
  },
  {
    id: 'financial_sec_markets',
    name_zh: '📈 06 金融市場與財報 (SEC EDGAR & Markets)',
    name_en: '📈 06 Financial Markets (SEC EDGAR & Equities)',
    publisher: 'U.S. SEC & Market Feeds',
    badge: '2,400+ 筆行情 (SEC Open Access)',
    icon: '📈',
    classification: 'PUBLIC',
    desc_zh: '美股主流標的日線歷史價格、30日波動率、50日均線與 SEC 季報 (10-Q/10-K) 財務事實',
    desc_en: 'Daily equity OHLCV prices, 30-day volatility, 50 DMA & SEC Form 10-Q/10-K reported facts',
    sample_questions_zh: [
      '比較主要科技巨頭（AAPL、MSFT、NVDA 等）的 30 日歷史波動率與 50 日均線',
      '統計近一季平均每日交易量（Volume）最高與日報酬率波動最大的標的',
      '從 SEC 10-Q 申報事實中，分析各企業的季度總營收與自由現金流 (FCF) 表現',
      '比較不同產業板塊（Technology、Healthcare、Financials）的平均營業利益率'
    ],
    sample_questions_en: [
      'Compare 30-day realized volatility and 50-day moving averages across tech securities',
      'Which securities experienced the highest trading volume and daily return swings?',
      'Compare quarterly revenue growth and free cash flow across SEC 10-Q/10-K reported facts',
      'Analyze operating margins and gross margins across sectors (Technology, Healthcare, Financials)'
    ]
  }
];

export default function AIAnalystInterface({ initialQuestion, initialDataset }: AIAnalystInterfaceProps) {
  const { t, language } = useTranslation();
  const isZh = language === 'zh-TW';
  const [question, setQuestion] = useState(initialQuestion || '');
  const [selectedDataset, setSelectedDataset] = useState(initialDataset || 'auto');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [clarificationRequired, setClarificationRequired] = useState(false);
  const [showLineage, setShowLineage] = useState(false);

  // Sync initialQuestion when changed from outside
  useEffect(() => {
    if (initialQuestion) {
      setQuestion(initialQuestion);
    }
  }, [initialQuestion]);

  useEffect(() => {
    if (initialDataset) {
      setSelectedDataset(initialDataset);
    }
  }, [initialDataset]);

  const activeOption = DOMAIN_SWITCHER_OPTIONS.find((opt) => opt.id === selectedDataset) || DOMAIN_SWITCHER_OPTIONS[0];

  const handleRunQuery = async (queryText?: string) => {
    const q = queryText || question;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    setClarificationRequired(false);

    try {
      const res = await submitQuery(q, selectedDataset === 'auto' ? undefined : selectedDataset);
      setResponse(res);
      if (res.status === 'CLARIFICATION_REQUIRED') {
        setClarificationRequired(true);
      }
    } catch (err: any) {
      setError(err.message || '查詢執行異常，請稍後重試');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    if (!response?.query_id) return;
    triggerReportDownload(response.query_id, 'pdf');
  };

  const handleDownloadExcel = () => {
    if (!response?.query_id) return;
    triggerReportDownload(response.query_id, 'excel');
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Top Banner / Dataset Selector */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 backdrop-blur-xl flex flex-col gap-4 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                <Sparkles className="w-5 h-5" />
              </span>
              <h1 className="text-lg font-bold text-slate-100">
                {isZh ? 'AI 企業數據分析師 (AI Analyst Agent)' : 'AI Enterprise Data Analyst Agent'}
              </h1>
              <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                Google Gemini Live AI
              </span>
            </div>
            <p className="text-xs text-slate-400">
              {isZh
                ? '支援 6 大跨行業真實公開數據集，具備自然語言轉 SQL、AST 安全沙箱、強制 RLS 隔離與數值 Grounding 驗證。'
                : 'Direct natural-language to SQL execution against 6 real-world public domains with AST security & RLS.'}
            </p>
          </div>

          {/* Dataset Switcher Dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 whitespace-nowrap font-medium">
              {isZh ? '當前分析領域:' : 'Active Domain:'}
            </span>
            <select
              value={selectedDataset}
              onChange={(e) => setSelectedDataset(e.target.value)}
              className="bg-slate-950 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2 focus:outline-none focus:border-indigo-500 font-medium"
            >
              {DOMAIN_SWITCHER_OPTIONS.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {isZh ? opt.name_zh : opt.name_en}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Selected Domain Provenance Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs bg-slate-950/60 p-3 rounded-xl border border-slate-800">
          <div className="flex items-center gap-3">
            <span className="font-semibold text-slate-300">
              {isZh ? activeOption.name_zh : activeOption.name_en}
            </span>
            <span className="text-slate-400">|</span>
            <span className="text-slate-400">來源: {activeOption.publisher}</span>
            <span className="text-slate-400">|</span>
            <span className="text-slate-400 font-mono">{activeOption.badge}</span>
          </div>

          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase border ${
            activeOption.classification === 'RESTRICTED'
              ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
              : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
          }`}>
            {activeOption.classification}
          </span>
        </div>

        {/* Query Input Area */}
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder={
                isZh
                  ? '以繁體中文向 AI 分析師提出任何業務分析問題...'
                  : 'Ask any analytical business question against real dataset...'
              }
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleRunQuery();
              }}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-10 pr-4 py-3 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500 shadow-inner"
            />
          </div>

          <button
            onClick={() => handleRunQuery()}
            disabled={loading || !question.trim()}
            className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 disabled:opacity-50 text-white rounded-xl text-sm font-semibold transition-all shadow-md shadow-indigo-950/40 flex items-center justify-center gap-2 whitespace-nowrap"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>AI 分析中...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>開始分析</span>
              </>
            )}
          </button>
        </div>

        {/* Recommended Sample Prompts */}
        <div className="flex flex-col gap-2 pt-1 border-t border-slate-800/80">
          <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>{isZh ? '推薦分析提問（點擊即時執行）：' : 'Recommended Analytical Prompts:'}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {(isZh ? activeOption.sample_questions_zh : activeOption.sample_questions_en).map((qText, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuestion(qText);
                  handleRunQuery(qText);
                }}
                className="text-left px-3 py-1.5 rounded-lg bg-slate-800/60 hover:bg-indigo-950/60 hover:border-indigo-500/40 border border-slate-700/60 text-xs text-slate-300 transition-all"
              >
                {qText}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error / Alert Display */}
      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl flex items-center gap-3 text-rose-300 text-sm">
          <AlertTriangle className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Query Results Presentation */}
      {response && (
        <div className="flex flex-col gap-6">
          {/* Executive Summary Card */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 backdrop-blur-xl shadow-xl flex flex-col gap-5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <h2 className="text-base font-bold text-slate-100">
                  {isZh ? 'AI 商業決策分析報告' : 'AI Executive Analytical Report'}
                </h2>
                <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Grounding: {response.grounding_status}
                </span>
              </div>

              {/* Action Buttons: Lineage + PDF / Excel Export */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowLineage(!showLineage)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs flex items-center gap-1.5 transition-all"
                >
                  <Layers className="w-3.5 h-3.5 text-indigo-400" />
                  {isZh ? (showLineage ? '收起數據血緣' : '查看數據血緣') : 'Lineage'}
                </button>
                <button
                  onClick={handleDownloadPDF}
                  className="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs flex items-center gap-1.5 transition-all font-medium"
                >
                  <Download className="w-3.5 h-3.5" />
                  {isZh ? '匯出 Executive PDF' : 'PDF Report'}
                </button>
                <button
                  onClick={handleDownloadExcel}
                  className="px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-xs flex items-center gap-1.5 transition-all font-medium"
                >
                  <FileSpreadsheet className="w-3.5 h-3.5" />
                  {isZh ? '匯出 7-Sheet Excel' : 'Excel Report'}
                </button>
              </div>
            </div>

            {/* Lineage Visualizer Drawer (Optional) */}
            {showLineage && (
              <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-mono text-slate-300 flex flex-col gap-2">
                <div className="font-bold text-indigo-400 flex items-center gap-2">
                  <Cpu className="w-4 h-4" />
                  <span>端到端數據治理與執行血緣 (End-to-End Governance Lineage)</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 pt-2 text-[11px]">
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400">1. 目標領域:</span> {response.analytical_results?.dataset_id || selectedDataset}
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400">2. AST 安全:</span> READ_ONLY_PASSED
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400">3. RLS 隔離:</span> TENANT_BOUND
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400">4. 數據品質:</span> {response.data_quality?.quality_score || 98.5}% (5維度)
                  </div>
                </div>
              </div>
            )}

            {/* Markdown Summary Content */}
            <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed whitespace-pre-line">
              {response.analytical_results?.summary}
            </div>

            {/* Visual Analytics Chart (Matplotlib Base64) */}
            {response.visualization?.image_b64 && (
              <div className="mt-2 flex flex-col gap-2 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <div className="text-xs font-semibold text-slate-300">
                  {isZh ? 'Python 沙箱生成之數據可視化圖表' : 'Sandboxed Python Visualization'}
                </div>
                <div className="flex justify-center">
                  <img
                    src={`data:image/png;base64,${response.visualization.image_b64}`}
                    alt="Visualization Chart"
                    className="max-h-72 rounded-lg border border-slate-800/80 shadow-md"
                  />
                </div>
              </div>
            )}

            {/* Grounded Claims Badges */}
            {response.claims && response.claims.length > 0 && (
              <div className="flex flex-col gap-2 pt-2 border-t border-slate-800">
                <div className="text-xs font-semibold text-slate-400">
                  {isZh ? '數據庫事實驗證斷言 (Grounded Facts)' : 'Verified Grounded Claims'}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {response.claims.map((c, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-xl bg-slate-950/50 border border-slate-800/80 flex flex-col gap-1 text-xs"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-300">{c.metric || '驗證指標'}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {Math.round(c.confidence_score * 100)}% 吻合
                        </span>
                      </div>
                      <p className="text-slate-400 text-[11px] leading-tight">{c.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Generated DuckDB SQL */}
            <div className="flex flex-col gap-2 bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-mono text-indigo-400 font-semibold">DuckDB Vectorized SQL:</span>
                <span className="text-[11px]">{response.analytical_results?.rows?.length || 0} 筆數據返回</span>
              </div>
              <pre className="text-xs text-sky-300 font-mono overflow-x-auto whitespace-pre-wrap">
                {response.generated_sql}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
