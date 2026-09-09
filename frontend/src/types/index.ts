export interface ExecutionStep {
  step: string;
  status: string;
  reason?: string;
  provider?: string;
  model?: string;
  model_name?: string;
  reviewer?: string;
  rls_predicates?: string[];
}

export interface GroundedClaim {
  claim_id: string;
  text: string;
  metric?: string;
  value?: any;
  status: 'SUPPORTED' | 'PARTIALLY_SUPPORTED' | 'UNSUPPORTED' | 'CONTRADICTED';
  evidence: string;
  confidence_score: number;
}

export interface QueryResponse {
  query_id: string;
  status: 'SUCCEEDED' | 'BLOCKED' | 'FAILED' | 'CLARIFICATION_REQUIRED';
  question: string;
  generated_sql: string;
  rewritten_sql: string;
  execution_steps: ExecutionStep[];
  data_quality: {
    quality_score: number;
    null_ratio: number;
    duplicate_count: number;
    freshness_status: string;
    warnings: string[];
  };
  analytical_results: {
    summary: string;
    grounded_claims: GroundedClaim[];
    columns: string[];
    rows: any[][];
    dataset_id?: string;
    domain_name?: string;
    collaboration?: {
      enabled: boolean;
      participants: CollaborationParticipant[];
    };
  };
  visualization?: {
    image_b64?: string;
    chart_type?: string;
  };
  claims: GroundedClaim[];
  grounding_status: string;
  collaboration_info?: {
    enabled: boolean;
    participants: CollaborationParticipant[];
  };
}

export interface AuditLogItem {
  event_id: string;
  timestamp: string;
  tenant_id: string;
  user_id: string;
  action: string;
  resource: string;
  result: 'ALLOWED' | 'BLOCKED' | 'NEEDS_CLARIFICATION';
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  reason: string;
}

export interface SchemaTable {
  table_name: string;
  description: string;
  column_count: number;
}

export interface SemanticMetric {
  name: string;
  aliases?: string[];
  description: string;
  domain?: string;
  dataset_id?: string;
  formula?: string;
  sql_expression?: string;
  base_table?: string;
  sensitivity?: string;
  version?: string;
  governance_rule?: string;
}

export interface DemoDataset {
  dataset_id: string;
  dataset_name: string;
  domain: string;
  publisher: string;
  source_url: string;
  terms_url?: string;
  license: string;
  version: string;
  retrieved_at: string;
  checksum: string;
  source_format: string;
  storage_format: string;
  row_count: number;
  table_count: number;
  schema_version: string;
  data_classification: 'PUBLIC' | 'INTERNAL' | 'CONFIDENTIAL' | 'RESTRICTED';
  refresh_frequency: string;
  date_range: string;
  geographic_scope: string;
  quality_score: number;
  documentation_url: string;
  citation: string;
  icon: string;
  tables: string[];
  sample_queries: string[];
  safety_disclaimer?: string;
  governance_rule?: string;
  disclaimer?: string;
  // Backward compatibility fields
  id?: string;
  name_zh?: string;
  name_en?: string;
  category_zh?: string;
  category_en?: string;
  description_zh?: string;
  description_en?: string;
}

export interface DatasetDetail {
  metadata: DemoDataset;
  columns: string[];
  rows: Record<string, any>[];
  total_rows: number;
  column_stats?: Array<{
    column_name: string;
    type: string;
    sample_values?: string[];
  }>;
  tables?: string[];
}

export interface SQLInspectRequest {
  raw_sql: string;
  simulated_tenant_id?: string;
  simulated_role?: string;
  simulated_regions?: string[];
  simulated_departments?: string[];
  compliance_mode?: string;
}

export interface InjectedPredicate {
  type: string;
  table: string;
  predicate: string;
  rationale: string;
}

export interface MaskedColumn {
  column: string;
  sensitivity: string;
  data_type: string;
  mask_applied: string;
  target_alias: string;
}

export interface ComplianceItem {
  standard: string;
  rule: string;
  passed: boolean;
  details: string;
}

export interface PerformanceCostEstimate {
  estimated_rows: number;
  cost_rating: 'OPTIMAL' | 'MODERATE_WARNING' | 'CRITICAL_OVERHEAD';
  is_cost_exceeded: boolean;
  has_cartesian_product: boolean;
  table_count: number;
  join_count: number;
  has_where_clause: boolean;
  warnings: string[];
  explain_plan_raw: string;
  plan_nodes: Array<{
    operation: string;
    type: string;
  }>;
}

export interface SQLInspectResponse {
  raw_sql: string;
  rewritten_sql: string;
  is_safe: boolean;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  violations: string[];
  ast_analysis: {
    root?: string;
    projections?: string[];
    from_tables?: string[];
    where_clause?: string | null;
    joins?: string[];
    group_by?: string | null;
    limit?: string | null;
  };
  injected_predicates: InjectedPredicate[];
  masked_columns: MaskedColumn[];
  cost_estimate: PerformanceCostEstimate;
  compliance_checklist: ComplianceItem[];
  mutation_explanations: string[];
}

export interface SecurityPreset {
  id: string;
  name: string;
  category: string;
  sql: string;
  description: string;
}

export interface ProviderOption {
  id: string;
  name: string;
  description: string;
  default_model: string;
  models: string[];
  base_url?: string | null;
  key_required: boolean;
  key_field?: string | null;
}

export interface LLMConfigResponse {
  provider: string;
  model: string;
  gemini_api_key_configured: boolean;
  gemini_api_key_masked: string | null;
  openai_api_key_configured: boolean;
  openai_api_key_masked: string | null;
  available_providers: ProviderOption[];
}

export interface UpdateLLMConfigRequest {
  provider?: string;
  model?: string;
  gemini_api_key?: string;
  openai_api_key?: string;
  persist_to_env?: boolean;
}

export interface TestLLMConnectionRequest {
  provider: string;
  model?: string;
  api_key?: string;
  base_url?: string;
}

export interface TestLLMConnectionResponse {
  success: boolean;
  provider: string;
  model: string;
  latency_ms: number;
  message: string;
  sample_output?: string | null;
}

export interface DetectKeyResponse {
  provider_id: string;
  provider_name: string;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  recommended_models: string[];
  default_model: string;
  default_base_url?: string | null;
  key_format_hint: string;
  description: string;
}

export interface VaultKeyItem {
  id: string;
  provider: string;
  name: string;
  api_key_masked: string;
  model: string;
  base_url?: string | null;
  is_active: boolean;
  created_at: number;
}

export interface AddVaultKeyRequest {
  id?: string;
  provider: string;
  name?: string;
  api_key: string;
  model: string;
  base_url?: string | null;
  is_active?: boolean;
}

export interface CollaborationParticipant {
  role: string;
  provider: string;
  model: string;
  name: string;
}

export interface CollaborationSettings {
  enabled: boolean;
  roles: {
    sql_generator?: string | null;
    sql_reviewer?: string | null;
    insight_generator?: string | null;
  };
  participants: CollaborationParticipant[];
  vault_keys: VaultKeyItem[];
}



