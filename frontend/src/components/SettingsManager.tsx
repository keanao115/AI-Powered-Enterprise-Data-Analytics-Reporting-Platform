'use client';

import React, { useState, useEffect } from 'react';
import {
  Key,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Eye,
  EyeOff,
  Sparkles,
  Zap,
  Server,
  ShieldCheck,
  Send,
  Save,
  Check,
  Trash2,
  X,
  Plus,
  Layers,
  Network,
  Bot,
  ArrowRight,
  HelpCircle,
} from 'lucide-react';
import {
  fetchLLMSettings,
  updateLLMSettings,
  testLLMConnection,
  detectApiKeyProvider,
  fetchKeyVault,
  saveKeyVaultItem,
  deleteKeyVaultItem,
  activateKeyVaultItem,
  fetchCollaborationSettings,
  saveCollaborationSettings,
} from '../lib/api';
import {
  LLMConfigResponse,
  TestLLMConnectionResponse,
  DetectKeyResponse,
  VaultKeyItem,
  CollaborationSettings,
} from '../types';
import { useTranslation } from '../locales/LanguageContext';

export default function SettingsManager() {
  const { t } = useTranslation();

  const [config, setConfig] = useState<LLMConfigResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Active Single Model Settings
  const [selectedProvider, setSelectedProvider] = useState<string>('gemini');
  const [selectedModel, setSelectedModel] = useState<string>('gemini-flash-latest');
  const [isCustomModel, setIsCustomModel] = useState<boolean>(false);
  const [customModelInput, setCustomModelInput] = useState<string>('');
  const [customBaseUrlInput, setCustomBaseUrlInput] = useState<string>('');

  // Universal Smart Key Input & Auto-Detection
  const [universalKeyInput, setUniversalKeyInput] = useState<string>('');
  const [showUniversalKey, setShowUniversalKey] = useState<boolean>(false);
  const [detectedInfo, setDetectedInfo] = useState<DetectKeyResponse | null>(null);
  const [detecting, setDetecting] = useState<boolean>(false);
  const [keyLabelInput, setKeyLabelInput] = useState<string>('');

  // Multi-API Vault
  const [vaultKeys, setVaultKeys] = useState<VaultKeyItem[]>([]);
  const [vaultLoading, setVaultLoading] = useState<boolean>(false);

  // Multi-Model Collaboration
  const [collabConfig, setCollabConfig] = useState<CollaborationSettings | null>(null);
  const [collabEnabled, setCollabEnabled] = useState<boolean>(false);
  const [roleSqlGen, setRoleSqlGen] = useState<string>('');
  const [roleReviewer, setRoleReviewer] = useState<string>('');
  const [roleInsight, setRoleInsight] = useState<string>('');
  const [savingCollab, setSavingCollab] = useState<boolean>(false);

  // Persist & Feedback
  const [persistToEnv, setPersistToEnv] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [testing, setTesting] = useState<boolean>(false);
  const [revoking, setRevoking] = useState<boolean>(false);

  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [saveErrorMsg, setSaveErrorMsg] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<TestLLMConnectionResponse | null>(null);

  useEffect(() => {
    loadAllSettings();
  }, []);

  const loadAllSettings = async () => {
    setLoading(true);
    try {
      const [llmData, vaultData, collabData] = await Promise.all([
        fetchLLMSettings(),
        fetchKeyVault().catch(() => ({ keys: [], total: 0, active_provider: 'gemini', active_model: 'gemini-flash-latest' })),
        fetchCollaborationSettings().catch(() => null),
      ]);

      setConfig(llmData);
      setSelectedProvider(llmData.provider);
      setSelectedModel(llmData.model);

      const activeProvider = llmData.available_providers.find((p) => p.id === llmData.provider);
      if (activeProvider && !activeProvider.models.includes(llmData.model)) {
        setIsCustomModel(true);
        setCustomModelInput(llmData.model);
      }

      setVaultKeys(vaultData.keys || []);

      if (collabData) {
        setCollabConfig(collabData);
        setCollabEnabled(collabData.enabled);
        setRoleSqlGen(collabData.roles?.sql_generator || '');
        setRoleReviewer(collabData.roles?.sql_reviewer || '');
        setRoleInsight(collabData.roles?.insight_generator || '');
      }
    } catch (err: any) {
      console.error('Failed to load settings:', err);
    } finally {
      setLoading(false);
    }
  };

  // Trigger real-time auto-detection when user types/pastes a key
  const handleKeyInputChange = async (value: string) => {
    setUniversalKeyInput(value);
    if (!value.trim()) {
      setDetectedInfo(null);
      return;
    }

    setDetecting(true);
    try {
      const result = await detectApiKeyProvider(value.trim());
      setDetectedInfo(result);
      if (result.default_model) {
        setSelectedModel(result.default_model);
      }
      if (result.default_base_url) {
        setCustomBaseUrlInput(result.default_base_url);
      }
      if (result.provider_id && result.provider_id !== 'custom') {
        setSelectedProvider(result.provider_id);
      }
    } catch (e) {
      console.error('Key detection error:', e);
    } finally {
      setDetecting(false);
    }
  };

  const handleProviderChange = (providerId: string) => {
    setSelectedProvider(providerId);
    setTestResult(null);
    setSaveSuccessMsg(null);
    setSaveErrorMsg(null);

    const providerObj = config?.available_providers.find((p) => p.id === providerId);
    if (providerObj) {
      setSelectedModel(providerObj.default_model);
      setIsCustomModel(false);
      if (providerObj.base_url) {
        setCustomBaseUrlInput(providerObj.base_url);
      }
    }
  };

  const handleModelChange = (modelName: string) => {
    if (modelName === '__custom__') {
      setIsCustomModel(true);
    } else {
      setIsCustomModel(false);
      setSelectedModel(modelName);
    }
  };

  const getEffectiveModel = (): string => {
    if (isCustomModel && customModelInput.trim()) {
      return customModelInput.trim();
    }
    return selectedModel;
  };

  // Add Key to Vault
  const handleAddToVault = async () => {
    if (!universalKeyInput.trim()) return;
    setSaving(true);
    try {
      const providerToSave = detectedInfo?.provider_id || selectedProvider;
      const modelToSave = getEffectiveModel();
      const nameToSave = keyLabelInput.trim() || `${detectedInfo?.provider_name || providerToSave.toUpperCase()} (${modelToSave})`;

      await saveKeyVaultItem({
        provider: providerToSave,
        name: nameToSave,
        api_key: universalKeyInput.trim(),
        model: modelToSave,
        base_url: customBaseUrlInput.trim() || undefined,
        is_active: false,
      });

      const vaultData = await fetchKeyVault();
      setVaultKeys(vaultData.keys || []);
      setUniversalKeyInput('');
      setKeyLabelInput('');
      setDetectedInfo(null);
      setSaveSuccessMsg(t.settingsVaultAddSuccess);
      setTimeout(() => setSaveSuccessMsg(null), 4000);
    } catch (err: any) {
      setSaveErrorMsg(err?.message || 'Failed to add key to vault');
    } finally {
      setSaving(false);
    }
  };

  // Delete Key from Vault
  const handleDeleteVaultKey = async (keyId: string) => {
    if (typeof window !== 'undefined' && !window.confirm(t.settingsApiKeyRevokeConfirm)) {
      return;
    }
    try {
      await deleteKeyVaultItem(keyId);
      const vaultData = await fetchKeyVault();
      setVaultKeys(vaultData.keys || []);
      setSaveSuccessMsg(t.settingsVaultDeleteSuccess);
      setTimeout(() => setSaveSuccessMsg(null), 4000);
    } catch (err: any) {
      setSaveErrorMsg(err?.message || 'Failed to remove key from vault');
    }
  };

  // Activate Vault Key as Primary System Provider
  const handleActivateVaultKey = async (keyId: string) => {
    try {
      const res = await activateKeyVaultItem(keyId);
      const [llmData, vaultData] = await Promise.all([fetchLLMSettings(), fetchKeyVault()]);
      setConfig(llmData);
      setSelectedProvider(llmData.provider);
      setSelectedModel(llmData.model);
      setVaultKeys(vaultData.keys || []);
      setSaveSuccessMsg(`${t.settingsVaultActivateSuccess} ${res.active_provider} (${res.active_model})`);
      setTimeout(() => setSaveSuccessMsg(null), 5000);
    } catch (err: any) {
      setSaveErrorMsg(err?.message || 'Failed to activate vault key');
    }
  };

  // Save Primary Active Configuration
  const handleSave = async () => {
    setSaving(true);
    setSaveSuccessMsg(null);
    setSaveErrorMsg(null);
    try {
      const effectiveProvider = detectedInfo?.provider_id || selectedProvider;
      const effectiveModel = getEffectiveModel();
      const payload: any = {
        provider: effectiveProvider,
        model: effectiveModel,
        persist_to_env: persistToEnv,
      };

      if (universalKeyInput.trim()) {
        if (effectiveProvider === 'gemini') {
          payload.gemini_api_key = universalKeyInput.trim();
        } else if (effectiveProvider === 'openai') {
          payload.openai_api_key = universalKeyInput.trim();
        }

        // Also register into vault
        await saveKeyVaultItem({
          provider: effectiveProvider,
          name: keyLabelInput.trim() || `${detectedInfo?.provider_name || effectiveProvider.toUpperCase()} (${effectiveModel})`,
          api_key: universalKeyInput.trim(),
          model: effectiveModel,
          base_url: customBaseUrlInput.trim() || undefined,
          is_active: true,
        }).catch(() => {});
      }

      const updated = await updateLLMSettings(payload);
      setConfig(updated);
      setUniversalKeyInput('');
      setDetectedInfo(null);
      const vaultData = await fetchKeyVault().catch(() => ({ keys: [] }));
      setVaultKeys(vaultData.keys || []);

      setSaveSuccessMsg(t.settingsSaveSuccess);
      setTimeout(() => setSaveSuccessMsg(null), 5000);
    } catch (err: any) {
      setSaveErrorMsg(err?.message || t.settingsSaveFailed);
    } finally {
      setSaving(false);
    }
  };

  // Revoke Primary Key
  const handleRevokeKey = async (provider: 'gemini' | 'openai') => {
    if (typeof window !== 'undefined' && !window.confirm(t.settingsApiKeyRevokeConfirm)) {
      return;
    }

    setRevoking(true);
    setSaveSuccessMsg(null);
    setSaveErrorMsg(null);
    setTestResult(null);

    try {
      const payload: any = {
        provider: selectedProvider,
        model: getEffectiveModel(),
        persist_to_env: persistToEnv,
      };

      if (provider === 'gemini') {
        payload.gemini_api_key = '';
      } else if (provider === 'openai') {
        payload.openai_api_key = '';
      }

      const updated = await updateLLMSettings(payload);
      setConfig(updated);
      setUniversalKeyInput('');
      setSaveSuccessMsg(t.settingsApiKeyRevokeSuccess);
      setTimeout(() => setSaveSuccessMsg(null), 5000);
    } catch (err: any) {
      setSaveErrorMsg(err?.message || 'Failed to revoke API key');
    } finally {
      setRevoking(false);
    }
  };

  // Test Connection
  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const candidateKey = universalKeyInput.trim() || undefined;
      const res = await testLLMConnection({
        provider: detectedInfo?.provider_id || selectedProvider,
        model: getEffectiveModel(),
        api_key: candidateKey,
        base_url: customBaseUrlInput.trim() || undefined,
      });
      setTestResult(res);
    } catch (err: any) {
      setTestResult({
        success: false,
        provider: selectedProvider,
        model: getEffectiveModel(),
        latency_ms: 0,
        message: err?.message || 'Network error during connection test',
      });
    } finally {
      setTesting(false);
    }
  };

  // Save Multi-Model Collaboration Settings
  const handleSaveCollaboration = async () => {
    setSavingCollab(true);
    try {
      const res = await saveCollaborationSettings({
        enabled: collabEnabled,
        roles: {
          sql_generator: roleSqlGen || null,
          sql_reviewer: roleReviewer || null,
          insight_generator: roleInsight || null,
        },
      });
      setCollabConfig({
        enabled: res.config.enabled,
        roles: res.config.roles,
        participants: res.participants,
        vault_keys: vaultKeys,
      });
      setSaveSuccessMsg(t.settingsCollabSaveSuccess);
      setTimeout(() => setSaveSuccessMsg(null), 5000);
    } catch (err: any) {
      setSaveErrorMsg(err?.message || 'Failed to save collaboration settings');
    } finally {
      setSavingCollab(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12 text-slate-400 text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2 text-sky-400" />
        Loading settings...
      </div>
    );
  }

  const currentProviderObj = config?.available_providers.find((p) => p.id === selectedProvider);

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      {/* Header Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-sky-950/40 to-slate-900 border border-slate-800 shadow-xl">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
                <Key className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-bold text-slate-100">{t.settingsTitle}</h2>
            </div>
            <p className="text-xs text-slate-400 max-w-2xl">{t.settingsSubtitle}</p>
          </div>
          <div className="flex items-center gap-2">
            {collabEnabled && (
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-950/80 border border-purple-800 text-purple-300 flex items-center gap-1.5 shadow-sm">
                <Network className="w-3.5 h-3.5" />
                {t.settingsCollabActivePill}
              </span>
            )}
            <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-sky-950 border border-sky-800/80 text-sky-300 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5" />
              {config?.provider.toUpperCase()} / {config?.model}
            </span>
          </div>
        </div>
      </div>

      {/* Security Guarantee Banner */}
      <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-800/40 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <p className="text-xs text-emerald-200/90 leading-relaxed font-sans">{t.settingsZeroLeakNote}</p>
      </div>

      {/* SECTION 1: Universal Smart API Key Input with Instant Auto-Detection */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-lg">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-sky-400" />
            <span>通用金鑰智慧自動識別 (Universal Smart Key Input)</span>
          </h3>
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-sky-950 text-sky-300 border border-sky-800/60 flex items-center gap-1">
            <Zap className="w-3 h-3 text-amber-400" />
            {t.settingsAutoDetectBadge}
          </span>
        </div>

        <p className="text-xs text-slate-400 leading-relaxed">
          貼上任何 AI 大模型金鑰（如 Google Gemini、Anthropic Claude、DeepSeek、Groq、OpenAI、OpenRouter、Mistral 或自訂端點），系統將即時自動識別服務商、推薦最佳模型與參數，並支援直接儲存為主要模型或加入多金鑰管理庫。
        </p>

        <div className="space-y-3">
          <div className="relative">
            <input
              type={showUniversalKey ? 'text' : 'password'}
              value={universalKeyInput}
              onChange={(e) => handleKeyInputChange(e.target.value)}
              placeholder="在此貼上任何 API Key (例如 AQ.Ab8RN6... 或 sk-ant-... 或 dsk-... 或 gsk_...)"
              className="w-full px-4 py-3 pr-20 bg-slate-950 border border-slate-700 rounded-xl text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-sky-400 font-mono shadow-inner"
            />
            <div className="absolute right-3 top-3 flex items-center gap-2">
              {detecting && <RefreshCw className="w-4 h-4 animate-spin text-sky-400" />}
              {universalKeyInput && (
                <button
                  type="button"
                  onClick={() => handleKeyInputChange('')}
                  className="text-slate-500 hover:text-slate-300 p-0.5"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              <button
                type="button"
                onClick={() => setShowUniversalKey(!showUniversalKey)}
                className="text-slate-500 hover:text-slate-300 p-0.5"
              >
                {showUniversalKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Auto-Detection Intelligence Panel */}
          {detectedInfo && (
            <div className="p-4 rounded-xl bg-gradient-to-r from-sky-950/40 via-indigo-950/30 to-slate-950 border border-sky-500/40 space-y-3 animate-in fade-in duration-200">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-300">{t.settingsAutoDetectDetected}</span>
                  <span className="px-2.5 py-0.5 rounded-lg text-xs font-bold bg-sky-900/80 text-sky-200 border border-sky-700 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    {detectedInfo.provider_name}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <span className="text-slate-400">{t.settingsAutoDetectConfidence}</span>
                  <span
                    className={`px-2 py-0.5 rounded font-mono font-bold ${
                      detectedInfo.confidence === 'HIGH'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-amber-950 text-amber-300 border border-amber-800'
                    }`}
                  >
                    {detectedInfo.confidence}
                  </span>
                </div>
              </div>

              <div className="text-[11px] text-slate-400 flex items-center gap-1.5 font-mono">
                <span className="text-slate-500">{t.settingsAutoDetectHint}</span>
                <span className="text-slate-300">{detectedInfo.key_format_hint}</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                    推薦模型 (Recommended Models)
                  </label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-sky-400"
                  >
                    {detectedInfo.recommended_models.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                    自訂金鑰名稱標籤 (可選)
                  </label>
                  <input
                    type="text"
                    value={keyLabelInput}
                    onChange={(e) => setKeyLabelInput(e.target.value)}
                    placeholder={`例如: ${detectedInfo.provider_name} 主力金鑰`}
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex flex-wrap items-center justify-end gap-2 pt-2 border-t border-slate-800/80">
                <button
                  type="button"
                  onClick={handleAddToVault}
                  disabled={saving}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-950 hover:bg-indigo-900 text-indigo-300 border border-indigo-700/60 text-xs font-semibold transition-all disabled:opacity-50 cursor-pointer"
                >
                  <Plus className="w-3.5 h-3.5" />
                  {t.settingsAutoDetectAddToVault}
                </button>
                <button
                  type="button"
                  onClick={handleSave}
                  disabled={saving}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold transition-all shadow-md shadow-sky-600/20 disabled:opacity-50 cursor-pointer"
                >
                  <Check className="w-3.5 h-3.5" />
                  設為主要執行模型
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* SECTION 2: Target AI Backend Providers Catalog */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-lg">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-sky-400" />
            {t.settingsProviderCardTitle}
          </h3>
          <span className="text-[11px] text-slate-500 font-mono">支援任意大模型與 OpenAI 相容端點</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {config?.available_providers.map((p) => {
            const isSelected = selectedProvider === p.id;
            return (
              <button
                key={p.id}
                type="button"
                onClick={() => handleProviderChange(p.id)}
                className={`text-left p-3.5 rounded-xl border transition-all relative ${
                  isSelected
                    ? 'bg-sky-950/40 border-sky-500/80 shadow-md shadow-sky-500/10'
                    : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 hover:bg-slate-950'
                }`}
              >
                {isSelected && (
                  <div className="absolute top-3 right-3 w-2 h-2 rounded-full bg-sky-400 shadow-sm shadow-sky-400" />
                )}
                <div className="flex items-center gap-2 mb-1">
                  {p.id === 'gemini' && <Zap className="w-4 h-4 text-amber-400" />}
                  {p.id === 'openai' && <Cpu className="w-4 h-4 text-emerald-400" />}
                  {p.id === 'deepseek' && <Bot className="w-4 h-4 text-sky-400" />}
                  {p.id === 'anthropic' && <Sparkles className="w-4 h-4 text-orange-400" />}
                  {p.id === 'groq' && <Zap className="w-4 h-4 text-red-400" />}
                  {p.id === 'mock' && <Server className="w-4 h-4 text-purple-400" />}
                  {!['gemini', 'openai', 'deepseek', 'anthropic', 'groq', 'mock'].includes(p.id) && (
                    <Cpu className="w-4 h-4 text-indigo-400" />
                  )}
                  <span className={`text-xs font-bold ${isSelected ? 'text-sky-300' : 'text-slate-200'}`}>
                    {p.name}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-2 leading-snug">{p.description}</p>
                <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
                  <span className="text-slate-500 truncate max-w-[140px]">預設: {p.default_model}</span>
                  {p.key_required ? (
                    <span className="text-amber-400/90 font-medium shrink-0">需要金鑰</span>
                  ) : (
                    <span className="text-emerald-400/90 font-medium shrink-0">離線免費</span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Custom Base URL Input if custom or third-party */}
        {(selectedProvider === 'custom' || customBaseUrlInput) && (
          <div className="pt-2">
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              {t.settingsCustomBaseUrl}
            </label>
            <input
              type="text"
              value={customBaseUrlInput}
              onChange={(e) => setCustomBaseUrlInput(e.target.value)}
              placeholder={t.settingsCustomBaseUrlPlaceholder}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-sky-500"
            />
          </div>
        )}
      </div>

      {/* SECTION 3: Multi-API Vault (多金鑰管理庫) */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Layers className="w-4 h-4 text-sky-400" />
              {t.settingsVaultTitle}
            </h3>
            <p className="text-xs text-slate-400">{t.settingsVaultSubtitle}</p>
          </div>
          <span className="text-xs font-mono text-slate-400">
            庫存金鑰：<strong className="text-sky-300">{vaultKeys.length}</strong>
          </span>
        </div>

        {vaultKeys.length === 0 ? (
          <div className="p-6 rounded-xl bg-slate-950 border border-dashed border-slate-800 text-center text-xs text-slate-500 space-y-2">
            <Key className="w-6 h-6 mx-auto text-slate-600" />
            <p>{t.settingsVaultEmpty}</p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {vaultKeys.map((item) => (
              <div
                key={item.id}
                className={`p-3.5 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition-all ${
                  item.is_active
                    ? 'bg-sky-950/30 border-sky-500/60 shadow-sm shadow-sky-500/10'
                    : 'bg-slate-950 border-slate-800/80 hover:border-slate-700'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-200">{item.name}</span>
                    {item.is_active && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-800/80 flex items-center gap-1">
                        <Check className="w-2.5 h-2.5" />
                        {t.settingsVaultActiveBadge}
                      </span>
                    )}
                    <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-mono bg-slate-800 text-slate-300">
                      {item.provider}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-[11px] font-mono text-slate-400">
                    <span>模型: <strong className="text-slate-300">{item.model}</strong></span>
                    <span>憑證: <strong className="text-slate-300">{item.api_key_masked || '(空白)'}</strong></span>
                    {item.base_url && <span>URL: {item.base_url}</span>}
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  {!item.is_active && (
                    <button
                      type="button"
                      onClick={() => handleActivateVaultKey(item.id)}
                      className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
                    >
                      {t.settingsVaultActivateBtn}
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => handleDeleteVaultKey(item.id)}
                    className="p-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/50 transition-colors"
                    title={t.settingsVaultDeleteBtn}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* SECTION 4: Multi-Model Collaborative Analytics (多大模型互相合作分析) */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-lg">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Network className="w-4 h-4 text-purple-400" />
              {t.settingsCollabTitle}
            </h3>
            <p className="text-xs text-slate-400 max-w-2xl">{t.settingsCollabSubtitle}</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer shrink-0">
            <input
              type="checkbox"
              checked={collabEnabled}
              onChange={(e) => setCollabEnabled(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
          </label>
        </div>

        {collabEnabled && (
          <div className="space-y-4 pt-2 animate-in fade-in duration-200">
            {/* Architecture Pipeline Visualizer */}
            <div className="p-3.5 rounded-xl bg-slate-950 border border-purple-900/40 flex flex-col md:flex-row items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2 text-sky-300 bg-sky-950/40 px-3 py-2 rounded-lg border border-sky-800/50">
                <Bot className="w-4 h-4 text-sky-400 shrink-0" />
                <div>
                  <div className="font-bold text-[11px]">角色 1: SQL 生成</div>
                  <div className="text-[10px] text-slate-400">Text-to-SQL 專家</div>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 hidden md:block" />
              <div className="flex items-center gap-2 text-amber-300 bg-amber-950/40 px-3 py-2 rounded-lg border border-amber-800/50">
                <ShieldCheck className="w-4 h-4 text-amber-400 shrink-0" />
                <div>
                  <div className="font-bold text-[11px]">角色 2: SQL 交叉審查</div>
                  <div className="text-[10px] text-slate-400">AST/防笛卡兒積校驗</div>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 hidden md:block" />
              <div className="flex items-center gap-2 text-emerald-300 bg-emerald-950/40 px-3 py-2 rounded-lg border border-emerald-800/50">
                <Server className="w-4 h-4 text-emerald-400 shrink-0" />
                <div>
                  <div className="font-bold text-[11px]">DuckDB 引擎</div>
                  <div className="text-[10px] text-slate-400">唯讀真實資料查詢</div>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-600 hidden md:block" />
              <div className="flex items-center gap-2 text-purple-300 bg-purple-950/40 px-3 py-2 rounded-lg border border-purple-800/50">
                <Sparkles className="w-4 h-4 text-purple-400 shrink-0" />
                <div>
                  <div className="font-bold text-[11px]">角色 3: 商業洞察</div>
                  <div className="text-[10px] text-slate-400">繁體中文高階顧問</div>
                </div>
              </div>
            </div>

            {/* Role Assignment Selectors */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  {t.settingsCollabRoleSqlGen}
                </label>
                <select
                  value={roleSqlGen}
                  onChange={(e) => setRoleSqlGen(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="">預設系統主要模型 ({selectedProvider})</option>
                  {vaultKeys.map((vk) => (
                    <option key={vk.id} value={vk.id}>
                      {vk.name} ({vk.provider})
                    </option>
                  ))}
                  {config?.available_providers.map((p) => (
                    <option key={`p_${p.id}`} value={p.id}>
                      {p.name} ({p.default_model})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  {t.settingsCollabRoleReview}
                </label>
                <select
                  value={roleReviewer}
                  onChange={(e) => setRoleReviewer(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="">預設系統主要模型 ({selectedProvider})</option>
                  {vaultKeys.map((vk) => (
                    <option key={vk.id} value={vk.id}>
                      {vk.name} ({vk.provider})
                    </option>
                  ))}
                  {config?.available_providers.map((p) => (
                    <option key={`p_${p.id}`} value={p.id}>
                      {p.name} ({p.default_model})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  {t.settingsCollabRoleInsight}
                </label>
                <select
                  value={roleInsight}
                  onChange={(e) => setRoleInsight(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="">預設系統主要模型 ({selectedProvider})</option>
                  {vaultKeys.map((vk) => (
                    <option key={vk.id} value={vk.id}>
                      {vk.name} ({vk.provider})
                    </option>
                  ))}
                  {config?.available_providers.map((p) => (
                    <option key={`p_${p.id}`} value={p.id}>
                      {p.name} ({p.default_model})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <button
                type="button"
                onClick={handleSaveCollaboration}
                disabled={savingCollab}
                className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition-all shadow-md shadow-purple-600/20 disabled:opacity-50 cursor-pointer"
              >
                {savingCollab ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                {t.settingsCollabSaveBtn}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* SECTION 5: Connection Diagnostics & Feedback */}
      {testResult && (
        <div
          className={`p-4 rounded-xl border transition-all ${
            testResult.success
              ? 'bg-emerald-950/30 border-emerald-800/60 text-emerald-200'
              : 'bg-rose-950/30 border-rose-800/60 text-rose-200'
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              {testResult.success ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-rose-400" />
              )}
              <span className="text-xs font-bold">
                {testResult.success ? t.settingsTestSuccess : t.settingsTestFailed}
              </span>
            </div>
            <span className="text-xs font-mono text-slate-400">
              {t.settingsLatencyLabel} <strong className="text-slate-200">{testResult.latency_ms} ms</strong>
            </span>
          </div>
          <p className="text-xs opacity-90 mb-2">{testResult.message}</p>
          {testResult.sample_output && (
            <div className="mt-2 p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-slate-300">
              <span className="text-slate-500 block mb-1">{t.settingsSampleOutputLabel}</span>
              {testResult.sample_output}
            </div>
          )}
        </div>
      )}

      {saveSuccessMsg && (
        <div className="p-3 rounded-lg bg-emerald-950/40 border border-emerald-800/60 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          {saveSuccessMsg}
        </div>
      )}
      {saveErrorMsg && (
        <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          {saveErrorMsg}
        </div>
      )}

      {/* Footer Actions */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
        <button
          type="button"
          onClick={handleTestConnection}
          disabled={testing}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors disabled:opacity-50 cursor-pointer"
        >
          {testing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          {testing ? t.settingsTestingBtn : t.settingsTestBtn}
        </button>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
            <input
              type="checkbox"
              checked={persistToEnv}
              onChange={(e) => setPersistToEnv(e.target.checked)}
              className="rounded bg-slate-950 border-slate-700 text-sky-500 focus:ring-0"
            />
            <span className="hidden sm:inline">寫入 .env</span>
          </label>
          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold shadow-lg shadow-sky-600/20 transition-all disabled:opacity-50 cursor-pointer"
          >
            {saving ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
            {saving ? t.settingsSavingBtn : t.settingsSaveBtn}
          </button>
        </div>
      </div>
    </div>
  );
}
