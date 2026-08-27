# Backup, Restore & Disaster Recovery Procedures

## Backup Strategy

### Application Database
The application database stores user accounts, organizations, workspaces, schema registry metadata, audit logs, and query history.

- **Backup Command**:
  ```bash
  pg_dump -U app_user -d app_db -F c -b -v -f storage/backups/app_db_$(date +%Y%m%d_%H%M%S).dump
  ```
- **Restore Command**:
  ```bash
  pg_restore -U app_user -d app_db -v storage/backups/app_db_latest.dump
  ```

### Local Demo DuckDB Backup
- **Backup Script**: `cp backend/analytics_demo.duckdb storage/backups/analytics_demo.duckdb.bak`
- **Restore Script**: `cp storage/backups/analytics_demo.duckdb.bak backend/analytics_demo.duckdb`

## Disaster Recovery SLAs
- **RPO (Recovery Point Objective)**: 1 Hour
- **RTO (Recovery Time Objective)**: 15 Minutes
