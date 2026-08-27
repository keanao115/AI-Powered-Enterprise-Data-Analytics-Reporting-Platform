from typing import Any, Dict, List, Optional
from app.core.security import DataClassification


class SchemaRegistry:
    def __init__(self):
        self._catalog: Dict[str, Dict[str, Any]] = {
            # --- DOMAIN 01: E-COMMERCE / RETAIL (Olist Brazilian E-Commerce) ---
            "olist_orders": {
                "description": "E-Commerce orders tracking purchase timestamp, approval, delivery milestones, estimated vs actual delivery, and delay days.",
                "columns": {
                    "order_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Unique order identifier"},
                    "customer_id": {"type": "VARCHAR", "classification": DataClassification.CONFIDENTIAL, "description": "Foreign key to customer profile"},
                    "order_status": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Order lifecycle status (delivered, shipped, canceled)"},
                    "order_purchase_timestamp": {"type": "TIMESTAMP", "classification": DataClassification.PUBLIC, "description": "Purchase transaction timestamp"},
                    "order_approved_at": {"type": "TIMESTAMP", "classification": DataClassification.PUBLIC, "description": "Payment approval timestamp"},
                    "order_delivered_carrier_date": {"type": "TIMESTAMP", "classification": DataClassification.PUBLIC, "description": "Hand-off to logistics carrier"},
                    "order_delivered_customer_date": {"type": "TIMESTAMP", "classification": DataClassification.PUBLIC, "description": "Actual delivery timestamp to customer"},
                    "order_estimated_delivery_date": {"type": "TIMESTAMP", "classification": DataClassification.PUBLIC, "description": "Estimated promised delivery date"},
                    "is_late_delivery": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "1 if actual delivery date exceeded estimated date, else 0"},
                    "delivery_delay_days": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Number of days delivered past estimate"},
                    "order_year": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Order fiscal year"},
                    "order_month": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Order fiscal month (1-12)"},
                    "order_year_month": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Year-Month format (YYYY-MM)"},
                },
            },
            "olist_order_items": {
                "description": "Order item line records with product IDs, seller IDs, item prices, and freight values.",
                "columns": {
                    "order_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Foreign key to olist_orders"},
                    "order_item_id": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Item sequential index within order"},
                    "product_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Foreign key to olist_products"},
                    "seller_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Seller unique identifier"},
                    "price": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "Item price in BRL"},
                    "freight_value": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "Freight and shipping charge in BRL"},
                    "total_item_value": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "Sum of price and freight"},
                },
            },
            "olist_products": {
                "description": "Product catalog with categories (Portuguese and English) and physical dimensions.",
                "columns": {
                    "product_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Unique product SKU identifier"},
                    "product_category_name": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Category name in Portuguese"},
                    "product_category_name_english": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Category name in English"},
                    "product_weight_g": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Product physical weight in grams"},
                    "product_length_cm": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Length in cm"},
                    "product_height_cm": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Height in cm"},
                    "product_width_cm": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Width in cm"},
                },
            },
            "olist_customers": {
                "description": "Customer geographical profiles across Brazilian states and zip codes.",
                "columns": {
                    "customer_id": {"type": "VARCHAR", "classification": DataClassification.CONFIDENTIAL, "description": "Order-specific customer key"},
                    "customer_unique_id": {"type": "VARCHAR", "classification": DataClassification.CONFIDENTIAL, "description": "Unique customer master identifier"},
                    "customer_zip_code_prefix": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Zip code prefix"},
                    "customer_city": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "City name"},
                    "customer_state": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "2-letter Brazilian state code (e.g. SP, RJ, MG)"},
                },
            },
            "olist_order_payments": {
                "description": "Order payment method records (credit card, boleto, voucher, debit card), installments and value.",
                "columns": {
                    "order_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Foreign key to olist_orders"},
                    "payment_sequential": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Payment sequence number"},
                    "payment_type": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Payment instrument (credit_card, boleto, voucher, debit_card)"},
                    "payment_installments": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Number of payment installments"},
                    "payment_value": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "Transaction payment value"},
                },
            },
            "olist_order_reviews": {
                "description": "Customer satisfaction review scores (1 to 5 stars) and review creation date.",
                "columns": {
                    "review_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Unique review identifier"},
                    "order_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Foreign key to olist_orders"},
                    "review_score": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Customer satisfaction rating (1 to 5 stars)"},
                    "review_creation_date": {"type": "DATE", "classification": DataClassification.PUBLIC, "description": "Date review was submitted"},
                },
            },

            # --- DOMAIN 02: URBAN TRANSPORTATION (NYC TLC Taxi) ---
            "nyc_taxi_trips": {
                "description": "NYC TLC yellow/green taxi trip records with pickup/dropoff timestamps, zones, fares, tips, tolls, and duration.",
                "columns": {
                    "trip_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Unique trip identifier"},
                    "vendor_id": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "TPEP/LPEP provider code"},
                    "pickup_datetime": {"type": "TIMESTAMP", "classification": DataClassification.PUBLIC, "description": "Trip pickup timestamp"},
                    "dropoff_datetime": {"type": "TIMESTAMP", "classification": DataClassification.PUBLIC, "description": "Trip dropoff timestamp"},
                    "passenger_count": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Passenger count"},
                    "trip_distance_miles": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "Trip distance in miles"},
                    "pickup_location_id": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "TLC taxi pickup zone location ID"},
                    "dropoff_location_id": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "TLC taxi dropoff zone location ID"},
                    "rate_code_id": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Rate code (1=Standard, 2=JFK, etc.)"},
                    "payment_type": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Payment method (Credit Card, Cash, Dispute)"},
                    "fare_amount": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "Base metered fare"},
                    "extra_surcharge": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "Rush hour / overnight surcharges"},
                    "mta_tax": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "MTA tax ($0.50)"},
                    "tip_amount": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "Driver tip amount"},
                    "tolls_amount": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "Bridge and tunnel tolls"},
                    "congestion_surcharge": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "NY State congestion surcharge"},
                    "total_amount": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "Total charge to passenger"},
                    "trip_duration_minutes": {"type": "DECIMAL(8,1)", "classification": DataClassification.PUBLIC, "description": "Calculated trip duration in minutes"},
                    "pickup_hour": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Pickup hour of the day (0-23)"},
                    "pickup_day_of_week": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Day of the week (Monday-Sunday)"},
                    "pickup_date": {"type": "DATE", "classification": DataClassification.PUBLIC, "description": "Pickup calendar date"},
                    "pickup_year_month": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Year-Month (YYYY-MM)"},
                },
            },
            "taxi_zones": {
                "description": "NYC TLC 263 official taxi zone boundary lookups and borough assignments.",
                "columns": {
                    "location_id": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Location ID matching pickup/dropoff ID"},
                    "zone_name": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Neighborhood zone name (e.g. Midtown Center, JFK Airport)"},
                    "borough": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Borough name (Manhattan, Brooklyn, Queens, Bronx, Staten Island, EWR)"},
                },
            },

            # --- DOMAIN 03: AIRLINE OPERATIONS (U.S. DOT BTS) ---
            "bts_flights": {
                "description": "U.S. BTS reporting carrier scheduled vs actual flight performance, delays, causes, and cancellations.",
                "columns": {
                    "flight_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Unique flight record key"},
                    "flight_date": {"type": "DATE", "classification": DataClassification.PUBLIC, "description": "Scheduled flight date"},
                    "carrier_code": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "2-letter IATA carrier code (e.g. AA, DL, UA, WN)"},
                    "flight_number": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Flight number"},
                    "origin_airport": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Origin 3-letter IATA airport code"},
                    "dest_airport": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Destination 3-letter IATA airport code"},
                    "route": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Origin-Destination route pair (e.g. JFK-LAX)"},
                    "scheduled_dep_time": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Scheduled departure time (HH:MM)"},
                    "departure_delay_minutes": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Departure delay in minutes (>14 min considered delayed)"},
                    "arrival_delay_minutes": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Arrival delay in minutes (>14 min considered delayed)"},
                    "is_arr_on_time": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "1 if arrived <= 14 mins of schedule and not canceled, else 0"},
                    "is_dep_on_time": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "1 if departed <= 14 mins of schedule and not canceled, else 0"},
                    "cancelled": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "1 if flight was cancelled, else 0"},
                    "cancellation_reason": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Cancellation cause (Weather, Carrier, NAS, Security)"},
                    "diverted": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "1 if flight was diverted to alternate airport, else 0"},
                    "air_time_minutes": {"type": "DECIMAL(8,1)", "classification": DataClassification.PUBLIC, "description": "Flight airborne duration in minutes"},
                    "distance_miles": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Flight distance in nautical miles"},
                    "taxi_out_minutes": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Taxi-out duration from gate to takeoff"},
                    "taxi_in_minutes": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Taxi-in duration from landing to gate"},
                    "carrier_delay_minutes": {"type": "DECIMAL(8,1)", "classification": DataClassification.PUBLIC, "description": "Delay attributable to airline operations"},
                    "weather_delay_minutes": {"type": "DECIMAL(8,1)", "classification": DataClassification.PUBLIC, "description": "Delay attributable to meteorological conditions"},
                    "nas_delay_minutes": {"type": "DECIMAL(8,1)", "classification": DataClassification.PUBLIC, "description": "Delay attributable to National Airspace System"},
                    "security_delay_minutes": {"type": "DECIMAL(8,1)", "classification": DataClassification.PUBLIC, "description": "Delay attributable to security screening"},
                    "late_aircraft_delay_minutes": {"type": "DECIMAL(8,1)", "classification": DataClassification.PUBLIC, "description": "Delay caused by late arrival of previous aircraft"},
                    "month": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Month number (1-12)"},
                    "day_of_week": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Day of the week (Monday-Sunday)"},
                },
            },
            "bts_airlines": {
                "description": "Major U.S. commercial airline carrier metadata and headquarters.",
                "columns": {
                    "carrier_code": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "IATA carrier code"},
                    "airline_name": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Full legal carrier name"},
                    "headquarters": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Corporate headquarters city/state"},
                },
            },
            "bts_airports": {
                "description": "Commercial hub airport metadata across U.S. geographic regions.",
                "columns": {
                    "airport_code": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "3-letter IATA airport code"},
                    "airport_name": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Airport name"},
                    "city": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "City name"},
                    "state": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "2-letter state code"},
                    "region": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "U.S. geographic region (Northeast, South, Midwest, West)"},
                },
            },

            # --- DOMAIN 04: HEALTHCARE / CLINICAL (PhysioNet MIMIC-IV) ---
            "mimic_patients": {
                "description": "Deidentified patient demographics with strict RESTRICTED classification.",
                "columns": {
                    "subject_id": {"type": "INTEGER", "classification": DataClassification.RESTRICTED, "description": "Deidentified patient ID"},
                    "gender": {"type": "VARCHAR", "classification": DataClassification.CONFIDENTIAL, "description": "Patient biological sex (M/F)"},
                    "anchor_age": {"type": "INTEGER", "classification": DataClassification.CONFIDENTIAL, "description": "Patient anchor age in years"},
                    "anchor_year_group": {"type": "VARCHAR", "classification": DataClassification.RESTRICTED, "description": "Deidentified 3-year date shift group"},
                    "dod_recorded": {"type": "INTEGER", "classification": DataClassification.RESTRICTED, "description": "Date of death recorded flag"},
                },
            },
            "mimic_admissions": {
                "description": "Hospital admission records tracking admission type, insurance, and length of stay (LOS).",
                "columns": {
                    "hadm_id": {"type": "INTEGER", "classification": DataClassification.RESTRICTED, "description": "Hospital admission ID"},
                    "subject_id": {"type": "INTEGER", "classification": DataClassification.RESTRICTED, "description": "Patient identifier"},
                    "admittime": {"type": "TIMESTAMP", "classification": DataClassification.RESTRICTED, "description": "Hospital admission timestamp"},
                    "dischtime": {"type": "TIMESTAMP", "classification": DataClassification.RESTRICTED, "description": "Hospital discharge timestamp"},
                    "admission_type": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Admission category (EW EMER., OBSERVATION, URGENT)"},
                    "admission_location": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Point of origin location"},
                    "insurance": {"type": "VARCHAR", "classification": DataClassification.CONFIDENTIAL, "description": "Primary insurance payer"},
                    "hospital_expire_flag": {"type": "INTEGER", "classification": DataClassification.RESTRICTED, "description": "1 if deceased during admission, else 0"},
                    "length_of_stay_days": {"type": "DECIMAL(8,1)", "classification": DataClassification.PUBLIC, "description": "Total length of hospital stay in days"},
                    "admission_year": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Admission year"},
                    "admission_month": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Admission month (1-12)"},
                },
            },
            "mimic_icu_stays": {
                "description": "Intensive Care Unit (ICU) stays, care unit types (MICU, SICU, CCU), and ICU duration.",
                "columns": {
                    "stay_id": {"type": "INTEGER", "classification": DataClassification.RESTRICTED, "description": "ICU stay identifier"},
                    "subject_id": {"type": "INTEGER", "classification": DataClassification.RESTRICTED, "description": "Patient identifier"},
                    "hadm_id": {"type": "INTEGER", "classification": DataClassification.RESTRICTED, "description": "Hospital admission ID"},
                    "first_careunit": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "First ICU care unit entered"},
                    "last_careunit": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Final ICU care unit before discharge"},
                    "icu_los_days": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "Length of stay in ICU in days"},
                    "intime": {"type": "TIMESTAMP", "classification": DataClassification.RESTRICTED, "description": "ICU admission timestamp"},
                    "outtime": {"type": "TIMESTAMP", "classification": DataClassification.RESTRICTED, "description": "ICU discharge timestamp"},
                },
            },
            "mimic_diagnoses": {
                "description": "Clinical ICD-10 diagnostic classifications and diagnostic sequence numbers.",
                "columns": {
                    "hadm_id": {"type": "INTEGER", "classification": DataClassification.RESTRICTED, "description": "Hospital admission ID"},
                    "subject_id": {"type": "INTEGER", "classification": DataClassification.RESTRICTED, "description": "Patient identifier"},
                    "seq_num": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Diagnosis priority sequence (1=Primary)"},
                    "icd_code": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "ICD-10 clinical diagnosis code"},
                    "icd_title": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Standardized medical diagnosis title"},
                    "category": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Clinical system category (Circulatory, Respiratory, Endocrine)"},
                },
            },

            # --- DOMAIN 05: PUBLIC SAFETY (City of Chicago Crimes Portal) ---
            "chicago_crimes": {
                "description": "Reported municipal crime incidents in Chicago tracking primary types, locations, wards, and arrest outcomes.",
                "columns": {
                    "case_number": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "CPD official case number"},
                    "incident_date": {"type": "TIMESTAMP", "classification": DataClassification.PUBLIC, "description": "Reported incident timestamp"},
                    "primary_type": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Primary crime type (THEFT, BATTERY, ASSAULT, etc.)"},
                    "crime_category": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "High-level classification (Property, Violent, Financial)"},
                    "description": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Subcategory incident description"},
                    "location_description": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Location setting (STREET, RESIDENCE, APARTMENT)"},
                    "arrest": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "1 if arrest was made, else 0"},
                    "domestic": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "1 if domestic-related, else 0"},
                    "district": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "CPD Police District Number (1-25)"},
                    "ward": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Chicago City Council Ward (1-50)"},
                    "community_area": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Chicago community area index (1-77)"},
                    "fbi_code": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "FBI UCR classification code"},
                    "year": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Calendar year of incident"},
                    "month": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Month number (1-12)"},
                    "day_of_week": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Day of the week"},
                    "hour_of_day": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Hour of the day (0-23)"},
                    "year_month": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Year-Month (YYYY-MM)"},
                },
            },
            "chicago_districts": {
                "description": "Chicago Police Department (CPD) 22 official district headquarters and names.",
                "columns": {
                    "district_number": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Police district number"},
                    "district_name": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "District name (e.g. Central, Near North, Harrison)"},
                    "station_address": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "District station street address"},
                },
            },

            # --- DOMAIN 06: FINANCIAL MARKETS (SEC EDGAR & Market Equities) ---
            "market_securities": {
                "description": "U.S. public listed corporate securities, sectors, industries, and SEC CIK numbers.",
                "columns": {
                    "ticker": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Stock ticker symbol (e.g. AAPL, MSFT, NVDA)"},
                    "company_name": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Corporate entity legal name"},
                    "sector": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "GICS economic sector"},
                    "industry": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "GICS industry classification"},
                    "exchange": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Listing exchange (NASDAQ, NYSE)"},
                    "cik": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "SEC Central Index Key (10-digit identifier)"},
                    "market_cap_mil_usd": {"type": "DECIMAL(12,2)", "classification": DataClassification.PUBLIC, "description": "Market capitalization in millions USD"},
                },
            },
            "market_daily_prices": {
                "description": "Daily OHLCV trading prices, daily returns, 50-day moving average, and 30-day volatility.",
                "columns": {
                    "ticker": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Stock ticker symbol"},
                    "trading_date": {"type": "DATE", "classification": DataClassification.PUBLIC, "description": "Trading calendar date"},
                    "open_price": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "Opening trade price"},
                    "high_price": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "Daily high price"},
                    "low_price": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "Daily low price"},
                    "close_price": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "Closing price"},
                    "adj_close_price": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "Split/dividend adjusted close price"},
                    "volume": {"type": "BIGINT", "classification": DataClassification.PUBLIC, "description": "Shares traded volume"},
                    "daily_return_pct": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "Daily percentage price change"},
                    "trading_value_usd": {"type": "DECIMAL(14,2)", "classification": DataClassification.PUBLIC, "description": "Total dollar trading volume"},
                    "ma_50": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "50-day moving average price"},
                    "volatility_30d": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "30-day realized price volatility"},
                    "year_month": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Year-Month (YYYY-MM)"},
                },
            },
            "market_financial_facts": {
                "description": "SEC EDGAR 10-Q/10-K reported financial facts (revenue, net income, FCF, R&D, margins).",
                "columns": {
                    "fact_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Unique financial fact identifier"},
                    "ticker": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Stock ticker symbol"},
                    "fiscal_period": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Fiscal quarter (e.g. 2023-Q1, 2024-Q2)"},
                    "form_type": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "SEC filing form (10-Q, 10-K)"},
                    "revenue_mil_usd": {"type": "DECIMAL(10,1)", "classification": DataClassification.PUBLIC, "description": "Reported total revenue in millions USD"},
                    "net_income_mil_usd": {"type": "DECIMAL(10,1)", "classification": DataClassification.PUBLIC, "description": "Reported net income in millions USD"},
                    "free_cash_flow_mil_usd": {"type": "DECIMAL(10,1)", "classification": DataClassification.PUBLIC, "description": "Free cash flow in millions USD"},
                    "rnd_expense_mil_usd": {"type": "DECIMAL(10,1)", "classification": DataClassification.PUBLIC, "description": "Research and development expense"},
                    "gross_margin_pct": {"type": "DECIMAL(8,1)", "classification": DataClassification.PUBLIC, "description": "Gross profit margin percentage"},
                    "operating_margin_pct": {"type": "DECIMAL(8,1)", "classification": DataClassification.PUBLIC, "description": "Operating profit margin percentage"},
                    "eps_diluted_usd": {"type": "DECIMAL(8,2)", "classification": DataClassification.PUBLIC, "description": "Diluted earnings per share in USD"},
                    "filing_date": {"type": "DATE", "classification": DataClassification.PUBLIC, "description": "SEC EDGAR official filing date"},
                },
            },

            # --- PREVIOUS SYNTHETIC DEMO TABLES (KEPT FOR COMPATIBILITY) ---
            "sales_orders": {
                "description": "Enterprise B2B sales transaction records with margins and regional reps.",
                "columns": {
                    "order_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Order key"},
                    "total_amount": {"type": "DECIMAL(12,2)", "classification": DataClassification.PUBLIC, "description": "Total order amount in USD"},
                    "gross_margin_pct": {"type": "DECIMAL(5,2)", "classification": DataClassification.PUBLIC, "description": "Gross margin percentage"},
                    "region": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Sales territory"},
                }
            },
            "customer_churn": {
                "description": "SaaS customer account metrics, MRR, NPS, and churn risk scores.",
                "columns": {
                    "customer_id": {"type": "VARCHAR", "classification": DataClassification.CONFIDENTIAL, "description": "Customer key"},
                    "industry": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Industry domain"},
                    "mrr_usd": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "Monthly recurring revenue"},
                    "churn_risk_score": {"type": "DECIMAL(4,2)", "classification": DataClassification.PUBLIC, "description": "ML churn risk score (0.0 to 1.0)"},
                }
            },
            "inventory_supply_chain": {
                "description": "Global hardware warehouse inventory levels and stock status.",
                "columns": {
                    "sku_id": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Stock keeping unit"},
                    "warehouse_location": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Warehouse hub"},
                    "current_stock": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Current stock units"},
                    "safety_stock": {"type": "INTEGER", "classification": DataClassification.PUBLIC, "description": "Minimum safety buffer"},
                }
            },
            "financial_metrics": {
                "description": "Corporate quarterly P&L statements, EBITDA, and budget variances.",
                "columns": {
                    "department": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Department name"},
                    "revenue_usd": {"type": "DECIMAL(12,2)", "classification": DataClassification.PUBLIC, "description": "Revenue"},
                    "ebitda_usd": {"type": "DECIMAL(12,2)", "classification": DataClassification.PUBLIC, "description": "EBITDA profit"},
                }
            },
            "employee_performance": {
                "description": "Workforce performance ratings, compensation, and satisfaction metrics.",
                "columns": {
                    "department": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Department name"},
                    "performance_rating": {"type": "DECIMAL(3,2)", "classification": DataClassification.PUBLIC, "description": "Performance rating (1.0 to 5.0)"},
                    "annual_base_salary_usd": {"type": "DECIMAL(10,2)", "classification": DataClassification.CONFIDENTIAL, "description": "Base salary"},
                }
            },
            "marketing_campaigns": {
                "description": "Multi-channel advertising campaigns, ad spend, and ROAS.",
                "columns": {
                    "channel": {"type": "VARCHAR", "classification": DataClassification.PUBLIC, "description": "Marketing channel"},
                    "ad_spend_usd": {"type": "DECIMAL(10,2)", "classification": DataClassification.PUBLIC, "description": "Advertising spend"},
                    "roas": {"type": "DECIMAL(6,2)", "classification": DataClassification.PUBLIC, "description": "Return on ad spend"},
                }
            },
        }

    def get_tables(self, tenant_id: str) -> List[str]:
        return list(self._catalog.keys())

    def get_table_details(self, table_name: str) -> Optional[Dict[str, Any]]:
        return self._catalog.get(table_name)


schema_registry = SchemaRegistry()
