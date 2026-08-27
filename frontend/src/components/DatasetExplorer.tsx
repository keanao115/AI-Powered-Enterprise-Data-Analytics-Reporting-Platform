'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  Database,
  Download,
  Search,
  Sparkles,
  ChevronRight,
  ShoppingCart,
  Car,
  Plane,
  Activity,
  ShieldAlert,
  TrendingUp,
  FileSpreadsheet,
  BarChart2,
  Table as TableIcon,
  CheckCircle2,
  ExternalLink,
  Shield,
  Layers,
  Calendar,
  Globe,
  Award
} from 'lucide-react';
import { DemoDataset, DatasetDetail } from '../types';
import { fetchDatasets, fetchDatasetDetails, getDatasetDownloadUrl } from '../lib/api';
import { useTranslation } from '../locales/LanguageContext';

interface DatasetExplorerProps {
  onSelectPromptForAnalyst?: (question: string, datasetId?: string) => void;
}

const DOMAIN_ICONS: Record<string, React.ReactNode> = {
  ShoppingCart: <ShoppingCart className="w-5 h-5 text-emerald-400" />,
  Car: <Car className="w-5 h-5 text-sky-400" />,
  Plane: <Plane className="w-5 h-5 text-indigo-400" />,
  Activity: <Activity className="w-5 h-5 text-rose-400" />,
  ShieldAlert: <ShieldAlert className="w-5 h-5 text-amber-400" />,
  TrendingUp: <TrendingUp className="w-5 h-5 text-purple-400" />,
};

export default function DatasetExplorer({ onSelectPromptForAnalyst }: DatasetExplorerProps) {
  const { t, language } = useTranslation();
  const isZh = language === 'zh-TW';
  const [datasets, setDatasets] = useState<DemoDataset[]>([]);
  const [selectedId, setSelectedId] = useState<string>('ecommerce_olist');
  const [datasetDetail, setDatasetDetail] = useState<DatasetDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [showStats, setShowStats] = useState<boolean>(true);

  // Load dataset list on mount
  useEffect(() => {
    async function loadList() {
      setLoading(true);
      try {
        const list = await fetchDatasets();
        setDatasets(list);
        if (list.length > 0) {
          setSelectedId(list[0].dataset_id || list[0].id || 'ecommerce_olist');
        }
      } catch (err) {
        console.error('Failed to fetch dataset list:', err);
      } finally {
        setLoading(false);
      }
    }
    loadList();
  }, []);

  // Fetch dataset details when selectedId changes or search changes
  useEffect(() => {
    if (!selectedId) return;
    let isCancelled = false;

    async function loadDetail() {
      setDetailLoading(true);
      try {
        const data = await fetchDatasetDetails(selectedId, searchQuery, 50, 0);
        if (!isCancelled && data) {
          setDatasetDetail(data);
        }
      } catch (err) {
        console.error('Failed to fetch dataset details:', err);
      } finally {
        if (!isCancelled) setDetailLoading(false);
      }
    }

    const timer = setTimeout(loadDetail, 250);
    return () => {
      isCancelled = true;
      clearTimeout(timer);
    };
  }, [selectedId, searchQuery]);

  const activeDataset = useMemo(() => {
    return datasets.find((d) => (d.dataset_id || d.id) === selectedId) || datasets[0];
  }, [datasets, selectedId]);

  // Client-side sorting for rows
  const sortedRows = useMemo(() => {
    if (!datasetDetail?.rows) return [];
    if (!sortColumn) return datasetDetail.rows;

    return [...datasetDetail.rows].sort((a, b) => {
      const valA = a[sortColumn];
      const valB = b[sortColumn];

      if (valA == null) return 1;
      if (valB == null) return -1;

      if (typeof valA === 'number' && typeof valB === 'number') {
        return sortDirection === 'asc' ? valA - valB : valB - valA;
      }
      const strA = String(valA).toLowerCase();
      const strB = String(valB).toLowerCase();
      if (strA < strB) return sortDirection === 'asc' ? -1 : 1;
      if (strA > strB) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [datasetDetail, sortColumn, sortDirection]);

  const handleSort = (col: string) => {
    if (sortColumn === col) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortColumn(col);
      setSortDirection('asc');
    }
  };

  const handleAskAI = (promptText: string) => {
    if (onSelectPromptForAnalyst) {
      onSelectPromptForAnalyst(promptText, selectedId);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <span className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Database className="w-6 h-6" />
            </span>
            <h1 className="text-xl font-bold text-slate-100">
              {isZh ? '企業真實示範數據中心' : 'Enterprise Real-World Dataset Catalog'}
            </h1>
          </div>
          <p className="text-sm text-slate-400">
            {isZh
              ? '6 大跨行業公共真實數據集 (Olist零售、NYC車資、BTS航班、MIMIC醫療、芝加哥治安、SEC財報)，支援 3-Tier 架構與實時 AI 數據分析。'
              : 'Six authentic public enterprise datasets across major industries with 3-tier raw/clean/curated architecture and full provenance.'}
          </p>
        </div>

        {activeDataset && (
          <div className="flex items-center gap-3">
            <a
              href={getDatasetDownloadUrl(activeDataset.dataset_id || activeDataset.id || selectedId)}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 rounded-xl text-sm font-medium transition-all shadow-sm"
            >
              <Download className="w-4 h-4 text-sky-400" />
              {isZh ? '下載 Curated CSV' : 'Export Curated CSV'}
            </a>
          </div>
        )}
      </div>

      {/* Main Grid: Left Selector Sidebar + Right Data View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: 6 Dataset Cards */}
        <div className="lg:col-span-4 flex flex-col gap-3">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-400 px-1 flex items-center justify-between">
            <span>{isZh ? '選擇真實數據領域' : 'SELECT DATASET DOMAIN'}</span>
            <span className="text-[11px] font-normal text-slate-400">{datasets.length} 領域就緒</span>
          </div>

          {loading ? (
            <div className="flex flex-col gap-3">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="h-28 bg-slate-900/40 rounded-xl border border-slate-800/60 animate-pulse" />
              ))}
            </div>
          ) : (
            datasets.map((d) => {
              const dId = d.dataset_id || d.id || '';
              const isSelected = selectedId === dId;
              const icon = DOMAIN_ICONS[d.icon] || <Database className="w-5 h-5 text-indigo-400" />;

              return (
                <button
                  key={dId}
                  onClick={() => {
                    setSelectedId(dId);
                    setSearchQuery('');
                  }}
                  className={`text-left p-4 rounded-xl border transition-all duration-200 flex flex-col gap-2 relative overflow-hidden group ${
                    isSelected
                      ? 'bg-gradient-to-br from-indigo-950/40 to-slate-900 border-indigo-500/50 shadow-lg shadow-indigo-950/30'
                      : 'bg-slate-900/40 hover:bg-slate-900/80 border-slate-800/70 hover:border-slate-700'
                  }`}
                >
                  {isSelected && (
                    <div className="absolute top-0 left-0 bottom-0 w-1 bg-indigo-500 rounded-l" />
                  )}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/50">
                        {icon}
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-slate-100 group-hover:text-indigo-300 transition-colors">
                          {d.dataset_name || d.name_zh || d.name_en}
                        </div>
                        <div className="text-[11px] text-slate-400">{d.domain || d.category_zh}</div>
                      </div>
                    </div>
                    <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {d.quality_score || 98}%
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/50">
                    <span className="flex items-center gap-1">
                      <Globe className="w-3 h-3 text-slate-400" /> {d.publisher}
                    </span>
                    <span className="font-mono text-slate-400">{d.row_count?.toLocaleString()} 筆記錄</span>
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Right: Active Dataset Deep-Dive & Data Table */}
        <div className="lg:col-span-8 flex flex-col gap-5">
          {activeDataset && (
            <>
              {/* Dataset Provenance & Metadata Banner */}
              <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 backdrop-blur-xl flex flex-col gap-4">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-slate-100">
                        {activeDataset.dataset_name}
                      </h2>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase border ${
                        activeDataset.data_classification === 'RESTRICTED'
                          ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      }`}>
                        {activeDataset.data_classification || 'PUBLIC'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      <span className="font-semibold text-slate-300">來源發布者:</span> {activeDataset.publisher} | <span className="font-semibold text-slate-300">授權:</span> {activeDataset.license}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <a
                      href={activeDataset.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs transition-all"
                    >
                      <ExternalLink className="w-3.5 h-3.5 text-indigo-400" />
                      官方公開源碼頁
                    </a>
                  </div>
                </div>

                {/* Provenance Pills */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-2.5 rounded-xl bg-slate-800/50 border border-slate-800">
                    <div className="text-slate-400 text-[10px]">涵蓋時間區間</div>
                    <div className="font-semibold text-slate-200 mt-0.5">{activeDataset.date_range}</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-800/50 border border-slate-800">
                    <div className="text-slate-400 text-[10px]">地理範圍</div>
                    <div className="font-semibold text-slate-200 mt-0.5">{activeDataset.geographic_scope}</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-800/50 border border-slate-800">
                    <div className="text-slate-400 text-[10px]">數據質量評分</div>
                    <div className="font-semibold text-emerald-400 mt-0.5">{activeDataset.quality_score}% (5維度合格)</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-800/50 border border-slate-800">
                    <div className="text-slate-400 text-[10px]">儲存格式</div>
                    <div className="font-semibold text-sky-300 mt-0.5 font-mono text-[11px]">3-Tier Parquet / DuckDB</div>
                  </div>
                </div>

                {/* Citation & Disclaimer */}
                <div className="text-[11px] text-slate-400 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 font-mono">
                  <span className="text-indigo-400 font-bold">Citation:</span> {activeDataset.citation}
                </div>
              </div>

              {/* Recommended 1-Click AI Questions */}
              {activeDataset.sample_queries && activeDataset.sample_queries.length > 0 && (
                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 flex flex-col gap-2.5">
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    <span>{isZh ? '精選商業分析提問（點擊直接由 AI Analyst 分析）' : 'Curated Enterprise Analytical Questions'}</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {activeDataset.sample_queries.map((q, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleAskAI(q)}
                        className="text-left px-3 py-2 rounded-xl bg-slate-800/60 hover:bg-indigo-950/50 hover:border-indigo-500/40 border border-slate-700/50 text-xs text-slate-200 transition-all flex items-start justify-between gap-2 group"
                      >
                        <span className="line-clamp-2">{q}</span>
                        <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all shrink-0 mt-0.5" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Data Table Search & Actions */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 flex flex-col gap-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <TableIcon className="w-4 h-4 text-indigo-400" />
                    <span className="text-sm font-semibold text-slate-200">
                      {isZh ? '資料表即時預覽' : 'Curated Table Data Grid'}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      ({datasetDetail?.total_rows ? datasetDetail.total_rows.toLocaleString() : 0} 筆可用)
                    </span>
                  </div>

                  <div className="relative w-full sm:w-64">
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      placeholder={isZh ? '在資料庫中搜尋...' : 'Search records...'}
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full bg-slate-950/80 border border-slate-700/70 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>

                {/* Table Content */}
                <div className="overflow-x-auto border border-slate-800 rounded-xl max-h-96">
                  {detailLoading ? (
                    <div className="p-12 text-center text-xs text-slate-400 animate-pulse flex flex-col items-center justify-center gap-2">
                      <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                      載入 DuckDB 向量化數據中...
                    </div>
                  ) : datasetDetail && datasetDetail.columns && datasetDetail.columns.length > 0 ? (
                    <table className="w-full text-left text-xs border-collapse">
                      <thead className="bg-slate-950/80 sticky top-0 border-b border-slate-800 text-slate-300 font-semibold">
                        <tr>
                          {datasetDetail.columns.map((col) => (
                            <th
                              key={col}
                              onClick={() => handleSort(col)}
                              className="px-3 py-2.5 whitespace-nowrap cursor-pointer hover:text-indigo-300 transition-colors"
                            >
                              <div className="flex items-center gap-1.5">
                                <span>{col}</span>
                                {sortColumn === col && (
                                  <span className="text-[10px] text-indigo-400">
                                    {sortDirection === 'asc' ? '▲' : '▼'}
                                  </span>
                                )}
                              </div>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 bg-slate-900/30">
                        {sortedRows.length > 0 ? (
                          sortedRows.map((row, rIdx) => (
                            <tr key={rIdx} className="hover:bg-slate-800/40 transition-colors font-mono text-[11px]">
                              {datasetDetail.columns.map((col) => (
                                <td key={col} className="px-3 py-2 text-slate-300 whitespace-nowrap">
                                  {row[col] != null ? String(row[col]) : <span className="text-slate-400 italic">null</span>}
                                </td>
                              ))}
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan={datasetDetail.columns.length} className="text-center py-8 text-slate-400">
                              無相符之數據記錄
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  ) : (
                    <div className="p-8 text-center text-xs text-slate-400">
                      尚未載入資料表架構
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
