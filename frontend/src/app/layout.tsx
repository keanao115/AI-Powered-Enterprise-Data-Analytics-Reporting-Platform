import './globals.css';
import React from 'react';
import { LanguageProvider } from '../locales/LanguageContext';

export const metadata = {
  title: 'AI Enterprise Data Analytics Platform | 企業級 AI 數據分析平台',
  description: 'Production-Grade AI-Powered Enterprise Data Analytics & Reporting Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-TW" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen antialiased">
        <LanguageProvider>
          {children}
        </LanguageProvider>
      </body>
    </html>
  );
}
