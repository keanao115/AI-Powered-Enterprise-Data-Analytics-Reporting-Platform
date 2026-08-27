import os
import random
import csv
from datetime import datetime, timedelta

# Set fixed random seed for reproducible high quality
random.seed(42)

DEMO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "demo_data"))
os.makedirs(DEMO_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. ENTERPRISE SALES ORDERS (~2,500 Rows)
# -------------------------------------------------------------
def generate_sales_orders(count=2500):
    filepath = os.path.join(DEMO_DIR, "01_enterprise_sales_orders.csv")
    print(f"Generating {count} enterprise sales orders -> {filepath}")
    
    companies = [
        ("Cyberdyne Systems Corp", "Enterprise Strategic", "Technology & AI"),
        ("Globex Corporation", "Enterprise Strategic", "Conglomerate"),
        ("Initech Cloud Solutions", "Mid-Market", "Software"),
        ("Stark Aerospace & Defense", "Enterprise Strategic", "Aerospace"),
        ("Wayne Enterprises Holdings", "Enterprise Strategic", "Finance & Industrial"),
        ("Soylent BioTech Global", "Mid-Market", "BioTech"),
        ("Tyrell Synthetic Dynamics", "Enterprise Strategic", "Robotics"),
        ("Umbrella Life Sciences", "Enterprise Strategic", "Pharma"),
        ("Wonka Global Logistics", "Mid-Market", "Supply Chain"),
        ("Hooli Enterprise Cloud", "Enterprise Strategic", "Cloud Services"),
        ("Pied Piper Compression", "Mid-Market", "DeepTech"),
        ("Massive Dynamic AI", "Enterprise Strategic", "Artificial Intelligence"),
        ("Oceanic Airlines Group", "Enterprise Strategic", "Aviation"),
        ("Nakatomi Trading Corp", "Mid-Market", "Trading & Real Estate"),
        ("Acme Aerospace Systems", "Mid-Market", "Manufacturing"),
        ("Dunder Mifflin Paper & Tech", "SMB Growth", "Retail & Supplies"),
        ("Sterling Cooper Advertising", "Mid-Market", "Marketing & Media"),
        ("Virtucon Industries", "Enterprise Strategic", "Industrial Equipment"),
        ("Buy N Large Retail Mega", "Enterprise Strategic", "E-Commerce"),
        ("Oscorp Pharmaceutical", "Enterprise Strategic", "Life Sciences"),
        ("Weyland-Yutani Deep Space", "Enterprise Strategic", "Energy & Mining"),
        ("Gekko Financial Partners", "Enterprise Strategic", "FinTech & Hedge Fund"),
        ("Delos Experience Living", "Enterprise Strategic", "Hospitality"),
        ("Aperture Quantum Lab", "Mid-Market", "Research & Quantum"),
        ("Black Mesa Research", "Enterprise Strategic", "Scientific R&D"),
        ("Shinra Electric Power", "Enterprise Strategic", "Energy & Utilities"),
        ("Vault-Tec Security Hub", "Enterprise Strategic", "Cybersecurity"),
        ("LexCorp Advanced Metals", "Enterprise Strategic", "Materials"),
        ("Omni Consumer Products", "Enterprise Strategic", "Consumer Tech"),
        ("Sartre Software SAS", "SMB Growth", "Dev Tools"),
        ("Athena Health Systems", "Mid-Market", "Healthcare"),
        ("Zeus Renewable Power", "Mid-Market", "Clean Energy"),
        ("Apex FinTech Global", "Enterprise Strategic", "Banking"),
        ("Quantum Peak Labs", "SMB Growth", "Semiconductor"),
        ("Hyperion Data Mesh", "Mid-Market", "Data Infrastructure")
    ]
    
    regions = [
        ("US-East", "United States"), ("US-West", "United States"), ("US-Central", "United States"),
        ("EU-West", "United Kingdom"), ("EU-Central", "Germany"), ("EU-West", "France"),
        ("EU-North", "Netherlands"), ("EU-Central", "Switzerland"),
        ("APAC-East", "Japan"), ("APAC-East", "Taiwan"), ("APAC-South", "Singapore"),
        ("APAC-ANZ", "Australia"), ("APAC-East", "South Korea"),
        ("LATAM", "Brazil"), ("MEA", "United Arab Emirates")
    ]
    
    channels = ["Direct Field Sales", "Strategic Reseller Partner", "Online B2B Portal", "Global Alliance Partner"]
    
    products = [
        ("Enterprise Data Lakehouse Engine", "Cloud Infrastructure", "SKU-INFRA-801", 12500.00, 0.78),
        ("Neural Fabric GenAI Platform", "AI Platform", "SKU-AI-9001", 24800.00, 0.84),
        ("Zero-Trust Security Perimeter", "Cybersecurity Suite", "SKU-SEC-402", 8900.00, 0.75),
        ("QuantumDB Distributed Cluster", "Database Infrastructure", "SKU-DB-880", 16500.00, 0.81),
        ("Global ERP Enterprise Suite", "Enterprise ERP", "SKU-ERP-101", 35000.00, 0.68),
        ("DevSecOps Automation Mesh", "Developer Tools", "SKU-DEV-701", 4500.00, 0.86),
        ("Edge IoT Fleet Orchestrator", "IoT & Edge Computing", "SKU-IOT-330", 6800.00, 0.72),
        ("Realtime Anomaly Detection", "AI Platform", "SKU-AI-9050", 11200.00, 0.82),
        ("High-Speed API Gateway Gateway", "Cloud Infrastructure", "SKU-INFRA-805", 5400.00, 0.79),
        ("Compliance & Audit Vault", "Cybersecurity Suite", "SKU-SEC-410", 7200.00, 0.74)
    ]
    
    sales_reps = [
        "Alex Mercer", "Sarah Chen", "Marcus Vance", "Elena Rostova", "Kenji Sato",
        "David Lin", "Jessica Taylor", "Chloe Dubois", "Michael Chang", "Rachel Green",
        "Vikram Patel", "Astrid Lindgren", "Gabriel Santos", "Hannah Schmidt", "Brian O'Connor"
    ]
    
    payment_terms_list = ["Net 30", "Net 60", "Net 90", "Annual Pre-Paid", "Quarterly Net 30"]
    order_statuses = ["Completed", "In Fulfillment", "Pending Verification", "Completed"]
    
    start_date = datetime(2024, 1, 1)
    
    headers = [
        "order_id", "order_date", "fiscal_year", "fiscal_quarter", "customer_id",
        "customer_name", "account_tier", "industry", "region", "country",
        "sales_channel", "product_category", "product_sku", "product_name",
        "quantity", "unit_price", "discount_rate_pct", "total_amount",
        "cogs_amount", "gross_margin_pct", "payment_terms", "order_status", "sales_rep"
    ]
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i in range(1, count + 1):
            order_id = f"ORD-{2024 + (i // 1000)}-{i:05d}"
            # Distribution of dates across 2024 to 2026-08
            days_offset = random.randint(0, 950)
            order_dt = start_date + timedelta(days=days_offset)
            order_date_str = order_dt.strftime("%Y-%m-%d")
            f_year = order_dt.year
            f_qtr = f"{f_year}-Q{(order_dt.month - 1) // 3 + 1}"
            
            cust_idx = random.randint(0, len(companies) - 1)
            c_name, c_tier, c_ind = companies[cust_idx]
            cust_id = f"CUST-{cust_idx + 1:04d}"
            
            region, country = random.choice(regions)
            channel = random.choice(channels)
            
            p_name, p_cat, p_sku, base_price, target_margin = random.choice(products)
            
            # Enterprise orders have larger quantities
            if c_tier == "Enterprise Strategic":
                qty = random.randint(5, 120)
                disc = round(random.uniform(0.05, 0.25), 2)
            elif c_tier == "Mid-Market":
                qty = random.randint(2, 40)
                disc = round(random.uniform(0.0, 0.15), 2)
            else:
                qty = random.randint(1, 15)
                disc = round(random.uniform(0.0, 0.08), 2)
                
            unit_price = base_price * round(random.uniform(0.92, 1.08), 2)
            subtotal = qty * unit_price
            total_amt = round(subtotal * (1.0 - disc), 2)
            
            # Gross margin with realistic noise
            margin_pct = round(target_margin * 100 + random.uniform(-4.0, 4.0), 2)
            cogs = round(total_amt * (1.0 - margin_pct / 100.0), 2)
            
            pay_terms = random.choice(payment_terms_list)
            status = random.choice(order_statuses)
            rep = random.choice(sales_reps)
            
            writer.writerow([
                order_id, order_date_str, f_year, f_qtr, cust_id,
                c_name, c_tier, c_ind, region, country,
                channel, p_cat, p_sku, p_name,
                qty, round(unit_price, 2), round(disc * 100, 1), total_amt,
                cogs, margin_pct, pay_terms, status, rep
            ])
    print(f"Generated {count} sales orders successfully.")


# -------------------------------------------------------------
# 2. CUSTOMER CHURN & RETENTION TELEMETRY (~1,500 Rows)
# -------------------------------------------------------------
def generate_customer_churn(count=1500):
    filepath = os.path.join(DEMO_DIR, "02_customer_churn_retention.csv")
    print(f"Generating {count} customer churn records -> {filepath}")
    
    industries = [
        "FinTech & Banking", "Healthcare & BioTech", "E-Commerce & Retail",
        "SaaS & Enterprise Cloud", "Manufacturing & Robotics", "Telecom & 5G",
        "Media & Entertainment", "Logistics & Supply Chain", "Energy & CleanTech",
        "Government & Public Sector", "Professional Services & Legal"
    ]
    
    tiers = ["Startup Tier", "Professional", "Enterprise Plus", "Custom Strategic"]
    sizes = ["10-50 Employees", "51-200 Employees", "201-1000 Employees", "1000-5000 Employees", "5000+ Enterprise"]
    countries = ["United States", "United Kingdom", "Germany", "Japan", "Taiwan", "Singapore", "Canada", "Australia", "France", "Netherlands", "Switzerland"]
    depth_levels = ["Basic Exploratory", "Core Functional", "Deep Advanced", "Full API Mesh & Automation"]
    
    headers = [
        "customer_id", "company_name", "industry", "company_size", "headquarters_country",
        "subscription_tier", "contract_type", "mrr_usd", "arr_usd", "contract_length_months",
        "tenure_months", "nps_score", "csat_score", "monthly_active_users",
        "license_utilization_pct", "support_tickets_count", "critical_escalations",
        "avg_resolution_time_hrs", "product_usage_hours_per_week", "feature_adoption_depth",
        "last_login_days_ago", "executive_sponsor_engaged", "churn_risk_score",
        "churn_risk_level", "account_status"
    ]
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        company_prefixes = [
            "Apex", "Nexus", "Vertex", "Quantum", "Hyperion", "Aegis", "Cobalt", "Starlight", "Titan", "Lumina",
            "Omni", "Solaris", "Prism", "Vanguard", "Horizon", "Strata", "Aero", "Pulse", "Terra", "Cygnus",
            "Novus", "Polaris", "Echo", "Synthetix", "Vector", "Zion", "Aura", "Boreal", "Crest", "Dynasty"
        ]
        company_suffixes = [
            "Technologies", "Solutions", "Dynamics", "Systems", "Global", "Networks", "Labs", "Group", "Robotics", "Analytics",
            "Ventures", "Digital", "Software", "Cloud", "Biomedical", "Security", "Industries", "Logistics", "Enterprises", "Capital"
        ]
        
        for i in range(1, count + 1):
            cust_id = f"CUST-SAAS-{i:05d}"
            comp_name = f"{company_prefixes[i % len(company_prefixes)]} {company_suffixes[(i * 7) % len(company_suffixes)]} {chr(65 + (i % 26))}"
            ind = random.choice(industries)
            size = random.choice(sizes)
            country = random.choice(countries)
            tier = random.choice(tiers)
            contract_type = random.choice(["Annual Pre-Paid", "Multi-Year 3-Yr Strategic", "Quarterly Invoiced", "Monthly Flexible"])
            
            if tier == "Custom Strategic":
                mrr = round(random.uniform(25000.0, 95000.0), 2)
                contract_len = random.choice([24, 36, 48])
                mau = random.randint(500, 6500)
            elif tier == "Enterprise Plus":
                mrr = round(random.uniform(9000.0, 28000.0), 2)
                contract_len = random.choice([12, 24, 36])
                mau = random.randint(150, 1200)
            elif tier == "Professional":
                mrr = round(random.uniform(3000.0, 9500.0), 2)
                contract_len = random.choice([12, 24])
                mau = random.randint(40, 300)
            else:
                mrr = round(random.uniform(800.0, 3200.0), 2)
                contract_len = 12
                mau = random.randint(10, 80)
                
            arr = round(mrr * 12.0, 2)
            tenure = random.randint(1, 60)
            
            # Correlated Churn Telemetry
            # High risk correlated with: low NPS, low CSAT, high escalations, inactive days, low usage
            is_unhappy = random.random() < 0.22
            
            if is_unhappy:
                nps = random.randint(1, 6)
                csat = round(random.uniform(1.2, 3.4), 1)
                tickets = random.randint(8, 35)
                escalations = random.randint(1, 5)
                res_time = round(random.uniform(24.0, 72.0), 1)
                usage_hrs = round(random.uniform(2.0, 25.0), 1)
                last_login = random.randint(14, 85)
                sponsor_engaged = random.random() < 0.15
                util_pct = round(random.uniform(25.0, 58.0), 1)
                risk_score = round(random.uniform(0.62, 0.98), 2)
                risk_level = "Critical" if risk_score >= 0.8 else "High"
                status = random.choice(["Active - At Risk", "Active - At Risk", "Under Review", "Churned"])
            else:
                nps = random.randint(7, 10)
                csat = round(random.uniform(4.0, 5.0), 1)
                tickets = random.randint(0, 8)
                escalations = 0 if random.random() < 0.85 else 1
                res_time = round(random.uniform(1.5, 12.0), 1)
                usage_hrs = round(random.uniform(45.0, 180.0), 1)
                last_login = random.randint(0, 7)
                sponsor_engaged = True
                util_pct = round(random.uniform(75.0, 100.0), 1)
                risk_score = round(random.uniform(0.02, 0.38), 2)
                risk_level = "Low" if risk_score < 0.25 else "Medium"
                status = "Active - Healthy" if risk_score < 0.35 else "In Renewal Discussion"
                
            depth = random.choice(depth_levels)
            
            writer.writerow([
                cust_id, comp_name, ind, size, country,
                tier, contract_type, mrr, arr, contract_len,
                tenure, nps, csat, mau,
                util_pct, tickets, escalations,
                res_time, usage_hrs, depth,
                last_login, "Yes" if sponsor_engaged else "No", risk_score,
                risk_level, status
            ])
    print(f"Generated {count} customer churn records successfully.")


# -------------------------------------------------------------
# 3. GLOBAL INVENTORY & SUPPLY CHAIN (~1,500 Rows)
# -------------------------------------------------------------
def generate_inventory_supply_chain(count=1500):
    filepath = os.path.join(DEMO_DIR, "03_inventory_supply_chain.csv")
    print(f"Generating {count} inventory supply chain records -> {filepath}")
    
    warehouses = [
        ("WH-US-01", "California Mega-Hub", "US-West", "United States"),
        ("WH-US-02", "Virginia Cloud Center", "US-East", "United States"),
        ("WH-US-03", "Chicago Central Depot", "US-Central", "United States"),
        ("WH-EU-01", "Frankfurt Euro-Hub", "EU-Central", "Germany"),
        ("WH-EU-02", "Rotterdam Logistics Park", "EU-West", "Netherlands"),
        ("WH-EU-03", "London Distribution Gateway", "EU-West", "United Kingdom"),
        ("WH-APAC-01", "Taipei Logistics Hub", "APAC-East", "Taiwan"),
        ("WH-APAC-02", "Tokyo High-Tech Depot", "APAC-East", "Japan"),
        ("WH-APAC-03", "Singapore Gateway Center", "APAC-South", "Singapore"),
        ("WH-APAC-04", "Sydney Tech Fulfillment", "APAC-ANZ", "Australia"),
        ("WH-LATAM-01", "Sao Paulo Distribution", "LATAM", "Brazil"),
        ("WH-MEA-01", "Dubai Industrial Port Hub", "MEA", "United Arab Emirates")
    ]
    
    product_templates = [
        ("High-Density GPU Tensor Server Node", "Compute Servers", 14500.00, 45, 120),
        ("Liquid-Cooled AI Inference Blade", "Compute Servers", 8900.00, 60, 150),
        ("Quantum Optical 800G Core Switch", "Networking Hardware", 18500.00, 30, 80),
        ("Ultra-Low Latency Spine Router", "Networking Hardware", 12000.00, 40, 100),
        ("All-Flash NVMe High-IOPS Array", "Storage Systems", 15200.00, 35, 90),
        ("Distributed Object Storage Block", "Storage Systems", 6400.00, 80, 200),
        ("Edge AI Gateway Controller", "Edge Devices", 1850.00, 200, 600),
        ("Industrial IoT Telemetry Sensor", "Edge Devices", 125.00, 1500, 5000),
        ("Redundant Power Distribution Unit 3-Phase", "Power & Cooling", 3200.00, 100, 300),
        ("Direct-to-Chip Liquid Cooling Manifold", "Power & Cooling", 4100.00, 80, 250),
        ("100G Single-Mode Optical Transceiver", "Optical Components", 280.00, 800, 3000),
        ("Dense Wavelength Mux Transceiver", "Optical Components", 750.00, 400, 1500),
        ("Hardware Security Module (HSM) Vault", "Security Appliances", 9800.00, 25, 70),
        ("Next-Gen Firewall Threat Shield", "Security Appliances", 5600.00, 60, 180)
    ]
    
    suppliers = [
        ("SUP-TW-01", "TSMC Advanced Semiconductor", "Taiwan", 99.4),
        ("SUP-TW-02", "Foxconn Precision Industry", "Taiwan", 96.8),
        ("SUP-TW-03", "Quanta Computer Advanced Server", "Taiwan", 97.5),
        ("SUP-TW-04", "Delta Electronics Power Solutions", "Taiwan", 98.2),
        ("SUP-NL-01", "ASML Precision Optics Hub", "Netherlands", 99.1),
        ("SUP-US-01", "Supermicro Engineering Lab", "United States", 95.9),
        ("SUP-US-02", "Broadcom Optical Networks", "United States", 97.8),
        ("SUP-JP-01", "Murata High-Freq Components", "Japan", 98.9),
        ("SUP-JP-02", "Kyocera Ceramic Packaging", "Japan", 98.1),
        ("SUP-KR-01", "Samsung Memory Module Division", "South Korea", 97.2),
        ("SUP-DE-01", "Siemens Industrial Automation", "Germany", 98.6)
    ]
    
    headers = [
        "sku_id", "product_name", "category", "warehouse_id", "warehouse_location",
        "region", "country", "current_stock", "allocated_stock", "available_stock",
        "safety_stock", "reorder_point_qty", "max_capacity_units", "unit_cost_usd",
        "total_inventory_value_usd", "supplier_id", "supplier_name", "supplier_country",
        "supplier_reliability_score", "lead_time_days", "shipping_method", "defect_rate_pct",
        "inventory_turnover_ratio", "stock_status", "last_audit_date"
    ]
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        start_date = datetime(2026, 1, 1)
        
        for i in range(1, count + 1):
            sku_id = f"SKU-HW-{1000 + i:05d}"
            p_name, p_cat, base_cost, min_s, max_s = random.choice(product_templates)
            p_name_variant = f"{p_name} v{((i % 4) + 1)}.0"
            
            wh_id, wh_loc, wh_reg, wh_country = random.choice(warehouses)
            sup_id, sup_name, sup_country, sup_rel = random.choice(suppliers)
            
            unit_cost = round(base_cost * random.uniform(0.90, 1.12), 2)
            safety_stock = random.randint(min_s, max_s)
            reorder_point = int(safety_stock * random.uniform(1.4, 2.2))
            max_capacity = int(reorder_point * random.uniform(2.5, 4.0))
            
            # Stock Status logic
            status_rand = random.random()
            if status_rand < 0.12:
                # Critical Shortage / Low stock
                current_stock = random.randint(0, int(safety_stock * 0.7))
                allocated = int(current_stock * random.uniform(0.4, 0.95))
                stock_status = "Critical Shortage" if current_stock < (safety_stock * 0.4) else "Low Stock"
            elif status_rand > 0.88:
                # Overstocked
                current_stock = int(max_capacity * random.uniform(0.85, 0.98))
                allocated = int(current_stock * random.uniform(0.1, 0.3))
                stock_status = "Overstocked"
            else:
                current_stock = random.randint(int(safety_stock * 1.1), int(reorder_point * 1.8))
                allocated = int(current_stock * random.uniform(0.2, 0.6))
                stock_status = "Optimal"
                
            avail_stock = max(0, current_stock - allocated)
            total_val = round(current_stock * unit_cost, 2)
            
            lead_time = random.randint(5, 45)
            shipping = random.choice(["Air Priority Express", "Ocean Freight Container", "Dedicated Rail Cargo", "Ground Fleet Line"])
            defect_rate = round(random.uniform(0.05, 3.2), 2)
            turnover = round(random.uniform(2.5, 14.2), 1)
            
            audit_dt = start_date + timedelta(days=random.randint(0, 220))
            audit_str = audit_dt.strftime("%Y-%m-%d")
            
            writer.writerow([
                sku_id, p_name_variant, p_cat, wh_id, wh_loc,
                wh_reg, wh_country, current_stock, allocated, avail_stock,
                safety_stock, reorder_point, max_capacity, unit_cost,
                total_val, sup_id, sup_name, sup_country,
                sup_rel, lead_time, shipping, defect_rate,
                turnover, stock_status, audit_str
            ])
    print(f"Generated {count} inventory records successfully.")


# -------------------------------------------------------------
# 4. ENTERPRISE FINANCIAL QUARTERLY METRICS (~800 Rows)
# -------------------------------------------------------------
def generate_financial_metrics(count=800):
    filepath = os.path.join(DEMO_DIR, "04_financial_quarterly_metrics.csv")
    print(f"Generating {count} financial quarterly records -> {filepath}")
    
    business_units = [
        ("Enterprise Cloud Platform", "ECP"),
        ("Artificial Intelligence & Data Solutions", "AIDS"),
        ("Cybersecurity & Zero-Trust Infrastructure", "CZTI"),
        ("Global Hardware & Semiconductor Systems", "GHSS"),
        ("Digital Commerce & B2B Marketplace", "DCBM"),
        ("Strategic FinTech & Payments Hub", "SFTP"),
        ("Professional Services & Transformation", "PST"),
        ("Advanced R&D & Quantum Computing", "ARDQ")
    ]
    
    departments = [
        ("Core Engineering & Software R&D", "ENG"),
        ("Global Enterprise Sales & Field Ops", "SALES"),
        ("Global Growth & Brand Marketing", "MKTG"),
        ("Customer Success & Technical Account Mgmt", "CSM"),
        ("Cloud Infrastructure & Network Operations", "OPS"),
        ("Corporate General & Administrative", "GA"),
        ("Legal, Risk & Compliance", "LEGAL"),
        ("Product Strategy & User Experience", "PROD")
    ]
    
    headers = [
        "record_id", "fiscal_year", "fiscal_quarter", "period_label",
        "business_unit_code", "business_unit", "department_code", "department",
        "revenue_usd", "cogs_usd", "gross_profit_usd", "gross_margin_pct",
        "rd_expense_usd", "sales_marketing_expense_usd", "ga_expense_usd",
        "total_opex_usd", "operating_income_usd", "ebitda_usd", "ebitda_margin_pct",
        "net_income_usd", "capex_usd", "headcount", "budget_allocated_usd",
        "budget_variance_pct", "revenue_growth_yoy_pct"
    ]
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        years = [2023, 2024, 2025, 2026]
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        
        record_idx = 1
        for yr in years:
            for qtr in quarters:
                # 2026 Q4 is future forecast
                period_label = f"{yr}-{qtr}"
                growth_factor = 1.0 + (yr - 2023) * 0.18 + (quarters.index(qtr) * 0.04)
                
                for bu_name, bu_code in business_units:
                    for dept_name, dept_code in departments:
                        if record_idx > count:
                            break
                        rec_id = f"FIN-{yr}-{record_idx:05d}"
                        
                        base_rev = random.uniform(2500000.0, 18000000.0) * growth_factor
                        # R&D and GA departments don't generate direct revenue, allocation is internal
                        if dept_code in ["ENG", "GA", "LEGAL", "PROD"]:
                            rev = round(base_rev * random.uniform(0.1, 0.4), 2)
                        else:
                            rev = round(base_rev, 2)
                            
                        # COGS is 18% to 35% of revenue
                        cogs_pct = random.uniform(0.18, 0.35)
                        cogs = round(rev * cogs_pct, 2)
                        gross_profit = round(rev - cogs, 2)
                        gross_margin = round((gross_profit / rev) * 100.0, 2) if rev > 0 else 0.0
                        
                        rd_exp = round(random.uniform(400000.0, 3200000.0) * growth_factor, 2)
                        sm_exp = round(random.uniform(300000.0, 2500000.0) * growth_factor, 2)
                        ga_exp = round(random.uniform(150000.0, 1200000.0), 2)
                        
                        total_opex = round(rd_exp + sm_exp + ga_exp, 2)
                        operating_income = round(gross_profit - total_opex, 2)
                        
                        capex = round(random.uniform(100000.0, 1800000.0) * growth_factor, 2)
                        ebitda = round(operating_income + (capex * 0.45), 2)
                        ebitda_margin = round((ebitda / rev) * 100.0, 2) if rev > 0 else 0.0
                        
                        tax_rate = 0.21
                        net_income = round(operating_income * (1.0 - tax_rate), 2)
                        
                        headcount = int(random.uniform(35, 450) * growth_factor)
                        budget = round(total_opex * random.uniform(0.92, 1.12), 2)
                        variance = round(((total_opex - budget) / budget) * 100.0, 2)
                        yoy_growth = round(random.uniform(8.5, 36.0) + (yr - 2023) * 4.0, 2)
                        
                        writer.writerow([
                            rec_id, yr, qtr, period_label,
                            bu_code, bu_name, dept_code, dept_name,
                            rev, cogs, gross_profit, gross_margin,
                            rd_exp, sm_exp, ga_exp,
                            total_opex, operating_income, ebitda, ebitda_margin,
                            net_income, capex, headcount, budget,
                            variance, yoy_growth
                        ])
                        record_idx += 1
    print(f"Generated {record_idx - 1} financial records successfully.")


# -------------------------------------------------------------
# 5. GLOBAL HR EMPLOYEE WORKFORCE & PERFORMANCE (~1,500 Rows)
# -------------------------------------------------------------
def generate_employee_performance(count=1500):
    filepath = os.path.join(DEMO_DIR, "05_hr_employee_performance.csv")
    print(f"Generating {count} employee workforce records -> {filepath}")
    
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
        "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
        "Daniel", "Nancy", "Matthew", "Lisa", "Anthony", "Betty", "Donald", "Margaret", "Mark", "Sandra",
        "Alex", "Elena", "Kenji", "Wei", "Ting", "Hiroshi", "Yuki", "Chloe", "Lucas", "Mateo", "Camila",
        "Ananya", "Rohan", "Mei", "Astrid", "Sven", "Fatima", "Tariq", "Zoe", "Dmitri"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
        "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Chen", "Lin", "Huang", "Sato", "Tanaka", "Yamamoto", "Dubois", "Moreau", "Mueller", "Schmidt", "Schneider",
        "Patel", "Sharma", "Santos", "Oliveira", "Ivanov", "Kowalski", "Kim", "Park", "Nakamura"
    ]
    
    departments = [
        ("Core Software Engineering", "SWE"),
        ("AI & Machine Learning Research", "AI-RES"),
        ("Enterprise Solutions Architecture", "ARCH"),
        ("Global Enterprise Sales & BD", "SALES"),
        ("Customer Success & Technical Support", "CSM"),
        ("Cloud Platform & DevOps / SRE", "SRE"),
        ("Product Management & Growth", "PM"),
        ("UI/UX Product Design", "DESIGN"),
        ("People Operations & Talent Acquisition", "HR"),
        ("Corporate Finance, Legal & Compliance", "FIN-LEGAL")
    ]
    
    job_roles = {
        "SWE": [
            ("L1 Associate Software Engineer", 85000, 105000, 0.10),
            ("L2 Software Engineer", 110000, 140000, 0.15),
            ("L3 Senior Software Engineer", 145000, 185000, 0.20),
            ("L4 Staff Distributed Engineer", 190000, 240000, 0.25),
            ("L5 Principal Infrastructure Architect", 250000, 320000, 0.30),
            ("Engineering Director", 280000, 360000, 0.35)
        ],
        "AI-RES": [
            ("L2 AI/ML Engineer", 125000, 160000, 0.15),
            ("L3 Senior Deep Learning Researcher", 170000, 220000, 0.25),
            ("L4 Staff AI Scientist", 225000, 290000, 0.30),
            ("L5 Principal Research Fellow", 300000, 420000, 0.40)
        ],
        "SALES": [
            ("Enterprise SDR / BDR", 65000, 85000, 0.30),
            ("Mid-Market Account Executive", 95000, 130000, 0.40),
            ("Senior Enterprise Account Executive", 140000, 190000, 0.50),
            ("Strategic Sales Director", 210000, 280000, 0.55),
            ("VP of Global Enterprise Sales", 300000, 400000, 0.60)
        ],
        "ARCH": [
            ("Senior Solutions Architect", 150000, 195000, 0.20),
            ("Principal Enterprise Architect", 210000, 270000, 0.25)
        ],
        "CSM": [
            ("Customer Success Manager", 85000, 115000, 0.15),
            ("Senior Technical Account Manager", 120000, 155000, 0.20),
            ("Director of Customer Success", 180000, 230000, 0.25)
        ],
        "SRE": [
            ("Cloud Infrastructure SRE", 120000, 155000, 0.18),
            ("Staff Reliability Architect", 195000, 250000, 0.25)
        ],
        "PM": [
            ("Product Manager", 115000, 150000, 0.15),
            ("Senior Group Product Manager", 165000, 215000, 0.22),
            ("Director of Product", 230000, 300000, 0.30)
        ],
        "DESIGN": [
            ("Product Designer", 95000, 130000, 0.12),
            ("Staff UI/UX Design Lead", 155000, 200000, 0.20)
        ],
        "HR": [
            ("People Operations Partner", 80000, 110000, 0.12),
            ("Talent Acquisition Lead", 105000, 140000, 0.18)
        ],
        "FIN-LEGAL": [
            ("Senior Financial Analyst", 100000, 135000, 0.15),
            ("Corporate Counsel / Compliance Director", 190000, 260000, 0.25)
        ]
    }
    
    locations = [
        ("San Francisco", "United States", "US-West"),
        ("New York", "United States", "US-East"),
        ("Austin", "United States", "US-Central"),
        ("Taipei", "Taiwan", "APAC-East"),
        ("Tokyo", "Japan", "APAC-East"),
        ("Singapore", "Singapore", "APAC-South"),
        ("London", "United Kingdom", "EU-West"),
        ("Berlin", "Germany", "EU-Central"),
        ("Zurich", "Switzerland", "EU-Central"),
        ("Sydney", "Australia", "APAC-ANZ"),
        ("Remote - Global", "Global Remote", "Remote")
    ]
    
    headers = [
        "employee_id", "first_name", "last_name", "work_email", "department",
        "job_title", "work_location", "country", "region", "employment_type",
        "hire_date", "tenure_years", "base_salary_usd", "bonus_target_pct",
        "annual_total_comp_usd", "performance_rating", "last_review_score",
        "projects_completed_ytd", "training_hours_completed", "overtime_hours_per_month",
        "satisfaction_score", "work_life_balance_rating", "peer_recognition_count",
        "attrition_risk_pct", "attrition_risk_level", "promotion_eligible"
    ]
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        start_date = datetime(2018, 1, 1)
        
        for i in range(1, count + 1):
            emp_id = f"EMP-{10000 + i:05d}"
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            email = f"{fn.lower()}.{ln.lower()}{i % 99}@enterprise-ai.corp"
            
            dept_name, dept_code = random.choice(departments)
            role_options = job_roles.get(dept_code, job_roles["SWE"])
            title, min_sal, max_sal, bonus_pct = random.choice(role_options)
            
            city, country, region = random.choice(locations)
            emp_type = "Full-Time Permanent" if random.random() < 0.94 else "Contractor Strategic"
            
            days_hired = random.randint(60, 2900)
            hire_dt = start_date + timedelta(days=days_hired)
            hire_str = hire_dt.strftime("%Y-%m-%d")
            tenure = round(days_hired / 365.25, 1)
            
            base_sal = round(random.uniform(min_sal, max_sal), -2)
            total_comp = round(base_sal * (1.0 + bonus_pct), -2)
            
            # Correlated HR Analytics
            # High performers: high satisfaction, high projects, eligible for promotion
            # Burnout risk: high overtime, low satisfaction, high attrition risk
            is_burnout = random.random() < 0.18
            
            if is_burnout:
                perf = round(random.uniform(2.5, 4.2), 2)
                review_score = round(random.uniform(2.0, 3.8), 1)
                projects = random.randint(10, 28)
                training = random.randint(2, 20)
                overtime = round(random.uniform(25.0, 58.0), 1)
                satisfaction = round(random.uniform(2.2, 5.5), 1)
                wlb = round(random.uniform(1.0, 2.5), 1)
                attrition_pct = round(random.uniform(0.60, 0.95), 2)
                attrition_lvl = "High"
                promo = False
            else:
                perf = round(random.uniform(3.6, 5.0), 2)
                review_score = round(random.uniform(3.8, 5.0), 1)
                projects = random.randint(4, 18)
                training = random.randint(20, 85)
                overtime = round(random.uniform(0.0, 15.0), 1)
                satisfaction = round(random.uniform(7.0, 9.9), 1)
                wlb = round(random.uniform(3.5, 5.0), 1)
                attrition_pct = round(random.uniform(0.03, 0.35), 2)
                attrition_lvl = "Low" if attrition_pct < 0.20 else "Medium"
                promo = (perf >= 4.5 and tenure >= 1.5 and satisfaction >= 7.5)
                
            peer_count = random.randint(1, 38)
            
            writer.writerow([
                emp_id, fn, ln, email, dept_name,
                title, city, country, region, emp_type,
                hire_str, tenure, base_sal, round(bonus_pct * 100, 1),
                total_comp, perf, review_score,
                projects, training, overtime,
                satisfaction, wlb, peer_count,
                attrition_pct, attrition_lvl, "Yes" if promo else "No"
            ])
    print(f"Generated {count} employee records successfully.")


# -------------------------------------------------------------
# 6. OMNICHANNEL MARKETING CAMPAIGNS & ATTRIBUTION (~1,200 Rows)
# -------------------------------------------------------------
def generate_marketing_campaigns(count=1200):
    filepath = os.path.join(DEMO_DIR, "06_marketing_campaign_attribution.csv")
    print(f"Generating {count} marketing campaign attribution records -> {filepath}")
    
    channels = [
        ("Google Search Ads - Enterprise Intent", "Paid Search", 0.032, 7.8, 120.0),
        ("LinkedIn B2B Sponsored Content & InMail", "Paid Social", 0.024, 8.5, 180.0),
        ("Technical SEO & Pillar Blog Content", "Organic Content", 0.058, 22.4, 35.0),
        ("Executive Newsletter Sponsorships", "Sponsored Content", 0.045, 12.8, 85.0),
        ("Gartner & Forrester Summit Sponsorships", "Events & Conferences", 0.018, 6.5, 320.0),
        ("Virtual Tech Demos & Hands-on Webinars", "Owned Events", 0.052, 10.4, 65.0),
        ("Regional Strategic Partner Co-Marketing", "Partner Co-Op", 0.039, 14.2, 55.0),
        ("Developer Hackathons & Open Source Grants", "Community", 0.065, 16.8, 40.0),
        ("YouTube Deep-Dive Tech Architecture", "Video Marketing", 0.028, 9.2, 90.0),
        ("Programmatic Account-Based Display (ABM)", "ABM Display", 0.015, 5.8, 210.0),
        ("Tech Podcast Host-Read Sponsorship", "Audio & Podcasts", 0.034, 11.5, 75.0)
    ]
    
    audiences = [
        "Fortune 500 CTOs & VP Infrastructure", "FinTech Chief Information Security Officers (CISO)",
        "Enterprise Data Engineering Leads", "Cloud Native DevOps & SRE Architects",
        "Healthcare & Life Sciences Tech Leads", "Retail E-Commerce Engineering Directors",
        "Global AI/ML Research Scientists", "SMB Growth Tech Founders"
    ]
    
    regions = ["North America", "Western Europe", "APAC (Japan/Taiwan/SG)", "ANZ", "Global Multi-Region", "Latin America", "Middle East"]
    
    headers = [
        "campaign_id", "campaign_name", "channel", "channel_category", "target_audience",
        "target_region", "ad_spend_usd", "impressions", "clicks", "click_through_rate_pct",
        "leads_generated", "cost_per_lead_usd", "mql_qualified_leads", "sql_sales_opportunities",
        "pipeline_created_usd", "conversions", "revenue_generated_usd", "return_on_ad_spend",
        "customer_acquisition_cost_usd", "roi_pct", "start_date", "end_date", "campaign_status"
    ]
    
    campaign_themes = [
        "Next-Gen Lakehouse Migration", "GenAI Enterprise Copilot Accelerator", "Zero-Trust Perimeter Defense",
        "Cloud Cost Optimization 40%", "Kubernetes Multi-Cloud Mesh", "Real-Time Telemetry at Scale",
        "Automated Compliance & SOC2", "Edge AI for Smart Robotics", "Quantum-Safe Cryptography Suite",
        "Developer Productivity Blitz", "High-Throughput Streaming Engine", "Unified Customer 360 AI"
    ]
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        start_date = datetime(2024, 1, 1)
        
        for i in range(1, count + 1):
            camp_id = f"CAMP-{2024 + (i // 500)}-{i:05d}"
            theme = random.choice(campaign_themes)
            qtr_str = f"Q{((i % 4) + 1)} {2024 + (i // 500)}"
            camp_name = f"{theme} - {qtr_str} [Phase {(i % 3) + 1}]"
            
            ch_name, ch_cat, avg_ctr, target_roas, avg_cpl = random.choice(channels)
            audience = random.choice(audiences)
            reg = random.choice(regions)
            
            spend = round(random.uniform(2500.0, 95000.0), -2)
            cpc = round(random.uniform(2.5, 18.0), 2)
            clicks = max(100, int(spend / cpc))
            ctr = round(avg_ctr * 100 * random.uniform(0.75, 1.35), 2)
            impressions = int(clicks / (ctr / 100.0))
            
            leads = max(5, int(spend / (avg_cpl * random.uniform(0.75, 1.3))))
            cpl = round(spend / leads, 2)
            
            mql = int(leads * random.uniform(0.40, 0.75))
            sql = max(1, int(mql * random.uniform(0.25, 0.55)))
            
            # Revenue generated & ROAS with realistic variations
            actual_roas = round(target_roas * random.uniform(0.65, 1.45), 2)
            rev_gen = round(spend * actual_roas, 2)
            pipeline = round(rev_gen * random.uniform(2.5, 5.0), 2)
            
            conversions = max(1, int(sql * random.uniform(0.18, 0.45)))
            cac = round(spend / conversions, 2)
            roi_pct = round(((rev_gen - spend) / spend) * 100.0, 1)
            
            days_offset = random.randint(0, 900)
            c_start = start_date + timedelta(days=days_offset)
            c_end = c_start + timedelta(days=random.randint(14, 90))
            
            status = "Completed" if c_end < datetime(2026, 8, 1) else ("Active" if c_start <= datetime(2026, 8, 15) else "Scheduled")
            
            writer.writerow([
                camp_id, camp_name, ch_name, ch_cat, audience,
                reg, spend, impressions, clicks, ctr,
                leads, cpl, mql, sql,
                pipeline, conversions, rev_gen, actual_roas,
                cac, roi_pct, c_start.strftime("%Y-%m-%d"), c_end.strftime("%Y-%m-%d"), status
            ])
    print(f"Generated {count} marketing campaign records successfully.")


def run_all():
    print("=== Generating Fortune 500 Scale Enterprise Demo Datasets ===")
    generate_sales_orders(2500)
    generate_customer_churn(1500)
    generate_inventory_supply_chain(1500)
    generate_financial_metrics(800)
    generate_employee_performance(1500)
    generate_marketing_campaigns(1200)
    print("=== All 6 Massive Enterprise Datasets Generated Successfully! ===")


if __name__ == "__main__":
    run_all()
