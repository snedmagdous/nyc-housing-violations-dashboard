# CODE SAMPLE COVER PAGE

**Candidate:** Maya Murry
**Position:** Data Scientist (Reference No. RAD_NYC_DAS_6412)
**GitHub Repository:** https://github.com/snedmagdous/nyc-housing-violations-dashboard

---

## PROJECT OVERVIEW: NYC HOUSING VIOLATIONS DASHBOARD

This project demonstrates my ability to acquire data from public sources, develop databases, perform exploratory data analysis, and create visualizations that make complex patterns accessible to non-technical audiences—skills directly relevant to OAG's Data Scientist role.

### PROBLEM STATEMENT

New York City's housing code violation data is publicly available through NYC Open Data, but the raw data is difficult for community organizations, tenants, and legal advocates to use effectively. Patterns of systematic landlord neglect and enforcement disparities remain hidden without proper analysis and visualization tools.

---

## APPROACH & METHODOLOGIES

### Data Acquisition & ETL
- Acquired housing code violation data from NYC Open Data API (10,000+ records across all five boroughs)
- Developed Python scripts using `requests` library to handle API pagination, rate limiting, and data extraction
- Implemented data cleaning pipelines using `pandas` to handle missing values, standardize addresses, and validate data integrity

### Database Development
- Designed PostgreSQL database schema optimized for geospatial queries and temporal analysis
- Created indexed tables for violations, buildings, and landlords with appropriate foreign key relationships
- Wrote advanced SQL queries to aggregate violations by building, landlord, neighborhood, and violation type

### Exploratory Data Analysis
- Conducted statistical analysis to identify geographic patterns and severity distributions
- Analyzed violation concentrations across NYC boroughs (Brooklyn: 59%, Bronx: 38%)
- Identified that 90% of violations are Class I (immediately hazardous), indicating critical safety concerns

### Data Visualization
- Built REST API using FastAPI enabling programmatic access to cleaned data
- Created interactive search interface using React + TypeScript for building violation lookups
- Designed system architecture to support future interactive dashboard development

---

## KEY FILES TO REVIEW

### /src/data_pipeline/ - **ETL Pipeline (PRIORITY FOR REVIEW)**
- **`fetch_data.py`** - Data acquisition from NYC Open Data API with error handling and pagination
- **`clean_data.py`** - Data cleaning pipeline using pandas: standardization, validation, transformation
- **`load_data.py`** - PostgreSQL database loading with batch processing and transaction management
- **`setup_db.py`** - Database schema creation with PostGIS for geospatial queries

### /sql_queries/ - **Advanced SQL Demonstrations**
- **`01_basic_queries.sql`** - Foundational aggregations and filtering
- **`02_window_functions.sql`** - Ranking, running totals, and time-series analysis
- **`03_cte_subqueries.sql`** - Complex query composition with Common Table Expressions
- **`04_geospatial_queries.sql`** - PostGIS operations for geographic analysis

### /notebooks/
- **`exploratory_analysis.ipynb`** - Statistical analysis with visualizations and findings

### /src/api/ - **REST API Architecture**
- **`main.py`** - FastAPI application with documented endpoints
- **`routes/`** - Modular endpoint organization (violations, buildings, analysis)
- **`database.py`** - SQLAlchemy ORM configuration and connection pooling

### /src/analysis/ - **Statistical Analysis Modules**
- **`temporal_analysis.py`** - Time series analysis and seasonal pattern detection
- **`geospatial_analysis.py`** - Hotspot identification and clustering algorithms
- **`predictive_model.py`** - Risk score calculation for proactive enforcement

---

## TECHNICAL SKILLS DEMONSTRATED

✓ **Programming:** Python (pandas, numpy, requests), SQL, TypeScript
✓ **Data Acquisition:** API integration, error handling, data validation
✓ **Database Development:** PostgreSQL schema design, indexing, query optimization
✓ **Statistical Analysis:** Descriptive statistics, pattern detection, outlier identification
✓ **Data Visualization:** REST API design, interactive web interfaces
✓ **Git/GitHub:** Version control, comprehensive README, documentation

---

## HOW THIS PROJECT DEMONSTRATES DATASET ANALYSIS

### 1. Data Acquisition & Validation
**File:** `src/data_pipeline/fetch_data.py`
- Connects to NYC Open Data API using `requests` library
- Implements pagination to handle large datasets (10,000+ records)
- Validates API responses and handles error cases
- **OAG Relevance:** Similar to acquiring financial data, real estate records, or consumer complaints for investigations

### 2. Data Cleaning & Transformation
**File:** `src/data_pipeline/clean_data.py`
- Uses `pandas` for data manipulation and cleaning
- Standardizes violation classes (A, B, C, I) with descriptions
- Handles missing values appropriately by field type
- Creates derived features (severity scores, temporal fields)
- **OAG Relevance:** Parallels cleaning messy datasets from various sources for litigation support

### 3. Statistical Analysis & Hypothesis Testing
**File:** `notebooks/exploratory_analysis.ipynb`
- Analyzes geographic distribution of violations (Brooklyn 59%, Bronx 38%)
- Examines severity distribution (90% Class I violations = critical safety issues)
- Identifies patterns requiring intervention (10% open violations)
- **OAG Relevance:** Similar to testing hypotheses about fraud patterns or enforcement disparities

### 4. Database Design & SQL Querying
**Files:** `sql_queries/*.sql`
- Window functions for ranking worst offender buildings
- CTEs for complex multi-step aggregations
- Geospatial queries for neighborhood analysis
- **OAG Relevance:** Demonstrates ability to structure and query complex legal/regulatory datasets

### 5. Communicating Findings
**Files:** `README.md`, API documentation
- Translates technical findings into actionable insights
- Documents methodology for reproducibility
- Creates accessible interfaces for non-technical stakeholders
- **OAG Relevance:** Essential for presenting data to attorneys, policymakers, and investigators

---

## RELEVANCE TO OAG DATA SCIENTIST ROLE

This project directly parallels OAG's work:

1. **Acquiring data from public sources** to support investigations (like OAG's lawsuit preserving affordable housing)
2. **Developing databases and analytical tools** to detect patterns of misconduct
3. **Testing data for reliability** and developing appropriate methodologies
4. **Communicating findings** through visualizations accessible to non-technical audiences (legal teams, advocates)
5. **Continuously updating analysis** as new data becomes available

The codebase demonstrates my ability to work independently on all aspects of a data science project—from initial data acquisition through database development to final visualization—while maintaining code quality, documentation, and reproducibility through Git/GitHub.

---

## INSTRUCTIONS FOR REVIEWERS

### To review the code:

1. Visit: **https://github.com/snedmagdous/nyc-housing-violations-dashboard**
2. Key files are organized in directories as described above
3. **README.md** provides setup instructions and project context
4. All code includes inline comments explaining methodology and design decisions

### To run the project locally:

```bash
# Clone repository
git clone https://github.com/snedmagdous/nyc-housing-violations-dashboard.git
cd nyc-housing-violations-dashboard

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup (requires PostgreSQL with PostGIS)
python src/data_pipeline/setup_db.py
python src/data_pipeline/fetch_data.py
python src/data_pipeline/clean_data.py
python src/data_pipeline/load_data.py

# Run API
python -m uvicorn src.api.main:app --reload
# Visit http://localhost:8000/docs for interactive API documentation
```

---

## PROJECT STATUS

**Current Status (November 2025):** Core ETL pipeline and exploratory analysis are complete. Interactive dashboard is in development.

**Completed Components:**
- ✅ Data acquisition from NYC Open Data API
- ✅ Data cleaning and transformation pipeline
- ✅ PostgreSQL database with PostGIS
- ✅ Advanced SQL queries demonstrating various techniques
- ✅ Statistical analysis with real findings
- ✅ REST API with documented endpoints

**Future Enhancements:**
- Interactive data visualization dashboard
- Real-time trend analysis
- Predictive modeling for enforcement prioritization

---

## CONTACT INFORMATION

**Maya Murry**
Email: maya.khalil2022@gmail.com
Phone: (267) 454-5679
GitHub: [@snedmagdous](https://github.com/snedmagdous)
LinkedIn: [linkedin.com/in/maya-murry](https://www.linkedin.com/in/maya-murry)

For questions about methodology, technical implementation, or project design decisions, please don't hesitate to reach out.

---

*This code sample demonstrates end-to-end data pipeline development, statistical analysis, and system architecture—core competencies for the Data Scientist role at the New York Attorney General's Office.*
