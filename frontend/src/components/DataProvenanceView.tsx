'use client';

import React from 'react';
import { GitBranch } from 'lucide-react';
import { useTranslation } from '../locales/LanguageContext';

export default function DataProvenanceView() {
  const { t } = useTranslation();

  const steps = [
    { title: t.nodeSourceDb, desc: 'orders, order_items, products, regions' },
    { title: t.nodeSemanticLayer, desc: 'Metric: Revenue = SUM(orders.amount) WHERE status = "completed"' },
    { title: t.nodeAstPolicy, desc: t.rlsApplied },
    { title: t.stepDatabaseExecution, desc: 'Executed against DuckDB Analytics Engine (12.5ms)' },
    { title: t.stepInsightGrounding, desc: 'Score: 98.5% | 100% claims verified against facts' },
    { title: t.nodeFinalReport, desc: 'PDF / Excel Report Artifact generated' },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-4">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
        <GitBranch className="w-4 h-4 text-sky-400" />
        {t.provenanceTitle}
      </h3>
      <p className="text-xs text-slate-400">{t.provenanceSubtitle}</p>
      <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
        {steps.map((s, idx) => (
          <div key={idx} className="relative flex items-start gap-3">
            <div className="absolute -left-6 top-1 w-3 h-3 rounded-full bg-sky-500 ring-4 ring-slate-900" />
            <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-3 w-full text-xs">
              <div className="font-semibold text-slate-200">{s.title}</div>
              <div className="text-slate-400 mt-0.5">{s.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
