'use client';

import React from 'react';
import { Database, Lock, Eye, ShieldAlert } from 'lucide-react';
import { useTranslation } from '../locales/LanguageContext';

export default function DataDictionary() {
  const { t } = useTranslation();

  const tables = [
    {
      name: 'sales_orders',
      desc: 'B2B 企業多區域銷售訂單數據集 (Global Sales & Margin)',
      columns: [
        { name: 'order_id', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'customer_name', type: 'VARCHAR', classification: 'CONFIDENTIAL' },
        { name: 'region', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'country', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'product_category', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'total_amount', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'gross_margin_pct', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'sales_rep', type: 'VARCHAR', classification: 'PUBLIC' },
      ],
    },
    {
      name: 'customer_churn',
      desc: 'SaaS 客戶健康度、留存率與流失預警 (SaaS Retention & NPS)',
      columns: [
        { name: 'customer_id', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'company_name', type: 'VARCHAR', classification: 'CONFIDENTIAL' },
        { name: 'industry', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'subscription_tier', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'mrr_usd', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'nps_score', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'churn_risk_score', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'account_status', type: 'VARCHAR', classification: 'PUBLIC' },
      ],
    },
    {
      name: 'inventory_supply_chain',
      desc: '全球倉儲中心庫存水準與供應鏈警戒 (Supply Chain & Warehouses)',
      columns: [
        { name: 'sku_id', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'warehouse_location', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'product_name', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'current_stock', type: 'INT', classification: 'PUBLIC' },
        { name: 'safety_stock', type: 'INT', classification: 'PUBLIC' },
        { name: 'supplier_name', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'inventory_turnover_ratio', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'stock_status', type: 'VARCHAR', classification: 'PUBLIC' },
      ],
    },
    {
      name: 'financial_metrics',
      desc: '企業季度損益表與各部門預算 (Financial P&L & EBITDA)',
      columns: [
        { name: 'fiscal_quarter', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'fiscal_year', type: 'INT', classification: 'PUBLIC' },
        { name: 'department', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'revenue_usd', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'gross_profit_usd', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'opex_usd', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'ebitda_usd', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'headcount', type: 'INT', classification: 'PUBLIC' },
      ],
    },
    {
      name: 'employee_performance',
      desc: '人力資源績效、工作地點與員工滿意度 (HR & Workforce Analytics)',
      columns: [
        { name: 'employee_id', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'department', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'job_title', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'work_location', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'performance_rating', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'salary_band', type: 'VARCHAR', classification: 'INTERNAL' },
        { name: 'satisfaction_score', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'attrition_risk', type: 'VARCHAR', classification: 'PUBLIC' },
      ],
    },
    {
      name: 'marketing_campaigns',
      desc: '全通路行銷活動 ROI、CAC 與廣告花費 (Marketing Attribution & ROAS)',
      columns: [
        { name: 'campaign_id', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'campaign_name', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'channel', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'ad_spend_usd', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'conversions', type: 'INT', classification: 'PUBLIC' },
        { name: 'cost_per_acquisition_usd', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'revenue_generated_usd', type: 'DECIMAL', classification: 'PUBLIC' },
        { name: 'return_on_ad_spend', type: 'DECIMAL', classification: 'PUBLIC' },
      ],
    },
    {
      name: 'customers',
      desc: '客戶個人資訊與 PII 隱私防護 (Customer Demographics & PII)',
      columns: [
        { name: 'id', type: 'VARCHAR', classification: 'PUBLIC' },
        { name: 'name', type: 'VARCHAR', classification: 'CONFIDENTIAL' },
        { name: 'email', type: 'VARCHAR', classification: 'CONFIDENTIAL' },
        { name: 'ssn', type: 'VARCHAR', classification: 'RESTRICTED' },
        { name: 'credit_card', type: 'VARCHAR', classification: 'RESTRICTED' },
      ],
    },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
        <h3 className="text-sm font-semibold text-slate-100 mb-1">{t.dictionaryTitle}</h3>
        <p className="text-xs text-slate-400 mb-4">{t.dictionarySubtitle}</p>
      </div>

      {tables.map((tbl) => (
        <div key={tbl.name} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Database className="w-4 h-4 text-sky-400" />
            <h4 className="font-semibold text-slate-100 text-sm">{tbl.name}</h4>
            <span className="text-xs text-slate-400">• {tbl.desc}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-3 py-2">{t.colColumnName}</th>
                  <th className="px-3 py-2">{t.colDataType}</th>
                  <th className="px-3 py-2">Classification</th>
                  <th className="px-3 py-2">{t.colPiiRule}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {tbl.columns.map((c) => (
                  <tr key={c.name} className="hover:bg-slate-800/40">
                    <td className="px-3 py-2 font-mono">{c.name}</td>
                    <td className="px-3 py-2 text-slate-400">{c.type}</td>
                    <td className="px-3 py-2">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                          c.classification === 'RESTRICTED'
                            ? 'bg-rose-950 text-rose-300 border-rose-800/60'
                            : c.classification === 'CONFIDENTIAL'
                            ? 'bg-amber-950 text-amber-300 border-amber-800/60'
                            : 'bg-emerald-950 text-emerald-300 border-emerald-800/60'
                        }`}
                      >
                        {c.classification}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-slate-400">
                      {c.classification === 'RESTRICTED' ? t.ruleMasked : t.ruleNone}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
