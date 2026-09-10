'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { ShieldCheck, RefreshCw, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { fetchAuditLogs } from '../lib/api';
import { AuditLogItem } from '../types';
import { useTranslation } from '../locales/LanguageContext';

export default function AuditLogViewer() {
  const { t } = useTranslation();
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [filter, setFilter] = useState<'ALL' | 'BLOCKED' | 'ALLOWED'>('ALL');

  const loadLogs = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchAuditLogs();
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  const filteredLogs = logs.filter((log) => {
    if (filter === 'BLOCKED') return log.result === 'BLOCKED';
    if (filter === 'ALLOWED') return log.result === 'ALLOWED';
    return true;
  });

  const blockedCount = logs.filter((l) => l.result === 'BLOCKED').length;
  const allowedCount = logs.filter((l) => l.result === 'ALLOWED').length;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            {t.auditTitle}
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">{t.auditSubtitle}</p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          {/* Filter Pills */}
          <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
            <button
              onClick={() => setFilter('ALL')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                filter === 'ALL'
                  ? 'bg-sky-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {t.auditFilterAll} ({logs.length})
            </button>
            <button
              onClick={() => setFilter('BLOCKED')}
              className={`px-2.5 py-1 rounded font-medium flex items-center gap-1 transition-colors ${
                filter === 'BLOCKED'
                  ? 'bg-rose-600 text-white shadow'
                  : 'text-slate-400 hover:text-rose-300'
              }`}
            >
              <AlertTriangle className="w-3 h-3" />
              {t.auditFilterBlocked} ({blockedCount})
            </button>
            <button
              onClick={() => setFilter('ALLOWED')}
              className={`px-2.5 py-1 rounded font-medium flex items-center gap-1 transition-colors ${
                filter === 'ALLOWED'
                  ? 'bg-emerald-600 text-white shadow'
                  : 'text-slate-400 hover:text-emerald-300'
              }`}
            >
              <CheckCircle2 className="w-3 h-3" />
              {t.auditFilterAllowed} ({allowedCount})
            </button>
          </div>

          {/* Refresh Button */}
          <button
            onClick={loadLogs}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition disabled:opacity-50"
            title={t.auditRefreshBtn}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-sky-400' : ''}`} />
            <span>{loading ? t.auditRefreshingBtn : t.auditRefreshBtn}</span>
          </button>
        </div>
      </div>

      {filteredLogs.length === 0 ? (
        <div className="text-center py-12 text-slate-500 text-xs border border-dashed border-slate-800 rounded-lg">
          {t.auditEmptyLogs}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 font-semibold">
              <tr>
                <th className="px-3 py-2.5">{t.colTimestamp}</th>
                <th className="px-3 py-2.5">{t.colAction}</th>
                <th className="px-3 py-2.5">Resource</th>
                <th className="px-3 py-2.5">{t.colResult}</th>
                <th className="px-3 py-2.5">{t.colRiskLevel}</th>
                <th className="px-3 py-2.5">{t.colReason}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filteredLogs.map((log) => (
                <tr key={log.event_id} className="hover:bg-slate-800/40 font-mono transition-colors">
                  <td className="px-3 py-2.5 text-slate-400 whitespace-nowrap">{log.timestamp}</td>
                  <td className="px-3 py-2.5 font-semibold text-slate-200">{log.action}</td>
                  <td className="px-3 py-2.5 text-slate-300 truncate max-w-xs">{log.resource}</td>
                  <td className="px-3 py-2.5">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                        log.result === 'BLOCKED'
                          ? 'bg-rose-950 text-rose-300 border-rose-800/60'
                          : 'bg-emerald-950 text-emerald-300 border-emerald-800/60'
                      }`}
                    >
                      {log.result}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 font-semibold">
                    <span
                      className={`${
                        log.risk_level === 'CRITICAL' || log.risk_level === 'HIGH'
                          ? 'text-rose-400'
                          : log.risk_level === 'MEDIUM'
                          ? 'text-amber-400'
                          : 'text-emerald-400'
                      }`}
                    >
                      {log.risk_level}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 text-slate-400 max-w-md break-words">{log.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
