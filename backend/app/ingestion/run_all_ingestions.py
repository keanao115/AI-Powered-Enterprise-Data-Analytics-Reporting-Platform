import time
from typing import Dict, Any, List
from app.ingestion.datasets.olist_ecommerce import ingest_olist_ecommerce_dataset
from app.ingestion.datasets.nyc_taxi import ingest_nyc_taxi_dataset
from app.ingestion.datasets.bts_airlines import ingest_bts_airlines_dataset
from app.ingestion.datasets.mimic_healthcare import ingest_mimic_healthcare_dataset
from app.ingestion.datasets.chicago_safety import ingest_chicago_safety_dataset
from app.ingestion.datasets.sec_financial import ingest_sec_financial_dataset
from app.ingestion.ingestion_engine import ingestion_engine


def run_full_enterprise_ingestion_pipeline() -> Dict[str, Any]:
    """
    Executes the complete production-grade ingestion pipeline for all 6 public enterprise datasets.
    Stores raw files, cleans/normalizes data into parquet, creates DuckDB analytical tables,
    and calculates 5-dimension Data Quality scores.
    """
    start_time = time.time()
    results = {}

    print("--- Starting Production-Grade Enterprise Data Ingestion ---")
    
    # 1. E-Commerce (Olist)
    print("Ingesting [01/06] Brazilian E-Commerce Public Dataset by Olist...")
    results["ecommerce_olist"] = ingest_olist_ecommerce_dataset()

    # 2. Urban Transportation (NYC TLC)
    print("Ingesting [02/06] NYC TLC Taxi Trip Record Dataset...")
    results["transportation_nyc_taxi"] = ingest_nyc_taxi_dataset()

    # 3. Airline Operations (U.S. BTS)
    print("Ingesting [03/06] U.S. BTS Airline On-Time Performance Dataset...")
    results["airline_bts_ontime"] = ingest_bts_airlines_dataset()

    # 4. Healthcare (MIMIC-IV)
    print("Ingesting [04/06] PhysioNet MIMIC-IV Clinical Database Demo...")
    results["healthcare_mimic_iv"] = ingest_mimic_healthcare_dataset()

    # 5. Public Safety (City of Chicago)
    print("Ingesting [05/06] City of Chicago Reported Crimes Portal...")
    results["safety_chicago_crimes"] = ingest_chicago_safety_dataset()

    # 6. Financial Markets (SEC EDGAR)
    print("Ingesting [06/06] U.S. Public Financial Markets & SEC EDGAR Dataset...")
    results["financial_sec_markets"] = ingest_sec_financial_dataset()

    total_duration = round(time.time() - start_time, 2)
    print(f"--- Completed All 6 Dataset Ingestions in {total_duration}s ---")

    return {
        "status": "COMPLETED",
        "total_datasets": len(results),
        "duration_seconds": total_duration,
        "results": results,
    }


if __name__ == "__main__":
    run_full_enterprise_ingestion_pipeline()
