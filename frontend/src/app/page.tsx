'use client';

import React, { useState } from 'react';
import {
  Bot,
  Shield,
  Database,
  GitBranch,
  ShieldCheck,
  PlayCircle,
  FileSpreadsheet
} from 'lucide-react';
import AIAnalystInterface from '../components/AIAnalystInterface';
import DatasetExplorer from '../components/DatasetExplorer';
import SQLInspector from '../components/SQLInspector';
import DataProvenanceView from '../components/DataProvenanceView';
import DataDictionary from '../components/DataDictionary';
import AuditLogViewer from '../components/AuditLogViewer';
import EvaluationDashboard from '../components/EvaluationDashboard';
import LanguageSelector from '../components/LanguageSelector';
import { useTranslation } from '../locales/LanguageContext';

export default function Home() {
  const [activeTab, setActiveTab] = useState<
    'analyst' | 'datasets' | 'sql' | 'provenance' | 'dictionary' | 'audit' | 'eval'
  >('analyst');
  const [selectedPrompt, setSelectedPrompt] = useState<string>('');
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const { t } = useTranslation();

  const getTabTitle = () => {
    switch (activeTab) {
      case 'analyst':
        return t.navAnalyst;
      case 'datasets':
        return t.navDatasets;
      case 'sql':
        return t.navSql;
      case 'provenance':
        return t.navProvenance;
      case 'dictionary':
        return t.navDictionary;
      case 'audit':
        return t.navAudit;
      case 'eval':
        return t.navEval;
      default:
        return t.navAnalyst;
    }
  };

  const handleSelectPromptFromExplorer = (prompt: string, datasetId?: string) => {
    setSelectedPrompt(prompt);
    if (datasetId) {
      setSelectedDataset(datasetId);
    }
    setActiveTab('analyst');
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0">
        <div>
          {/* Brand Header */}
          <div className="p-4 border-b border-slate-800 space-y-3">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-tr from-sky-500 to-blue-600 rounded-xl shadow-lg shadow-sky-500/20">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-sm text-slate-100 leading-tight">{t.appTitle}</h1>
                <span className="text-[10px] text-slate-400 font-mono">{t.appSubtitle}</span>
              </div>
            </div>
            <div className="pt-1">
              <LanguageSelector />
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="p-3 space-y-1">
            <button
              onClick={() => setActiveTab('analyst')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'analyst'
                  ? 'bg-sky-600/20 text-sky-400 border border-sky-500/30'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Bot className="w-4 h-4" />
              {t.navAnalyst}
            </button>

            <button
              onClick={() => setActiveTab('datasets')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'datasets'
                  ? 'bg-sky-600/20 text-sky-400 border border-sky-500/30'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <FileSpreadsheet className="w-4 h-4" />
              {t.navDatasets}
            </button>

            <button
              onClick={() => setActiveTab('sql')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'sql'
                  ? 'bg-sky-600/20 text-sky-400 border border-sky-500/30'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Shield className="w-4 h-4" />
              {t.navSql}
            </button>

            <button
              onClick={() => setActiveTab('provenance')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'provenance'
                  ? 'bg-sky-600/20 text-sky-400 border border-sky-500/30'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <GitBranch className="w-4 h-4" />
              {t.navProvenance}
            </button>

            <button
              onClick={() => setActiveTab('dictionary')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'dictionary'
                  ? 'bg-sky-600/20 text-sky-400 border border-sky-500/30'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Database className="w-4 h-4" />
              {t.navDictionary}
            </button>

            <button
              onClick={() => setActiveTab('audit')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'audit'
                  ? 'bg-sky-600/20 text-sky-400 border border-sky-500/30'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              {t.navAudit}
            </button>

            <button
              onClick={() => setActiveTab('eval')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'eval'
                  ? 'bg-sky-600/20 text-sky-400 border border-sky-500/30'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <PlayCircle className="w-4 h-4" />
              {t.navEval}
            </button>
          </nav>
        </div>

        {/* Tenant & User Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950/40 text-xs">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span>{t.tenantLabel}</span>
            <span className="font-mono text-slate-200 font-semibold">tenant-acme</span>
          </div>
          <div className="flex items-center justify-between text-slate-400">
            <span>{t.userRoleLabel}</span>
            <span className="bg-emerald-950 text-emerald-300 border border-emerald-800/60 px-1.5 py-0.5 rounded text-[10px] font-semibold">
              ORG_ADMIN
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-6 bg-slate-950">
        <header className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
          <div>
            <h2 className="text-xl font-bold text-slate-100">{getTabTitle()}</h2>
            <p className="text-xs text-slate-400">{t.portalSubtitle}</p>
          </div>
          <div className="flex items-center gap-3">
            <LanguageSelector />
            <span className="flex items-center gap-1.5 bg-emerald-950 text-emerald-300 border border-emerald-800/60 px-3 py-1 rounded-full text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              {t.systemStatusOperational}
            </span>
          </div>
        </header>

        {activeTab === 'analyst' && (
          <AIAnalystInterface initialQuestion={selectedPrompt} initialDataset={selectedDataset} />
        )}
        {activeTab === 'datasets' && (
          <DatasetExplorer onSelectPromptForAnalyst={handleSelectPromptFromExplorer} />
        )}
        {activeTab === 'sql' && <SQLInspector />}
        {activeTab === 'provenance' && <DataProvenanceView />}
        {activeTab === 'dictionary' && <DataDictionary />}
        {activeTab === 'audit' && <AuditLogViewer />}
        {activeTab === 'eval' && <EvaluationDashboard />}
      </main>
    </div>
  );
}

