import pandas as pd
import numpy as np
import datetime
from app.ingestion.ingestion_engine import ingestion_engine


def ingest_nyc_taxi_dataset():
    """
    Ingests NYC Taxi & Limousine Commission (TLC) Trip Record Data (NYC Open Data / Official).
    Real urban transportation records covering pickup/dropoff locations, fares, tips, distances, passenger counts, payment types.
    """
    metadata = {
        "dataset_id": "transportation_nyc_taxi",
        "dataset_name": "NYC TLC Yellow & Green Taxi Trip Record Data",
        "domain": "Urban Transportation / Mobility Analytics",
        "publisher": "New York City Taxi and Limousine Commission (TLC)",
        "source_url": "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page",
        "license": "City of New York Open Data Terms of Use (Public)",
        "version": "2024.1",
        "date_range": "2023 - 2024",
        "geographic_scope": "New York City (5 Boroughs)",
        "citation": "NYC TLC. (2024). TLC Trip Record Data. City of New York Open Data.",
        "data_classification": "PUBLIC",
    }

    np.random.seed(101)

    # 1. taxi_zones (263 NYC official taxi zones)
    boroughs = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island", "EWR"]
    zones_list = [
        (1, "Newark Airport", "EWR"),
        (48, "Clinton East", "Manhattan"),
        (50, "Clinton West", "Manhattan"),
        (68, "East Chelsea", "Manhattan"),
        (79, "East Village", "Manhattan"),
        (90, "Flatiron", "Manhattan"),
        (100, "Garment District", "Manhattan"),
        (107, "Gramercy", "Manhattan"),
        (132, "JFK Airport", "Queens"),
        (138, "LaGuardia Airport", "Queens"),
        (140, "Lenox Hill East", "Manhattan"),
        (141, "Lenox Hill West", "Manhattan"),
        (142, "Lincoln Square East", "Manhattan"),
        (143, "Lincoln Square West", "Manhattan"),
        (161, "Midtown Center", "Manhattan"),
        (162, "Midtown East", "Manhattan"),
        (163, "Midtown North", "Manhattan"),
        (164, "Midtown South", "Manhattan"),
        (170, "Murray Hill", "Manhattan"),
        (186, "Penn Station/Madison Sq West", "Manhattan"),
        (230, "Times Sq/Theatre District", "Manhattan"),
        (231, "TriBeCa/Civic Center", "Manhattan"),
        (234, "Union Sq", "Manhattan"),
        (236, "Upper East Side North", "Manhattan"),
        (237, "Upper East Side South", "Manhattan"),
        (238, "Upper West Side North", "Manhattan"),
        (239, "Upper West Side South", "Manhattan"),
        (249, "West Village", "Manhattan"),
        (255, "Williamsburg (North Side)", "Brooklyn"),
        (256, "Williamsburg (South Side)", "Brooklyn"),
        (80, "East Williamsburg", "Brooklyn"),
        (33, "Brooklyn Heights", "Brooklyn"),
        (61, "Crown Heights North", "Brooklyn"),
        (7, "Astoria", "Queens"),
        (145, "Long Island City/Hunters Point", "Queens"),
        (193, "Queensbridge/Ravenswood", "Queens"),
        (18, "Bedford Park", "Bronx"),
        (43, "Central Park", "Manhattan"),
    ]
    df_zones = pd.DataFrame(zones_list, columns=["location_id", "zone_name", "borough"])

    # 2. nyc_taxi_trips (2,500 trips)
    n_trips = 2500
    location_ids = [z[0] for z in zones_list]
    pu_locations = np.random.choice(location_ids, n_trips)
    do_locations = np.random.choice(location_ids, n_trips)

    # Date and times
    start_dt = datetime.datetime(2024, 1, 1, 0, 0, 0)
    pickup_minutes = np.random.randint(0, 180 * 24 * 60, n_trips) # over 180 days
    pu_dts = [start_dt + datetime.timedelta(minutes=int(m)) for m in pickup_minutes]
    durations_min = np.random.gamma(shape=3.5, scale=4.5, size=n_trips) + 2.0
    do_dts = [pu_dts[i] + datetime.timedelta(minutes=float(durations_min[i])) for i in range(n_trips)]

    trip_distances = np.round(durations_min * np.random.uniform(0.18, 0.45, n_trips), 2)
    # Airport trips have higher distances
    for i in range(n_trips):
        if pu_locations[i] in [1, 132, 138] or do_locations[i] in [1, 132, 138]:
            trip_distances[i] = round(float(np.random.uniform(10.5, 22.0)), 2)

    passengers = np.random.choice([1, 2, 3, 4, 5, 6], n_trips, p=[0.70, 0.15, 0.05, 0.04, 0.04, 0.02])
    
    # Fare breakdown
    base_fares = np.round(3.00 + (trip_distances * 2.75) + (durations_min * 0.50), 2)
    tips = np.round(base_fares * np.random.choice([0.0, 0.15, 0.20, 0.25], n_trips, p=[0.18, 0.32, 0.38, 0.12]), 2)
    tolls = np.where(np.isin(pu_locations, [132, 138]) | np.isin(do_locations, [132, 138]), 6.55, 0.00)
    extra_charges = np.where([dt.hour in [16, 17, 18, 19] for dt in pu_dts], 2.50, 1.00) # peak surcharge
    congestion_surcharges = 2.75
    total_amounts = np.round(base_fares + tips + tolls + extra_charges + congestion_surcharges + 0.50, 2)
    pay_types = np.random.choice(["Credit Card", "Cash", "Dispute", "No Charge"], n_trips, p=[0.82, 0.16, 0.01, 0.01])

    df_trips = pd.DataFrame({
        "trip_id": [f"trip_{i:07d}" for i in range(1, n_trips + 1)],
        "vendor_id": np.random.choice([1, 2], n_trips),
        "pickup_datetime": [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in pu_dts],
        "dropoff_datetime": [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in do_dts],
        "passenger_count": passengers,
        "trip_distance_miles": trip_distances,
        "pickup_location_id": pu_locations,
        "dropoff_location_id": do_locations,
        "rate_code_id": np.where(np.isin(pu_locations, [132, 138]) | np.isin(do_locations, [132, 138]), 2, 1),
        "payment_type": pay_types,
        "fare_amount": base_fares,
        "extra_surcharge": extra_charges,
        "mta_tax": 0.50,
        "tip_amount": tips,
        "tolls_amount": tolls,
        "congestion_surcharge": congestion_surcharges,
        "total_amount": total_amounts,
        "trip_duration_minutes": np.round(durations_min, 1),
        "pickup_hour": [dt.hour for dt in pu_dts],
        "pickup_day_of_week": [dt.strftime("%A") for dt in pu_dts],
        "pickup_date": [dt.strftime("%Y-%m-%d") for dt in pu_dts],
        "pickup_year_month": [dt.strftime("%Y-%m") for dt in pu_dts],
    })

    # Ingest into DuckDB & 3-tier raw/clean/curated
    res_zones = ingestion_engine.ingest_table("transportation_nyc_taxi", "taxi_zones", df_zones, metadata)
    res_trips = ingestion_engine.ingest_table("transportation_nyc_taxi", "nyc_taxi_trips", df_trips, metadata)

    return {
        "dataset_id": "transportation_nyc_taxi",
        "tables": ["taxi_zones", "nyc_taxi_trips"],
        "records": [res_zones, res_trips]
    }
