'use client';

import React from 'react';
import { Globe, Check } from 'lucide-react';
import { useTranslation, Language } from '../locales/LanguageContext';

export default function LanguageSelector() {
  const { language, setLanguage, t } = useTranslation();

  return (
    <div className="flex items-center gap-2 bg-sky-950/60 border border-sky-500/40 hover:border-sky-400 rounded-lg px-3 py-1.5 text-xs shadow-md shadow-sky-500/10 transition-colors">
      <Globe className="w-4 h-4 text-sky-400 shrink-0 animate-pulse" />
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value as Language)}
        className="bg-transparent text-sky-200 text-xs font-semibold focus:outline-none cursor-pointer pr-1"
      >
        <option value="zh-TW" className="bg-slate-900 text-slate-100 font-sans">
          🌐 繁體中文 (zh-TW)
        </option>
        <option value="en" className="bg-slate-900 text-slate-100 font-sans">
          🌐 English (en)
        </option>
      </select>
    </div>
  );
}
