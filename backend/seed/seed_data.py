import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import duckdb
from app.ingestion.run_all_ingestions import run_full_enterprise_ingestion_pipeline


def seed_synthetic_analytics_database(db_path: str = "analytics_demo.duckdb"):
    conn = duckdb.connect(db_path)

    # 1. Regions
    conn.execute("""
        CREATE TABLE IF NOT EXISTS regions (
            id VARCHAR PRIMARY KEY,
            region_name VARCHAR NOT NULL
        );
        INSERT OR REPLACE INTO regions VALUES 
            ('reg-1', 'US'),
            ('reg-2', 'EU'),
            ('reg-3', 'APAC');
    """)

    # 2. Customers
    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            phone VARCHAR,
            ssn VARCHAR,
            region VARCHAR NOT NULL
        );
        INSERT OR REPLACE INTO customers VALUES 
            ('cust-1', 'tenant-acme', 'Acme Corp Admin', 'admin@acme.com', '+1-555-0192', '987-65-4321', 'US'),
            ('cust-2', 'tenant-acme', 'Globex Sales', 'sales@globex.com', '+44-20-7946', '123-45-6789', 'EU'),
            ('cust-3', 'tenant-acme', 'Stark Logistics', 'tony@stark.com', '+1-555-0100', '555-44-3322', 'US'),
            ('cust-4', 'tenant-acme', 'Cyberdyne AI', 'sarah@cyberdyne.com', '+81-3-1234', '999-88-7766', 'APAC');
    """)

    # 3. Products
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id VARCHAR PRIMARY KEY,
            product_name VARCHAR NOT NULL,
            category VARCHAR NOT NULL,
            price DECIMAL(10,2) NOT NULL
        );
        INSERT OR REPLACE INTO products VALUES 
            ('prod-101', 'Enterprise Data Engine', 'Software', 4999.00),
            ('prod-102', 'AI Analytics Pro', 'Software', 2999.00),
            ('prod-103', 'Cloud Connector', 'Hardware', 1499.00),
            ('prod-104', 'Developer License', 'Software', 499.00);
    """)

    # 4. Orders
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL,
            customer_id VARCHAR NOT NULL,
            region_id VARCHAR NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            status VARCHAR NOT NULL,
            order_date DATE NOT NULL
        );
        INSERT OR REPLACE INTO orders VALUES 
            ('ord-1001', 'tenant-acme', 'cust-1', 'reg-1', 1250000.00, 'completed', '2026-08-01'),
            ('ord-1002', 'tenant-acme', 'cust-2', 'reg-2', 850000.00, 'completed', '2026-08-05'),
            ('ord-1003', 'tenant-acme', 'cust-3', 'reg-1', 310000.00, 'completed', '2026-08-08'),
            ('ord-1004', 'tenant-acme', 'cust-4', 'reg-3', 25000.00, 'completed', '2026-08-10'),
            ('ord-1005', 'tenant-acme', 'cust-1', 'reg-1', 1100000.00, 'completed', '2026-07-15'),
            ('ord-1006', 'tenant-acme', 'cust-2', 'reg-2', 770000.00, 'completed', '2026-07-20');
    """)

    # 5. Order Items
    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id VARCHAR PRIMARY KEY,
            order_id VARCHAR NOT NULL,
            product_id VARCHAR NOT NULL,
            quantity INT NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL
        );
        INSERT OR REPLACE INTO order_items VALUES 
            ('item-1', 'ord-1001', 'prod-101', 200, 4999.00),
            ('item-2', 'ord-1002', 'prod-102', 250, 2999.00),
            ('item-3', 'ord-1003', 'prod-103', 150, 1499.00),
            ('item-4', 'ord-1004', 'prod-104', 50, 499.00);
    """)

    # 6. Returns
    conn.execute("""
        CREATE TABLE IF NOT EXISTS returns (
            id VARCHAR PRIMARY KEY,
            order_id VARCHAR NOT NULL,
            reason VARCHAR NOT NULL,
            return_date DATE NOT NULL
        );
        INSERT OR REPLACE INTO returns VALUES 
            ('ret-1', 'ord-1004', 'Defective License Key', '2026-08-11');
    """)

    # 7. Demo CSV tables (compatibility)
    demo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../demo_data"))
    demo_tables = [
        ("sales_orders", "01_enterprise_sales_orders.csv"),
        ("customer_churn", "02_customer_churn_retention.csv"),
        ("inventory_supply_chain", "03_inventory_supply_chain.csv"),
        ("financial_metrics", "04_financial_quarterly_metrics.csv"),
        ("employee_performance", "05_hr_employee_performance.csv"),
        ("marketing_campaigns", "06_marketing_campaign_attribution.csv"),
    ]

    for table_name, csv_file in demo_tables:
        csv_path = os.path.join(demo_dir, csv_file).replace("\\", "/")
        if os.path.exists(csv_path):
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{csv_path}');")

    conn.close()

    # 8. Ingest the 6 public real-world datasets into DuckDB & 3-tier raw/clean/curated
    run_full_enterprise_ingestion_pipeline()
    print(f"Successfully seeded enterprise analytics DuckDB dataset at '{db_path}'.")


if __name__ == "__main__":
    seed_synthetic_analytics_database()
