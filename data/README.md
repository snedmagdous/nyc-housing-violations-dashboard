# Data Directory

This directory contains housing violations data from NYC Open Data.

## Structure

```
data/
├── raw/              # Raw data downloaded from NYC Open Data (not tracked in git)
│   ├── hpd_violations.csv
│   ├── hpd_complaints.csv
│   └── pluto_data.csv
└── processed/        # Cleaned and transformed data (not tracked in git)
    └── violations_cleaned.csv
```

## Data Sources

### 1. HPD Housing Maintenance Code Violations
- **Dataset ID**: `wvxf-dwi5`
- **URL**: https://data.cityofnewyork.us/Housing-Development/Housing-Maintenance-Code-Violations/wvxf-dwi5
- **Description**: Violations issued by HPD inspectors for issues like lack of heat, broken plumbing, pests, etc.
- **Update Frequency**: Daily
- **Key Fields**:
  - `violationid`: Unique identifier
  - `buildingid`: Building identifier
  - `inspectiondate`: Date of inspection
  - `violationclass`: Severity (A=non-hazardous, B=hazardous, C=immediately hazardous)
  - `violationstatus`: Current status (Open, Closed, etc.)
  - `borough`, `housenumber`, `streetname`, `apartment`, `zip`

### 2. HPD Complaints
- **Dataset ID**: `uwyv-629c`
- **URL**: https://data.cityofnewyork.us/Housing-Development/Housing-Maintenance-Code-Complaints/uwyv-629c
- **Description**: Tenant-reported complaints to HPD
- **Purpose**: Identify enforcement gaps (complaints without violations)

### 3. PLUTO (Primary Land Use Tax Lot Output)
- **Dataset ID**: `64uk-42ks`
- **URL**: https://data.cityofnewyork.us/City-Government/Primary-Land-Use-Tax-Lot-Output-PLUTO/64uk-42ks
- **Description**: Building characteristics and ownership information
- **Purpose**: Enrich violation data with building metadata

## Downloading Data

Use the data pipeline scripts:

```bash
# Fetch violations data
python src/data_pipeline/fetch_data.py

# Clean data
python src/data_pipeline/clean_data.py

# Load to database
python src/data_pipeline/load_data.py
```

## Notes

- Raw and processed data files are **not tracked in git** (too large)
- Only data documentation is version-controlled
- First-time setup: Run `fetch_data.py` to download initial datasets
- Data is cached locally to minimize API calls

## Data Privacy

This project uses only publicly available data from NYC Open Data. No personally identifiable information (PII) is collected or stored.
