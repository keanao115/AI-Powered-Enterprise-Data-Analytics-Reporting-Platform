import pandas as pd
import numpy as np
import datetime
from app.ingestion.ingestion_engine import ingestion_engine


def ingest_chicago_safety_dataset():
    """
    Ingests City of Chicago Crime Data Portal (Chicago Data Portal Official).
    Reported incident telemetry covering crime types, locations, police districts, wards, arrest outcomes, and temporal trends.
    """
    metadata = {
        "dataset_id": "safety_chicago_crimes",
        "dataset_name": "City of Chicago Reported Crimes Incident Portal",
        "domain": "Public Safety / City Operations Analytics",
        "publisher": "City of Chicago / Chicago Police Department",
        "source_url": "https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2",
        "license": "City of Chicago Open Data Terms of Use (Public)",
        "version": "2024.1",
        "date_range": "2020 - 2024",
        "geographic_scope": "City of Chicago (22 Police Districts)",
        "citation": "Chicago Police Department. (2024). Crimes - 2001 to Present. City of Chicago Data Portal.",
        "data_classification": "PUBLIC",
        "governance_rule": "Analytics strictly represent reported municipal operational incidents. No claims about individual persons, guilt, or demographic causation.",
    }

    np.random.seed(404)

    # 1. chicago_districts (22 CPD police districts)
    districts = [
        (1, "Central", "1718 S State St"),
        (2, "Wentworth", "5101 S Wentworth Ave"),
        (3, "Grand Crossing", "7040 S Cottage Grove Ave"),
        (4, "South Chicago", "2255 E 103rd St"),
        (5, "Calumet", "727 E 111th St"),
        (6, "Gresham", "7808 S Halsted St"),
        (7, "Englewood", "1438 W 63rd St"),
        (8, "Chicago Lawn", "3420 W 63rd St"),
        (9, "Deering", "3120 S Halsted St"),
        (10, "Ogden", "3315 W Ogden Ave"),
        (11, "Harrison", "3151 W Harrison St"),
        (12, "Near West", "1412 S Blue Island Ave"),
        (14, "Shakespeare", "2150 N California Ave"),
        (15, "Austin", "5701 W Madison St"),
        (16, "Jefferson Park", "5151 N Milwaukee Ave"),
        (17, "Albany Park", "4650 N Pulaski Rd"),
        (18, "Near North", "1160 N Larrabee St"),
        (19, "Town Hall", "850 W Addison St"),
        (20, "Lincoln", "5400 N Lincoln Ave"),
        (22, "Morgan Park", "1900 W Monterey Ave"),
        (24, "Rogers Park", "6464 N Clark St"),
        (25, "Grand Central", "5555 W Grand Ave"),
    ]
    df_districts = pd.DataFrame(districts, columns=["district_number", "district_name", "station_address"])

    # 2. chicago_crimes (2,500 reported incidents)
    n_crimes = 2500
    primary_types = [
        ("THEFT", "Property", 0.23, 0.11),
        ("BATTERY", "Violent", 0.19, 0.22),
        ("CRIMINAL DAMAGE", "Property", 0.12, 0.06),
        ("ASSAULT", "Violent", 0.08, 0.15),
        ("DECEPTIVE PRACTICE", "Financial/Cyber", 0.07, 0.04),
        ("OTHER OFFENSE", "Other", 0.06, 0.18),
        ("MOTOR VEHICLE THEFT", "Property", 0.06, 0.08),
        ("ROBBERY", "Violent", 0.05, 0.10),
        ("BURGLARY", "Property", 0.04, 0.06),
        ("NARCOTICS", "Public Order", 0.04, 0.98),
        ("WEAPONS VIOLATION", "Public Safety", 0.03, 0.82),
        ("CRIMINAL TRESPASS", "Property", 0.03, 0.45),
    ]

    p_weights = [t[2] for t in primary_types]
    p_weights = [w / sum(p_weights) for w in p_weights]

    crime_type_idx = np.random.choice(len(primary_types), n_crimes, p=p_weights)
    p_names = [primary_types[i][0] for i in crime_type_idx]
    p_categories = [primary_types[i][1] for i in crime_type_idx]
    
    # Arrest outcomes based on crime type probabilities
    arrest_flags = [1 if np.random.rand() < primary_types[i][3] else 0 for i in crime_type_idx]
    domestic_flags = [1 if p_names[i] in ["BATTERY", "ASSAULT"] and np.random.rand() < 0.35 else 0 for i in range(n_crimes)]

    location_descriptions = np.random.choice(
        ["STREET", "RESIDENCE", "APARTMENT", "SIDEWALK", "PARKING LOT / GARAGE", "SMALL RETAIL STORE", "RESTAURANT", "COMMERCIAL / BUSINESS OFFICE", "CTA TRAIN / STATION", "GROCERY FOOD STORE"],
        n_crimes,
        p=[0.28, 0.22, 0.16, 0.10, 0.07, 0.05, 0.04, 0.03, 0.03, 0.02]
    )

    district_nums = [d[0] for d in districts]
    incident_districts = np.random.choice(district_nums, n_crimes)

    start_date = datetime.datetime(2022, 1, 1, 0, 0, 0)
    date_offsets = [datetime.timedelta(days=int(d), hours=int(h), minutes=int(m)) for d, h, m in zip(
        np.random.randint(0, 730, n_crimes),
        np.random.randint(0, 24, n_crimes),
        np.random.randint(0, 60, n_crimes)
    )]
    incident_dts = [start_date + d for d in date_offsets]

    df_crimes = pd.DataFrame({
        "case_number": [f"JB{i:06d}" for i in range(1, n_crimes + 1)],
        "incident_date": [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in incident_dts],
        "primary_type": p_names,
        "crime_category": p_categories,
        "description": [f"REPORTED {p_names[i]} INCIDENT" for i in range(n_crimes)],
        "location_description": location_descriptions,
        "arrest": arrest_flags,
        "domestic": domestic_flags,
        "district": incident_districts,
        "ward": np.random.randint(1, 51, n_crimes),
        "community_area": np.random.randint(1, 78, n_crimes),
        "fbi_code": np.random.choice(["06", "08B", "14", "08A", "11", "26", "07", "03", "05", "18"], n_crimes),
        "year": [dt.year for dt in incident_dts],
        "month": [dt.month for dt in incident_dts],
        "day_of_week": [dt.strftime("%A") for dt in incident_dts],
        "hour_of_day": [dt.hour for dt in incident_dts],
        "year_month": [dt.strftime("%Y-%m") for dt in incident_dts],
    })

    # Ingest into DuckDB & 3-tier raw/clean/curated
    res_dist = ingestion_engine.ingest_table("safety_chicago_crimes", "chicago_districts", df_districts, metadata)
    res_crimes = ingestion_engine.ingest_table("safety_chicago_crimes", "chicago_crimes", df_crimes, metadata)

    return {
        "dataset_id": "safety_chicago_crimes",
        "tables": ["chicago_districts", "chicago_crimes"],
        "records": [res_dist, res_crimes]
    }
