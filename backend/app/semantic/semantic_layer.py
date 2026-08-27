from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class MetricDefinition(BaseModel):
    name: str
    description: str
    domain: str
    dataset_id: str
    formula: str
    dimensions: List[str]
    allowed_aggregations: List[str]
    governance_rule: Optional[str] = None


class SemanticLayer:
    def __init__(self):
        self.metrics: Dict[str, MetricDefinition] = {
            # --- E-COMMERCE / RETAIL (Olist) ---
            "gross_merchandise_value": MetricDefinition(
                name="Gross Merchandise Value (GMV)",
                description="Total monetary value of items ordered through the platform including freight.",
                domain="E-Commerce / Retail",
                dataset_id="ecommerce_olist",
                formula="SUM(price + freight_value)",
                dimensions=["order_year_month", "product_category_name_english", "customer_state"],
                allowed_aggregations=["SUM"],
                governance_rule="Distinguish GMV from accounting profit. Do NOT invent cost-of-goods or margin if unavailable.",
            ),
            "average_order_value": MetricDefinition(
                name="Average Order Value (AOV)",
                description="Average monetary value per distinct customer order transaction.",
                domain="E-Commerce / Retail",
                dataset_id="ecommerce_olist",
                formula="SUM(price + freight_value) / COUNT(DISTINCT order_id)",
                dimensions=["order_year_month", "product_category_name_english", "customer_state"],
                allowed_aggregations=["AVG", "SUM/COUNT"],
            ),
            "late_delivery_rate": MetricDefinition(
                name="Late Delivery Rate",
                description="Percentage of completed customer orders delivered past the estimated delivery date.",
                domain="E-Commerce / Retail",
                dataset_id="ecommerce_olist",
                formula="(SUM(is_late_delivery) / COUNT(*)) * 100.0",
                dimensions=["customer_state", "order_year_month"],
                allowed_aggregations=["WEIGHTED_AVG"],
            ),
            "average_review_score": MetricDefinition(
                name="Average Customer Review Score",
                description="Mean customer satisfaction score on a 1-5 star scale.",
                domain="E-Commerce / Retail",
                dataset_id="ecommerce_olist",
                formula="AVG(review_score)",
                dimensions=["product_category_name_english", "review_creation_date"],
                allowed_aggregations=["AVG"],
            ),

            # --- URBAN TRANSPORTATION (NYC Taxi) ---
            "average_fare_by_hour": MetricDefinition(
                name="Average Trip Fare by Hour",
                description="Mean metered fare amount charged across pickup hours of the day.",
                domain="Urban Transportation",
                dataset_id="transportation_nyc_taxi",
                formula="AVG(total_amount)",
                dimensions=["pickup_hour", "pickup_day_of_week", "payment_type"],
                allowed_aggregations=["AVG"],
            ),
            "trip_demand_volume": MetricDefinition(
                name="Total Trip Demand Volume",
                description="Total number of completed taxi trips originating in a zone.",
                domain="Urban Transportation",
                dataset_id="transportation_nyc_taxi",
                formula="COUNT(trip_id)",
                dimensions=["pickup_location_id", "pickup_hour", "pickup_day_of_week"],
                allowed_aggregations=["COUNT"],
            ),
            "fare_per_mile": MetricDefinition(
                name="Average Fare per Mile",
                description="Revenue efficiency metric calculating average dollar fare per mile traveled.",
                domain="Urban Transportation",
                dataset_id="transportation_nyc_taxi",
                formula="SUM(fare_amount) / NULLIF(SUM(trip_distance_miles), 0)",
                dimensions=["pickup_location_id", "pickup_day_of_week"],
                allowed_aggregations=["RATIO"],
            ),

            # --- AIRLINE OPERATIONS (U.S. BTS) ---
            "on_time_arrival_rate": MetricDefinition(
                name="On-Time Arrival Rate",
                description="Percentage of scheduled flights that arrived within 14 minutes of schedule without cancellation.",
                domain="Airline Operations",
                dataset_id="airline_bts_ontime",
                formula="(SUM(is_arr_on_time) / COUNT(*)) * 100.0",
                dimensions=["carrier_code", "origin_airport", "dest_airport", "month"],
                allowed_aggregations=["WEIGHTED_SUM"],
                governance_rule="Must use weighted flight counts. Do NOT average airline-level percentages directly.",
            ),
            "cancellation_rate": MetricDefinition(
                name="Flight Cancellation Rate",
                description="Percentage of scheduled commercial flights canceled prior to completion.",
                domain="Airline Operations",
                dataset_id="airline_bts_ontime",
                formula="(SUM(cancelled) / COUNT(*)) * 100.0",
                dimensions=["carrier_code", "origin_airport", "cancellation_reason", "month"],
                allowed_aggregations=["WEIGHTED_SUM"],
            ),
            "average_arrival_delay": MetricDefinition(
                name="Average Arrival Delay Minutes",
                description="Mean arrival delay in minutes for completed flights.",
                domain="Airline Operations",
                dataset_id="airline_bts_ontime",
                formula="AVG(arrival_delay_minutes)",
                dimensions=["carrier_code", "origin_airport", "dest_airport"],
                allowed_aggregations=["AVG"],
            ),

            # --- HEALTHCARE (MIMIC-IV) ---
            "icu_length_of_stay_avg": MetricDefinition(
                name="Average ICU Length of Stay (LOS)",
                description="Mean duration of stay in intensive care units measured in days.",
                domain="Healthcare Operations",
                dataset_id="healthcare_mimic_iv",
                formula="AVG(icu_los_days)",
                dimensions=["first_careunit", "admission_type"],
                allowed_aggregations=["AVG"],
                governance_rule="Clinical operations metric only. NOT a diagnostic or medical decision system.",
            ),
            "hospital_admission_volume": MetricDefinition(
                name="Total Hospital Admission Volume",
                description="Count of patient hospital admissions by category and insurance.",
                domain="Healthcare Operations",
                dataset_id="healthcare_mimic_iv",
                formula="COUNT(hadm_id)",
                dimensions=["admission_type", "insurance", "admission_year"],
                allowed_aggregations=["COUNT"],
            ),

            # --- PUBLIC SAFETY (City of Chicago) ---
            "reported_incident_frequency": MetricDefinition(
                name="Reported Incident Frequency",
                description="Total count of municipal police reported crime incidents.",
                domain="Public Safety",
                dataset_id="safety_chicago_crimes",
                formula="COUNT(case_number)",
                dimensions=["primary_type", "district", "year_month", "day_of_week"],
                allowed_aggregations=["COUNT"],
                governance_rule="Represents reported municipal incidents only. No demographic or individual profiling claims.",
            ),
            "arrest_rate_pct": MetricDefinition(
                name="Incident Arrest Rate Percentage",
                description="Percentage of reported crime incidents resulting in an arrest.",
                domain="Public Safety",
                dataset_id="safety_chicago_crimes",
                formula="(SUM(arrest) / COUNT(*)) * 100.0",
                dimensions=["primary_type", "district", "year"],
                allowed_aggregations=["WEIGHTED_SUM"],
            ),

            # --- FINANCIAL MARKETS (SEC EDGAR) ---
            "trading_volume_daily": MetricDefinition(
                name="Average Daily Trading Volume",
                description="Average number of shares traded per session.",
                domain="Financial Markets",
                dataset_id="financial_sec_markets",
                formula="AVG(volume)",
                dimensions=["ticker", "year_month"],
                allowed_aggregations=["AVG"],
                governance_rule="Research demonstration only. Does NOT provide personalized investment advice.",
            ),
            "realized_volatility_30d": MetricDefinition(
                name="30-Day Realized Price Volatility",
                description="Standard deviation of daily percentage price returns over a rolling 30-day window.",
                domain="Financial Markets",
                dataset_id="financial_sec_markets",
                formula="AVG(volatility_30d)",
                dimensions=["ticker", "sector"],
                allowed_aggregations=["AVG"],
            ),
            "sec_reported_revenue": MetricDefinition(
                name="SEC Reported Corporate Revenue",
                description="Quarterly total revenue reported in official SEC Form 10-Q/10-K filings.",
                domain="Financial Markets",
                dataset_id="financial_sec_markets",
                formula="SUM(revenue_mil_usd)",
                dimensions=["ticker", "fiscal_period", "form_type"],
                allowed_aggregations=["SUM"],
            ),
        }

    def list_metrics(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [m.model_dump() for m in self.metrics.values()]

    def get_metric(self, name: str) -> Optional[MetricDefinition]:
        return self.metrics.get(name)


semantic_layer = SemanticLayer()
