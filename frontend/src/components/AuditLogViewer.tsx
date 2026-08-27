'use client';

import React, { useEffect, useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import { fetchAuditLogs } from '../lib/api';
import { AuditLogItem } from '../types';
import { useTranslation } from '../locales/LanguageContext';

export default function AuditLogViewer() {
  const { t } = useTranslation();
  const [logs, setLogs] = useState<AuditLogItem[]>([]);

  useEffect(() => {
    fetchAuditLogs().then(setLogs);
  }, []);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-4">
      <div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 mb-1">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          {t.auditTitle}
        </h3>
        <p className="text-xs text-slate-400">{t.auditSubtitle}</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 font-semibold">
            <tr>
              <th className="px-3 py-2">{t.colTimestamp}</th>
              <th className="px-3 py-2">{t.colAction}</th>
              <th className="px-3 py-2">Resource</th>
              <th className="px-3 py-2">{t.colResult}</th>
              <th className="px-3 py-2">{t.colRiskLevel}</th>
              <th className="px-3 py-2">{t.colReason}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {logs.map((log) => (
              <tr key={log.event_id} className="hover:bg-slate-800/40 font-mono">
                <td className="px-3 py-2 text-slate-400">{log.timestamp}</td>
                <td className="px-3 py-2 font-semibold text-slate-200">{log.action}</td>
                <td className="px-3 py-2 text-slate-300 truncate max-w-xs">{log.resource}</td>
                <td className="px-3 py-2">
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
                <td className="px-3 py-2 font-semibold text-rose-400">{log.risk_level}</td>
                <td className="px-3 py-2 text-slate-400">{log.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
