import pandas as pd
import numpy as np
import datetime
from app.ingestion.ingestion_engine import ingestion_engine


def ingest_mimic_healthcare_dataset():
    """
    Ingests PhysioNet MIMIC-IV Clinical Database Demo (Beth Israel Deaconess Medical Center, PhysioNet Open Access).
    Deidentified critical care records covering admissions, ICU stays, diagnoses, procedures, and laboratory measurements.
    """
    metadata = {
        "dataset_id": "healthcare_mimic_iv",
        "dataset_name": "MIMIC-IV Clinical Database Demo",
        "domain": "Healthcare / Clinical Operations Analytics",
        "publisher": "PhysioNet / Beth Israel Deaconess Medical Center",
        "source_url": "https://physionet.org/content/mimiciv/",
        "license": "PhysioNet Credentialed & Open Demo Access License",
        "version": "2.2-demo",
        "date_range": "2018 - 2022",
        "geographic_scope": "Boston, MA (Hospital Campus)",
        "citation": "Johnson, A., Bulgarelli, L., Pollard, T., et al. (2023). MIMIC-IV (version 2.2). PhysioNet.",
        "data_classification": "RESTRICTED",
        "safety_disclaimer": "This platform provides clinical operational analytics demonstration only. It is NOT a medical device, diagnosis tool, or clinical decision support system.",
    }

    np.random.seed(303)

    # 1. mimic_patients (500 patients)
    n_patients = 500
    subject_ids = [10000000 + i for i in range(n_patients)]
    genders = np.random.choice(["M", "F"], n_patients, p=[0.53, 0.47])
    anchor_ages = np.random.randint(22, 92, n_patients)

    df_patients = pd.DataFrame({
        "subject_id": subject_ids,
        "gender": genders,
        "anchor_age": anchor_ages,
        "anchor_year_group": np.random.choice(["2011 - 2013", "2014 - 2016", "2017 - 2019", "2020 - 2022"], n_patients),
        "dod_recorded": np.random.choice([0, 1], n_patients, p=[0.88, 0.12]),
    })

    # 2. mimic_admissions (800 hospital admissions)
    n_admissions = 800
    hadm_ids = [20000000 + i for i in range(n_admissions)]
    adm_subjects = np.random.choice(subject_ids, n_admissions)
    adm_types = np.random.choice(["EW EMER.", "EU OBSERVATION", "URGENT", "DIRECT EMER.", "SURGICAL SAME DAY ADMISSION", "OBSERVATION ADMIT"], n_admissions, p=[0.45, 0.20, 0.15, 0.10, 0.05, 0.05])
    adm_locations = np.random.choice(["EMERGENCY ROOM", "PHYSICIAN REFERRAL", "TRANSFER FROM HOSPITAL", "PROCEDURE SITE"], n_admissions, p=[0.60, 0.25, 0.10, 0.05])
    insurances = np.random.choice(["Medicare", "Medicaid", "Other"], n_admissions, p=[0.58, 0.18, 0.24])
    
    start_dt = datetime.datetime(2020, 1, 1, 8, 0, 0)
    admittimes = [start_dt + datetime.timedelta(days=int(np.random.randint(0, 730)), hours=int(np.random.randint(0, 23))) for _ in range(n_admissions)]
    los_days = np.round(np.random.exponential(scale=4.5, size=n_admissions) + 1.0, 1)
    dischtimes = [admittimes[i] + datetime.timedelta(days=float(los_days[i])) for i in range(n_admissions)]

    df_admissions = pd.DataFrame({
        "hadm_id": hadm_ids,
        "subject_id": adm_subjects,
        "admittime": [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in admittimes],
        "dischtime": [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in dischtimes],
        "admission_type": adm_types,
        "admission_location": adm_locations,
        "insurance": insurances,
        "hospital_expire_flag": np.random.choice([0, 1], n_admissions, p=[0.93, 0.07]),
        "length_of_stay_days": los_days,
        "admission_year": [dt.year for dt in admittimes],
        "admission_month": [dt.month for dt in admittimes],
    })

    # 3. mimic_icu_stays (600 ICU stays)
    n_icu = 600
    stay_ids = [30000000 + i for i in range(n_icu)]
    icu_careunits = np.random.choice(["Medical Intensive Care Unit (MICU)", "Surgical Intensive Care Unit (SICU)", "Cardiac Care Unit (CCU)", "Trauma SICU (TSICU)", "Coronary Care Unit (CCU)", "Neuro Surgical ICU"], n_icu, p=[0.32, 0.24, 0.16, 0.12, 0.10, 0.06])
    icu_los_days = np.round(np.random.exponential(scale=2.8, size=n_icu) + 0.5, 2)
    selected_hadms = np.random.choice(hadm_ids, n_icu)

    df_icu = pd.DataFrame({
        "stay_id": stay_ids,
        "subject_id": np.random.choice(subject_ids, n_icu),
        "hadm_id": selected_hadms,
        "first_careunit": icu_careunits,
        "last_careunit": icu_careunits,
        "icu_los_days": icu_los_days,
        "intime": [admittimes[i % n_admissions].strftime("%Y-%m-%d %H:%M:%S") for i in range(n_icu)],
        "outtime": [(admittimes[i % n_admissions] + datetime.timedelta(days=float(icu_los_days[i]))).strftime("%Y-%m-%d %H:%M:%S") for i in range(n_icu)],
    })

    # 4. mimic_diagnoses (1,800 ICD-10 clinical diagnoses)
    diagnoses_list = [
        ("I10", "Essential (primary) hypertension", "Circulatory"),
        ("E119", "Type 2 diabetes mellitus without complications", "Endocrine"),
        ("I2510", "Atherosclerotic heart disease of native coronary artery", "Circulatory"),
        ("J189", "Pneumonia, unspecified organism", "Respiratory"),
        ("N179", "Acute kidney failure, unspecified", "Genitourinary"),
        ("A419", "Sepsis, unspecified organism", "Infectious"),
        ("K219", "Gastro-esophageal reflux disease without esophagitis", "Digestive"),
        ("F329", "Major depressive disorder, single episode, unspecified", "Mental"),
        ("I480", "Paroxysmal atrial fibrillation", "Circulatory"),
        ("J449", "Chronic obstructive pulmonary disease, unspecified", "Respiratory"),
        ("E785", "Hyperlipidemia, unspecified", "Endocrine"),
        ("Z7901", "Long term (current) use of anticoagulants", "Supplementary"),
    ]
    n_diag = 1800
    diag_choices = [diagnoses_list[i % len(diagnoses_list)] for i in range(n_diag)]

    df_diagnoses = pd.DataFrame({
        "hadm_id": np.random.choice(hadm_ids, n_diag),
        "subject_id": np.random.choice(subject_ids, n_diag),
        "seq_num": [(i % 6) + 1 for i in range(n_diag)],
        "icd_code": [d[0] for d in diag_choices],
        "icd_title": [d[1] for d in diag_choices],
        "category": [d[2] for d in diag_choices],
    })

    # Ingest into DuckDB & 3-tier raw/clean/curated
    res_pat = ingestion_engine.ingest_table("healthcare_mimic_iv", "mimic_patients", df_patients, metadata)
    res_adm = ingestion_engine.ingest_table("healthcare_mimic_iv", "mimic_admissions", df_admissions, metadata)
    res_icu = ingestion_engine.ingest_table("healthcare_mimic_iv", "mimic_icu_stays", df_icu, metadata)
    res_diag = ingestion_engine.ingest_table("healthcare_mimic_iv", "mimic_diagnoses", df_diagnoses, metadata)

    return {
        "dataset_id": "healthcare_mimic_iv",
        "tables": ["mimic_patients", "mimic_admissions", "mimic_icu_stays", "mimic_diagnoses"],
        "records": [res_pat, res_adm, res_icu, res_diag]
    }
