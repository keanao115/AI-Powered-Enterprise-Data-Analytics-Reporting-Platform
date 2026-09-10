'use client';

import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { Database, Search, RefreshCw, Shield, Layers } from 'lucide-react';
import { fetchCatalog } from '../lib/api';
import { CatalogTable } from '../types';
import { useTranslation } from '../locales/LanguageContext';

const DEFAULT_TABLES: CatalogTable[] = [
  {
    name: 'sales_orders',
    desc: 'B2B 企業多區域銷售訂單數據集 (Global Sales & Margin)',
    columns: [
      { name: 'order_id', type: 'VARCHAR', classification: 'PUBLIC', description: '唯一訂單編號' },
      { name: 'customer_name', type: 'VARCHAR', classification: 'CONFIDENTIAL', description: '客戶企業全稱' },
      { name: 'region', type: 'VARCHAR', classification: 'PUBLIC', description: '銷售區域 (EMEA/APAC/NA)' },
      { name: 'country', type: 'VARCHAR', classification: 'PUBLIC', description: '國家代碼' },
      { name: 'product_category', type: 'VARCHAR', classification: 'PUBLIC', description: '商品類別' },
      { name: 'total_amount', type: 'DECIMAL', classification: 'PUBLIC', description: '訂單總金額 (USD)' },
      { name: 'gross_margin_pct', type: 'DECIMAL', classification: 'PUBLIC', description: '毛利率百分比' },
      { name: 'sales_rep', type: 'VARCHAR', classification: 'PUBLIC', description: '負責業務代表' },
    ],
  },
  {
    name: 'customers',
    desc: '客戶個人資訊與 PII 隱私防護 (Customer Demographics & PII)',
    columns: [
      { name: 'id', type: 'VARCHAR', classification: 'PUBLIC', description: '客戶識別號' },
      { name: 'name', type: 'VARCHAR', classification: 'CONFIDENTIAL', description: '客戶姓名' },
      { name: 'email', type: 'VARCHAR', classification: 'CONFIDENTIAL', description: '電子郵件地址' },
      { name: 'ssn', type: 'VARCHAR', classification: 'RESTRICTED', description: '社會安全碼' },
      { name: 'credit_card', type: 'VARCHAR', classification: 'RESTRICTED', description: '信用卡卡號' },
    ],
  },
];

export default function DataDictionary() {
  const { t } = useTranslation();
  const [tables, setTables] = useState<CatalogTable[]>(DEFAULT_TABLES);
  const [loading, setLoading] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const loadCatalog = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchCatalog();
      if (Array.isArray(data) && data.length > 0) {
        setTables(data);
      }
    } catch (err) {
      console.error('Failed to load schema catalog:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCatalog();
  }, [loadCatalog]);

  const filteredTables = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return tables;
    return tables.filter((tbl) => {
      const matchName = tbl.name.toLowerCase().includes(q);
      const matchDesc = tbl.desc?.toLowerCase().includes(q);
      const matchCols = tbl.columns?.some(
        (c) =>
          c.name.toLowerCase().includes(q) ||
          c.type.toLowerCase().includes(q) ||
          c.description?.toLowerCase().includes(q)
      );
      return matchName || matchDesc || matchCols;
    });
  }, [tables, searchQuery]);

  const totalColumns = useMemo(() => {
    return tables.reduce((acc, tbl) => acc + (tbl.columns?.length || 0), 0);
  }, [tables]);

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              <Database className="w-4 h-4 text-sky-400" />
              {t.dictionaryTitle}
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">{t.dictionarySubtitle}</p>
          </div>

          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 font-mono">
              <Layers className="w-3.5 h-3.5 text-sky-400" />
              {tables.length} {t.dictTotalTables} · {totalColumns} {t.dictTotalColumns}
            </span>

            <button
              onClick={loadCatalog}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition disabled:opacity-50"
              title={t.dictRefreshBtn}
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-sky-400' : ''}`} />
              <span>{t.dictRefreshBtn}</span>
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t.dictSearchPlaceholder}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition"
          />
        </div>
      </div>

      {/* Tables List */}
      {filteredTables.length === 0 ? (
        <div className="bg-slate-900 border border-dashed border-slate-800 rounded-xl p-12 text-center text-slate-500 text-xs">
          沒有符合搜尋條件的資料表
        </div>
      ) : (
        filteredTables.map((tbl) => (
          <div key={tbl.name} className="bg-slate-900 border border-slate-800 rounded-xl p-4 transition hover:border-slate-700">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-sky-500/10 rounded-lg border border-sky-500/20">
                  <Database className="w-4 h-4 text-sky-400" />
                </div>
                <div>
                  <h4 className="font-mono font-semibold text-slate-100 text-sm">{tbl.name}</h4>
                  <p className="text-xs text-slate-400">{tbl.desc}</p>
                </div>
              </div>
              <span className="text-[11px] font-mono text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                {tbl.columns.length} cols
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
                  <tr>
                    <th className="px-3 py-2">{t.colColumnName}</th>
                    <th className="px-3 py-2">{t.colDataType}</th>
                    <th className="px-3 py-2">Classification</th>
                    <th className="px-3 py-2">{t.colPiiRule}</th>
                    <th className="px-3 py-2">{t.colDescription}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {tbl.columns.map((c) => (
                    <tr key={c.name} className="hover:bg-slate-800/40 font-mono">
                      <td className="px-3 py-2 font-semibold text-slate-200">{c.name}</td>
                      <td className="px-3 py-2 text-sky-400">{c.type}</td>
                      <td className="px-3 py-2">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                            c.classification === 'RESTRICTED'
                              ? 'bg-rose-950 text-rose-300 border-rose-800/60'
                              : c.classification === 'CONFIDENTIAL'
                              ? 'bg-amber-950 text-amber-300 border-amber-800/60'
                              : c.classification === 'INTERNAL'
                              ? 'bg-blue-950 text-blue-300 border-blue-800/60'
                              : 'bg-emerald-950 text-emerald-300 border-emerald-800/60'
                          }`}
                        >
                          {c.classification}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-slate-400 font-sans">
                        {c.classification === 'RESTRICTED' ? (
                          <span className="flex items-center gap-1 text-rose-300">
                            <Shield className="w-3 h-3 text-rose-400" />
                            {t.ruleMasked}
                          </span>
                        ) : c.classification === 'CONFIDENTIAL' ? (
                          <span className="text-amber-300">{t.ruleHashed}</span>
                        ) : (
                          <span className="text-slate-500">{t.ruleNone}</span>
                        )}
                      </td>
                      <td className="px-3 py-2 text-slate-400 font-sans">{c.description || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

