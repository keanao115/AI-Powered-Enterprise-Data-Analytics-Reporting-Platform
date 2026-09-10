'use client';

import React, { useState, useEffect } from 'react';
import {
  Bot,
  Shield,
  Database,
  GitBranch,
  ShieldCheck,
  PlayCircle,
  FileSpreadsheet,
  Sliders,
  UserCheck
} from 'lucide-react';
import AIAnalystInterface from '../components/AIAnalystInterface';
import DatasetExplorer from '../components/DatasetExplorer';
import SQLInspector from '../components/SQLInspector';
import DataProvenanceView from '../components/DataProvenanceView';
import DataDictionary from '../components/DataDictionary';
import AuditLogViewer from '../components/AuditLogViewer';
import EvaluationDashboard from '../components/EvaluationDashboard';
import SettingsManager from '../components/SettingsManager';
import LanguageSelector from '../components/LanguageSelector';
import { useTranslation } from '../locales/LanguageContext';
import { loginUser, getAuthToken } from '../lib/api';

interface Persona {
  email: string;
  nameKey: 'personaAdminAcme' | 'personaAnalystAcme' | 'personaViewerAcme' | 'personaAdminGlobex' | 'personaAnalystGlobex';
  tenant_id: string;
  role: 'ORG_ADMIN' | 'ANALYST' | 'VIEWER';
}

const PERSONAS: Persona[] = [
  {
    email: 'admin@acme.com',
    nameKey: 'personaAdminAcme',
    tenant_id: 'tenant-acme',
    role: 'ORG_ADMIN',
  },
  {
    email: 'analyst@acme.com',
    nameKey: 'personaAnalystAcme',
    tenant_id: 'tenant-acme',
    role: 'ANALYST',
  },
  {
    email: 'viewer@acme.com',
    nameKey: 'personaViewerAcme',
    tenant_id: 'tenant-acme',
    role: 'VIEWER',
  },
  {
    email: 'admin@globex.com',
    nameKey: 'personaAdminGlobex',
    tenant_id: 'tenant-globex',
    role: 'ORG_ADMIN',
  },
  {
    email: 'analyst@globex.com',
    nameKey: 'personaAnalystGlobex',
    tenant_id: 'tenant-globex',
    role: 'ANALYST',
  },
];


export default function Home() {
  const [activeTab, setActiveTab] = useState<
    'analyst' | 'datasets' | 'sql' | 'provenance' | 'dictionary' | 'audit' | 'eval' | 'settings'
  >('analyst');
  const [selectedPrompt, setSelectedPrompt] = useState<string>('');
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [currentPersona, setCurrentPersona] = useState<Persona>(PERSONAS[0]);
  const [switching, setSwitching] = useState<boolean>(false);
  const { t } = useTranslation();

  useEffect(() => {
    if (!getAuthToken()) {
      loginUser(PERSONAS[0].email, 'password123').catch(() => {});
    }
  }, []);

  const handleSwitchPersona = async (email: string) => {
    const found = PERSONAS.find((p) => p.email === email);
    if (!found) return;
    setSwitching(true);
    try {
      await loginUser(found.email, 'password123');
      setCurrentPersona(found);
    } catch (err) {
      console.error('Persona switch failed:', err);
    } finally {
      setSwitching(false);
    }
  };


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
      case 'settings':
        return t.navSettings;
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

            <button
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                activeTab === 'settings'
                  ? 'bg-sky-600/20 text-sky-400 border border-sky-500/30'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Sliders className="w-4 h-4" />
              {t.navSettings}
            </button>
          </nav>
        </div>

        {/* Tenant & User Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950/60 text-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-medium flex items-center gap-1">
              <UserCheck className="w-3.5 h-3.5 text-sky-400" />
              {t.switchPersonaTitle}
            </span>
            {switching && <span className="text-[10px] text-sky-400 animate-pulse">切換中...</span>}
          </div>

          <select
            value={currentPersona.email}
            onChange={(e) => handleSwitchPersona(e.target.value)}
            disabled={switching}
            aria-label={t.switchPersonaTitle}
            className="w-full bg-slate-900 border border-slate-700 hover:border-slate-600 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 font-medium focus:outline-none focus:border-sky-500 transition cursor-pointer"
          >
            {PERSONAS.map((p) => (
              <option key={p.email} value={p.email}>
                {t[p.nameKey]}
              </option>
            ))}
          </select>

          <div className="pt-1 space-y-1 text-[11px]">
            <div className="flex items-center justify-between text-slate-400">
              <span>{t.tenantLabel}</span>
              <span className="font-mono text-slate-200 font-semibold">{currentPersona.tenant_id}</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>{t.userRoleLabel}</span>
              <span
                className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border ${
                  currentPersona.role === 'ORG_ADMIN'
                    ? 'bg-emerald-950 text-emerald-300 border-emerald-800/60'
                    : currentPersona.role === 'ANALYST'
                    ? 'bg-sky-950 text-sky-300 border-sky-800/60'
                    : 'bg-slate-800 text-slate-300 border-slate-700'
                }`}
              >
                {currentPersona.role}
              </span>
            </div>
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
            <div className="hidden lg:flex items-center gap-2 px-3 py-1 bg-slate-900 border border-slate-800 rounded-lg text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-slate-300 font-mono">{currentPersona.email}</span>
              <span className="text-slate-500 font-mono">({currentPersona.tenant_id})</span>
            </div>
            <LanguageSelector />
            <span className="flex items-center gap-1.5 bg-emerald-950 text-emerald-300 border border-emerald-800/60 px-3 py-1 rounded-full text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              {t.systemStatusOperational}
            </span>
          </div>
        </header>


        {activeTab === 'analyst' && (
          <AIAnalystInterface
            initialQuestion={selectedPrompt}
            initialDataset={selectedDataset}
            onNavigateToSettings={() => setActiveTab('settings')}
          />
        )}
        {activeTab === 'datasets' && (
          <DatasetExplorer onSelectPromptForAnalyst={handleSelectPromptFromExplorer} />
        )}
        {activeTab === 'sql' && <SQLInspector />}
        {activeTab === 'provenance' && <DataProvenanceView />}
        {activeTab === 'dictionary' && <DataDictionary />}
        {activeTab === 'audit' && <AuditLogViewer />}
        {activeTab === 'eval' && <EvaluationDashboard />}
        {activeTab === 'settings' && <SettingsManager />}
      </main>
    </div>
  );
}

