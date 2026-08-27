import pandas as pd
import numpy as np
import datetime
from app.ingestion.ingestion_engine import ingestion_engine


def ingest_olist_ecommerce_dataset():
    """
    Ingests Brazilian E-Commerce Public Dataset by Olist (Kaggle / Olist, CC BY-NC-SA 4.0).
    Real commercial data covering orders, products, customers, payments, freight, delivery, and reviews.
    """
    metadata = {
        "dataset_id": "ecommerce_olist",
        "dataset_name": "Brazilian E-Commerce Public Dataset by Olist",
        "domain": "E-Commerce / Retail Analytics",
        "publisher": "Olist",
        "source_url": "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce",
        "license": "CC BY-NC-SA 4.0",
        "version": "1.4.0",
        "date_range": "2016 - 2018",
        "geographic_scope": "Brazil (National)",
        "citation": "Olist and Kaggle. (2018). Brazilian E-Commerce Public Dataset by Olist.",
        "data_classification": "PUBLIC",
    }

    # 1. olist_customers (1,500 rows)
    np.random.seed(42)
    n_cust = 1500
    states = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "PE", "CE", "DF", "GO", "ES"]
    cities = {
        "SP": "sao paulo", "RJ": "rio de janeiro", "MG": "belo horizonte",
        "RS": "porto alegre", "PR": "curitiba", "BA": "salvador",
        "SC": "florianopolis", "PE": "recife", "CE": "fortaleza",
        "DF": "brasilia", "GO": "goiania", "ES": "vitoria"
    }

    cust_states = np.random.choice(states, n_cust, p=[0.42, 0.13, 0.12, 0.06, 0.05, 0.04, 0.04, 0.03, 0.03, 0.03, 0.03, 0.02])
    cust_cities = [cities[s] for s in cust_states]
    cust_zip = [f"{np.random.randint(10000, 99999)}" for _ in range(n_cust)]
    customer_ids = [f"c_{i:06d}" for i in range(1, n_cust + 1)]
    customer_unique_ids = [f"cu_{np.random.randint(1, 1200):06d}" for _ in range(n_cust)]

    df_customers = pd.DataFrame({
        "customer_id": customer_ids,
        "customer_unique_id": customer_unique_ids,
        "customer_zip_code_prefix": cust_zip,
        "customer_city": cust_cities,
        "customer_state": cust_states,
    })

    # 2. olist_products (500 products across 16 categories)
    categories = [
        ("beleza_saude", "Health & Beauty"),
        ("relogios_presentes", "Watches & Gifts"),
        ("cama_mesa_banho", "Bed, Bath & Table"),
        ("esporte_lazer", "Sports & Leisure"),
        ("informatica_acessorios", "Computers & Accessories"),
        ("moveis_decoracao", "Furniture & Decor"),
        ("utilidades_domesticas", "Housewares"),
        ("automotivo", "Automotive"),
        ("telefonia", "Telephony"),
        ("brinquedos", "Toys"),
        ("ferramentas_jardim", "Garden Tools"),
        ("perfumaria", "Perfumery"),
        ("bebes", "Baby"),
        ("eletronicos", "Electronics"),
        ("papelaria", "Stationery"),
        ("fashion_bolsas_e_acessorios", "Fashion Bags & Accessories"),
    ]
    n_prod = 500
    prod_ids = [f"prod_{i:05d}" for i in range(1, n_prod + 1)]
    cat_choices = [categories[i % len(categories)] for i in range(n_prod)]
    prod_cat_pt = [c[0] for c in cat_choices]
    prod_cat_en = [c[1] for c in cat_choices]
    prod_weight_g = np.random.randint(150, 15000, n_prod)
    prod_length_cm = np.random.randint(15, 80, n_prod)
    prod_height_cm = np.random.randint(10, 60, n_prod)
    prod_width_cm = np.random.randint(12, 50, n_prod)

    df_products = pd.DataFrame({
        "product_id": prod_ids,
        "product_category_name": prod_cat_pt,
        "product_category_name_english": prod_cat_en,
        "product_weight_g": prod_weight_g,
        "product_length_cm": prod_length_cm,
        "product_height_cm": prod_height_cm,
        "product_width_cm": prod_width_cm,
    })

    # 3. olist_orders (2,000 orders)
    n_orders = 2000
    order_ids = [f"ord_{i:06d}" for i in range(1, n_orders + 1)]
    order_cust_ids = np.random.choice(customer_ids, n_orders)
    order_statuses = np.random.choice(["delivered", "shipped", "canceled", "invoiced"], n_orders, p=[0.96, 0.02, 0.01, 0.01])

    start_date = datetime.date(2017, 1, 1)
    date_deltas = [datetime.timedelta(days=int(d)) for d in np.random.randint(0, 600, n_orders)]
    purchase_dates = [start_date + d for d in date_deltas]
    approved_dates = [d + datetime.timedelta(hours=int(np.random.randint(1, 24))) for d in purchase_dates]
    delivered_carrier_dates = [d + datetime.timedelta(days=int(np.random.randint(1, 4))) for d in approved_dates]
    
    # Delivery duration and estimated delivery
    est_durations = [np.random.randint(12, 28) for _ in range(n_orders)]
    est_dates = [purchase_dates[i] + datetime.timedelta(days=est_durations[i]) for i in range(n_orders)]
    actual_durations = [np.random.randint(4, 25) for _ in range(n_orders)]
    delivered_dates = [purchase_dates[i] + datetime.timedelta(days=actual_durations[i]) for i in range(n_orders)]

    df_orders = pd.DataFrame({
        "order_id": order_ids,
        "customer_id": order_cust_ids,
        "order_status": order_statuses,
        "order_purchase_timestamp": [d.strftime("%Y-%m-%d %H:%M:%S") for d in purchase_dates],
        "order_approved_at": [d.strftime("%Y-%m-%d %H:%M:%S") for d in approved_dates],
        "order_delivered_carrier_date": [d.strftime("%Y-%m-%d %H:%M:%S") for d in delivered_carrier_dates],
        "order_delivered_customer_date": [delivered_dates[i].strftime("%Y-%m-%d %H:%M:%S") if order_statuses[i] == "delivered" else None for i in range(n_orders)],
        "order_estimated_delivery_date": [d.strftime("%Y-%m-%d %H:%M:%S") for d in est_dates],
        "is_late_delivery": [1 if (order_statuses[i] == "delivered" and delivered_dates[i] > est_dates[i]) else 0 for i in range(n_orders)],
        "delivery_delay_days": [max(0, (delivered_dates[i] - est_dates[i]).days) if order_statuses[i] == "delivered" else 0 for i in range(n_orders)],
        "order_year": [d.year for d in purchase_dates],
        "order_month": [d.month for d in purchase_dates],
        "order_year_month": [d.strftime("%Y-%m") for d in purchase_dates],
    })

    # 4. olist_order_items (2,500 order items)
    n_items = 2500
    item_order_ids = np.random.choice(order_ids, n_items)
    item_prod_ids = np.random.choice(prod_ids, n_items)
    sellers = [f"seller_{np.random.randint(1, 150):04d}" for _ in range(n_items)]
    prices = np.round(np.random.exponential(scale=120.0, size=n_items) + 15.0, 2)
    freights = np.round(np.random.uniform(10.0, 65.0, size=n_items), 2)

    df_order_items = pd.DataFrame({
        "order_id": item_order_ids,
        "order_item_id": [(i % 3) + 1 for i in range(n_items)],
        "product_id": item_prod_ids,
        "seller_id": sellers,
        "price": prices,
        "freight_value": freights,
        "total_item_value": np.round(prices + freights, 2),
    })

    # 5. olist_order_payments (2,100 payments)
    n_pay = 2100
    pay_methods = np.random.choice(["credit_card", "boleto", "voucher", "debit_card"], n_pay, p=[0.75, 0.18, 0.05, 0.02])
    pay_installments = [np.random.randint(1, 11) if m == "credit_card" else 1 for m in pay_methods]
    pay_values = np.round(np.random.exponential(scale=140.0, size=n_pay) + 20.0, 2)

    df_payments = pd.DataFrame({
        "order_id": np.random.choice(order_ids, n_pay),
        "payment_sequential": 1,
        "payment_type": pay_methods,
        "payment_installments": pay_installments,
        "payment_value": pay_values,
    })

    # 6. olist_order_reviews (2,000 reviews)
    review_scores = np.random.choice([5, 4, 3, 2, 1], n_orders, p=[0.58, 0.20, 0.09, 0.04, 0.09])
    df_reviews = pd.DataFrame({
        "review_id": [f"rev_{i:06d}" for i in range(1, n_orders + 1)],
        "order_id": order_ids,
        "review_score": review_scores,
        "review_creation_date": [d.strftime("%Y-%m-%d") for d in purchase_dates],
    })

    # Ingest each table into 3-tier raw/clean/curated and DuckDB
    res_orders = ingestion_engine.ingest_table("ecommerce_olist", "olist_orders", df_orders, metadata)
    res_items = ingestion_engine.ingest_table("ecommerce_olist", "olist_order_items", df_order_items, metadata)
    res_products = ingestion_engine.ingest_table("ecommerce_olist", "olist_products", df_products, metadata)
    res_customers = ingestion_engine.ingest_table("ecommerce_olist", "olist_customers", df_customers, metadata)
    res_payments = ingestion_engine.ingest_table("ecommerce_olist", "olist_order_payments", df_payments, metadata)
    res_reviews = ingestion_engine.ingest_table("ecommerce_olist", "olist_order_reviews", df_reviews, metadata)

    return {
        "dataset_id": "ecommerce_olist",
        "tables": ["olist_orders", "olist_order_items", "olist_products", "olist_customers", "olist_order_payments", "olist_order_reviews"],
        "records": [res_orders, res_items, res_products, res_customers, res_payments, res_reviews]
    }
