# NYC Housing Violations Dashboard

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Holding landlords accountable through data transparency**

An interactive data analysis platform that exposes patterns of housing code violations across New York City, identifies repeat offenders, and reveals enforcement gaps in affordable housing protection. Built to empower tenant advocacy and inform policy decisions.

---

## 🎯 Project Overview

### The Problem

In New York City, thousands of tenants live in buildings with serious housing code violations—lack of heat, broken plumbing, pest infestations, and more. While data on these violations is publicly available through NYC Open Data, it remains fragmented and difficult to interpret, making it challenging for tenants, advocates, and policymakers to identify patterns of landlord negligence and enforcement failures.

### The Solution

This project transforms raw housing violation data into actionable insights by:

- **Identifying repeat offenders**: Tracking landlords and buildings with persistent violation patterns
- **Revealing enforcement gaps**: Analyzing complaint response times and inspection rates across neighborhoods
- **Geospatial analysis**: Mapping violation hotspots to identify areas of concentrated housing injustice
- **Temporal trend detection**: Uncovering seasonal patterns and long-term trends in housing conditions
- **Predictive risk modeling**: Forecasting which buildings are most likely to accumulate future violations

### Social Impact

This tool serves as a public accountability mechanism, enabling:
- **Tenants** to research buildings before renting and document patterns of neglect
- **Tenant advocates** to identify priority cases and systemic issues
- **Journalists** to investigate landlord practices and enforcement failures
- **Policymakers** to target interventions and allocate enforcement resources
- **Legal advocates** to build cases against negligent property owners

---

## 📊 Key Features

### Data Analysis
- **Multi-source integration**: Combines HPD violations, complaints, building ownership, and demographic data
- **Geospatial clustering**: Hotspot analysis using Getis-Ord Gi* statistics
- **Time series analysis**: Seasonal decomposition and trend detection
- **Network analysis**: Linking corporate landlords across multiple properties
- **Statistical testing**: Identifies significant disparities in enforcement by neighborhood

### Interactive Dashboard
- **Building search**: Look up violation history by address
- **Interactive maps**: Visualize violations across NYC with filtering options
- **Temporal visualizations**: Track violation trends over time
- **Landlord rankings**: Identify worst offenders by violation count and severity
- **Neighborhood comparisons**: Analyze enforcement equity across communities

### API
- **RESTful endpoints**: Programmatic access to cleaned data and analysis results
- **Flexible filtering**: Query by date range, violation type, borough, and more
- **Aggregated statistics**: Pre-computed metrics for fast dashboard performance

---

## 🛠️ Technology Stack

### Data Pipeline & Analysis
- **Python 3.9+**: Core data processing
- **pandas & NumPy**: Data manipulation and numerical analysis
- **GeoPandas & Shapely**: Geospatial analysis and mapping
- **scikit-learn**: Machine learning models for risk prediction
- **statsmodels**: Statistical testing and time series analysis
- **sodapy**: NYC Open Data API integration

### Backend
- **FastAPI**: High-performance REST API
- **PostgreSQL + PostGIS**: Geospatial database
- **SQLAlchemy**: Database ORM

### Frontend *(Coming Soon)*
- **React + TypeScript**: Interactive web application
- **Recharts/Plotly**: Data visualization components
- **Leaflet/Mapbox**: Interactive mapping

### Development Tools
- **Jupyter**: Exploratory analysis and documentation
- **pytest**: Testing framework
- **black & isort**: Code formatting
- **GitHub Actions**: CI/CD *(Coming Soon)*

---

## 📁 Project Structure

```
nyc-housing-violations-dashboard/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/                    # Raw data from NYC Open Data (not tracked)
│   ├── processed/              # Cleaned and transformed data
│   └── README.md               # Data documentation and sources
├── notebooks/
│   └── exploratory_analysis.ipynb  # Initial data exploration
├── src/
│   ├── data_pipeline/          # ETL pipeline
│   │   ├── fetch_data.py       # Download data from NYC Open Data
│   │   ├── clean_data.py       # Data cleaning and validation
│   │   └── load_data.py        # Load to PostgreSQL
│   ├── analysis/               # Analytical modules
│   │   ├── temporal_analysis.py    # Time series analysis
│   │   ├── geospatial_analysis.py  # Spatial clustering & hotspots
│   │   └── repeat_offenders.py     # Landlord tracking
│   └── api/                    # FastAPI application
│       ├── main.py             # API entry point
│       └── routes/             # API route definitions
├── frontend/                   # React dashboard (coming soon)
├── tests/                      # Unit and integration tests
├── docs/                       # Additional documentation
│   └── methodology.md          # Detailed analysis methodology
└── config/
    └── config.yaml             # Configuration settings
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 14+ with PostGIS extension (for geospatial features)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/snedmagdous/nyc-housing-violations-dashboard.git
   cd nyc-housing-violations-dashboard
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create a .env file in the project root
   cp config/.env.example .env

   # Edit .env with your configuration
   # - PostgreSQL connection string
   # - NYC Open Data API token (optional, for higher rate limits)
   ```

5. **Initialize the database**
   ```bash
   python src/data_pipeline/setup_db.py
   ```

### Quick Start

#### 1. Fetch Data
```bash
python src/data_pipeline/fetch_data.py
```
Downloads the latest HPD violations data from NYC Open Data API.

#### 2. Clean and Process
```bash
python src/data_pipeline/clean_data.py
```
Cleans raw data, geocodes addresses, and prepares for analysis.

#### 3. Run Analysis
```bash
jupyter notebook notebooks/exploratory_analysis.ipynb
```
Explore the data and see initial findings.

#### 4. Start the API
```bash
uvicorn src.api.main:app --reload
```
Access API documentation at `http://localhost:8000/docs`

---

## 📈 Analysis Methodology

### Data Sources

1. **HPD Housing Maintenance Code Violations**
   - Source: NYC Open Data
   - Records: 1.5M+ violations (2018-present)
   - Contains: Violation type, severity class, dates, addresses, status

2. **HPD Complaints**
   - Tenant-reported issues
   - Used to identify enforcement gaps

3. **PLUTO (Primary Land Use Tax Lot Output)**
   - Building characteristics and ownership
   - Enables demographic analysis

4. **NYC Borough Boundaries & Census Tracts**
   - For geospatial analysis and demographic overlays

### Key Analyses

#### 1. Temporal Pattern Detection
- **Seasonal decomposition**: Identifies recurring patterns (e.g., heating violations spike in winter)
- **Trend analysis**: Long-term changes in violation rates
- **Enforcement lag calculation**: Time from complaint to inspection to resolution

#### 2. Geospatial Clustering
- **Hotspot analysis**: Getis-Ord Gi* statistic identifies areas with significantly high violation concentrations
- **Spatial autocorrelation**: Moran's I test for neighborhood effects
- **Demographic overlay**: Correlates violation patterns with income, race, and other census data

#### 3. Repeat Offender Identification
- **Ownership network analysis**: Connects properties owned by the same entity across different LLCs
- **Violation rate normalization**: Accounts for building size and age
- **Ranking algorithm**: Weights by violation severity (Class A/B/C)

#### 4. Enforcement Equity Analysis
- **Response time analysis**: Compares complaint-to-inspection times across neighborhoods
- **Inspection rate disparities**: Tests for statistical significance in enforcement patterns
- **Demographic correlation**: Examines relationship between neighborhood demographics and enforcement activity

#### 5. Predictive Risk Modeling *(In Development)*
- **Features**: Building age, past violations, ownership type, neighborhood characteristics
- **Model**: Random Forest classifier for binary prediction (high-risk vs. low-risk)
- **Output**: Risk scores for proactive intervention targeting

---

## 📊 Key Findings *(Example - To Be Updated)*

> **Note**: These are placeholder findings. Actual results will be added after initial data analysis.

1. **Enforcement gaps are widest in [specific neighborhoods]**
   - Average complaint response time: X days in [neighborhood A] vs. Y days in [neighborhood B]

2. **Top 10 landlords account for Z% of Class C violations**
   - Corporate ownership associated with higher violation rates than individual owners

3. **Seasonal patterns reveal predictable failure points**
   - Heating violations spike 300% in winter months
   - Suggests need for proactive inspections before heating season

4. **[X]% of complaints never result in inspections**
   - Identifies systemic breakdown in enforcement pipeline

---

## 🤝 Contributing

This is currently a portfolio project, but suggestions and feedback are welcome! If you're interested in:
- Extending the analysis
- Improving the visualization
- Adding new data sources
- Deploying for public use

Please open an issue or reach out directly.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Maya Murry**
- Cornell University, B.Sc. Computer Science (May 2025)
- Lead Full-Stack Developer at an AI Healthcare Startup
- Focus: Data science for social justice and public service

**Contact**: hello@mayamurry.com
**Portfolio**: [mayamurry.com](https://mayamurry.com)
**LinkedIn**: [linkedin.com/in/maya-murry](https://www.linkedin.com/in/maya-murry)
**GitHub**: [@snedmagdous](https://github.com/snedmagdous)

---

## 🙏 Acknowledgments

- **NYC Open Data**: For making housing violations data publicly accessible
- **Tenant advocacy organizations**: For inspiration and guidance on policy priorities
- **Open source community**: For the excellent tools that made this analysis possible

---

## 📚 Related Resources

- [NYC Housing Preservation & Development](https://www.nyc.gov/site/hpd/index.page)
- [NYC Open Data Portal](https://opendata.cityofnewyork.us/)
- [Right to Counsel NYC](https://www.righttocounselnyc.org/)
- [Housing Justice for All](https://housingjusticeforall.org/)

---

## 🔍 Project Status

**Current Phase**: Data Pipeline Development

- [x] Project setup and structure
- [x] Requirements and dependencies defined
- [ ] Data fetching from NYC Open Data
- [ ] Data cleaning and preprocessing
- [ ] Exploratory data analysis
- [ ] Geospatial analysis implementation
- [ ] API development
- [ ] Frontend dashboard
- [ ] Deployment

---

*This project uses data-driven analysis to advance housing justice in New York City. Technology should serve the collective, dismantle systems of oppression, and empower those fighting for their rights.*
