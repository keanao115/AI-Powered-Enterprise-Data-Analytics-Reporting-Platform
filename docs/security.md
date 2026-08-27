# Security & Governance Architecture

## Security Principles

1. **The LLM is an Untrusted Planner**: The LLM NEVER determines access authorization, SQL validity, or execution permissions.
2. **Deterministic AST Policy Enforcement**: Every candidate SQL query is parsed into a syntax tree using `sqlglot`. Non-analytical statements (DDL/DML) are blocked fail-closed.
3. **Mandatory Row-Level Security (RLS)**: Queries are automatically rewritten to inject tenant and region isolation predicates.
4. **Data Minimization & PII Firewall**: PII attributes (SSN, Credit Cards, Email) are scrubbed before reaching frontend components or external AI providers.
5. **Double-Sandboxed Python Execution**: Code execution is protected by static AST inspection and process/container resource limits (memory, CPU, timeout, network disabled).
