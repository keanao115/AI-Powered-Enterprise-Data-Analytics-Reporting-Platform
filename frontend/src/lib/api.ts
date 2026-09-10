import { QueryResponse, AuditLogItem, SchemaTable, SemanticMetric, CatalogTable } from '../types';


const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

let inMemoryToken: string | null = null;

export function getAuthToken(): string | null {
  if (inMemoryToken) return inMemoryToken;
  if (typeof window !== 'undefined') {
    inMemoryToken = localStorage.getItem('access_token');
  }
  return inMemoryToken;
}

export function setAuthToken(token: string | null): void {
  inMemoryToken = token;
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }
}

export function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function loginUser(email: string, password: string = 'password123'): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail || '登入失敗');
  }
  const data = await res.json();
  if (data.access_token) {
    setAuthToken(data.access_token);
  }
  return data;
}

export async function fetchCurrentUser(): Promise<any> {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/v1/auth/me`, { headers });
  if (!res.ok) return null;
  return res.json();
}

export async function submitQuery(question: string, datasetId?: string): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE}/api/v1/queries`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ question, dataset_id: datasetId || undefined }),
  });
  if (!res.ok) {
    const errData = await res.json();
    throw new Error(errData?.detail?.message || errData?.error?.message || 'Query execution failed');
  }
  return res.json();
}

export async function fetchAuditLogs(): Promise<AuditLogItem[]> {
  const res = await fetch(`${API_BASE}/api/v1/audit`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) return [];
  return res.json();
}

export async function fetchSchemas(): Promise<SchemaTable[]> {
  const res = await fetch(`${API_BASE}/api/v1/schemas`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) return [];
  return res.json();
}

export async function fetchCatalog(): Promise<CatalogTable[]> {
  const res = await fetch(`${API_BASE}/api/v1/schemas/catalog`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) return [];
  return res.json();
}


export async function fetchMetrics(): Promise<SemanticMetric[]> {
  const res = await fetch(`${API_BASE}/api/v1/metrics`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) return [];
  return res.json();
}

export async function triggerReportDownload(queryId: string, format: string): Promise<void> {
  const token = getAuthToken();
  const url = `${API_BASE}/api/v1/reports/${queryId}/download?format=${format}${token ? `&token=${token}` : ''}`;
  window.open(url, '_blank');
}

export async function runEvaluation(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/evaluation/run`, { method: 'POST' });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData?.detail?.message || errData?.detail || errData?.error?.message || 'Evaluation benchmark failed');
  }
  return res.json();
}

export async function fetchDatasets(): Promise<import('../types').DemoDataset[]> {
  const res = await fetch(`${API_BASE}/api/v1/datasets`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchDatasetDetails(
  datasetId: string,
  search?: string,
  limit: number = 50,
  offset: number = 0
): Promise<import('../types').DatasetDetail | null> {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  params.append('limit', String(limit));
  params.append('offset', String(offset));

  const res = await fetch(`${API_BASE}/api/v1/datasets/${datasetId}?${params.toString()}`);
  if (!res.ok) return null;
  return res.json();
}

export function getDatasetDownloadUrl(datasetId: string): string {
  return `${API_BASE}/api/v1/datasets/${datasetId}/download`;
}

export async function inspectSQL(req: import('../types').SQLInspectRequest): Promise<import('../types').SQLInspectResponse> {
  const res = await fetch(`${API_BASE}/api/v1/security/inspect-sql`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData?.detail?.message || errData?.detail || errData?.error?.message || 'SQL inspection failed');
  }
  return res.json();
}

export async function fetchSecurityPresets(): Promise<import('../types').SecurityPreset[]> {
  const res = await fetch(`${API_BASE}/api/v1/security/presets`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchLLMSettings(): Promise<import('../types').LLMConfigResponse> {
  const res = await fetch(`${API_BASE}/api/v1/settings/llm`);
  if (!res.ok) {
    throw new Error('Failed to fetch LLM settings');
  }
  return res.json();
}

export async function updateLLMSettings(req: import('../types').UpdateLLMConfigRequest): Promise<import('../types').LLMConfigResponse> {
  const res = await fetch(`${API_BASE}/api/v1/settings/llm`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData?.detail?.message || errData?.detail || 'Failed to update LLM configuration');
  }
  return res.json();
}

export async function testLLMConnection(req: import('../types').TestLLMConnectionRequest): Promise<import('../types').TestLLMConnectionResponse> {
  const res = await fetch(`${API_BASE}/api/v1/settings/test-llm`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData?.detail?.message || errData?.detail || 'Failed to execute connection test');
  }
  return res.json();
}

export async function detectApiKeyProvider(key: string): Promise<import('../types').DetectKeyResponse> {
  const res = await fetch(`${API_BASE}/api/v1/settings/detect-key`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData?.detail?.message || errData?.detail || 'Failed to analyze API key');
  }
  return res.json();
}

export async function fetchKeyVault(): Promise<{
  keys: import('../types').VaultKeyItem[];
  total: number;
  active_provider: string;
  active_model: string;
}> {
  const res = await fetch(`${API_BASE}/api/v1/settings/vault`);
  if (!res.ok) {
    throw new Error('Failed to fetch key vault');
  }
  return res.json();
}

export async function saveKeyVaultItem(item: import('../types').AddVaultKeyRequest): Promise<{
  success: boolean;
  message: string;
  key: import('../types').VaultKeyItem;
}> {
  const res = await fetch(`${API_BASE}/api/v1/settings/vault`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData?.detail?.message || errData?.detail || 'Failed to save key in vault');
  }
  return res.json();
}

export async function deleteKeyVaultItem(providerId: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/api/v1/settings/vault/${encodeURIComponent(providerId)}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData?.detail?.message || errData?.detail || 'Failed to remove key from vault');
  }
  return res.json();
}

export async function activateKeyVaultItem(providerId: string): Promise<{
  success: boolean;
  message: string;
  active_provider: string;
  active_model: string;
}> {
  const res = await fetch(`${API_BASE}/api/v1/settings/vault/${encodeURIComponent(providerId)}/activate`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData?.detail?.message || errData?.detail || 'Failed to activate key');
  }
  return res.json();
}

export async function fetchCollaborationSettings(): Promise<import('../types').CollaborationSettings> {
  const res = await fetch(`${API_BASE}/api/v1/settings/collaboration`);
  if (!res.ok) {
    throw new Error('Failed to fetch collaboration settings');
  }
  return res.json();
}

export async function saveCollaborationSettings(req: {
  enabled: boolean;
  roles?: {
    sql_generator?: string | null;
    sql_reviewer?: string | null;
    insight_generator?: string | null;
  };
}): Promise<{
  success: boolean;
  message: string;
  config: any;
  participants: import('../types').CollaborationParticipant[];
}> {
  const res = await fetch(`${API_BASE}/api/v1/settings/collaboration`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData?.detail?.message || errData?.detail || 'Failed to update collaboration settings');
  }
  return res.json();
}




