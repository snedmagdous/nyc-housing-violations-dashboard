# Database Pipeline Quick Start

This guide will walk you through setting up and using the PostgreSQL database pipeline for the NYC Housing Violations project.

## Prerequisites

✅ Python virtual environment activated
✅ All dependencies installed (`pip install -r requirements.txt`)
✅ Cleaned data available (`data/processed/violations_cleaned.csv`)

## Step-by-Step Setup

### Step 1: Install PostgreSQL with PostGIS

Follow the detailed installation guide: [postgres_setup.md](postgres_setup.md)

**Quick checklist:**
- [ ] PostgreSQL 14+ installed
- [ ] PostGIS extension installed
- [ ] Database `nyc_housing_violations` created
- [ ] `.env` file configured with credentials

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This includes:
- `psycopg2-binary` - PostgreSQL adapter
- `sqlalchemy` - Python SQL toolkit
- `geoalchemy2` - PostGIS support for SQLAlchemy

### Step 3: Configure Database Connection

Create a `.env` file in the project root (copy from `.env.example`):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nyc_housing_violations
DB_USER=postgres
DB_PASSWORD=your_actual_password
```

Test your connection:
```bash
python config/database.py
```

### Step 4: Set Up Database Schema

This creates the `violations` and `buildings` tables with PostGIS support:

```bash
python src/data_pipeline/setup_db.py
```

**What this does:**
- Enables PostGIS extension
- Creates `violations` table (45 columns, geometry support)
- Creates `buildings` dimension table (aggregated metrics)
- Creates indexes for performance
- Validates schema

### Step 5: Load Data

Load your cleaned CSV data into PostgreSQL:

```bash
python src/data_pipeline/load_data.py
```

**What this does:**
- Reads `data/processed/violations_cleaned.csv`
- Converts lat/long to PostGIS geometry
- Loads 10,000 violations in batches
- Aggregates building-level metrics
- Calculates risk scores

**Expected output:**
```
============================================================
Load Data to PostgreSQL - NYC Housing Violations
============================================================

[1/2] Loading violations table...
  Loading batches: 100%|████████████| 10/10 [00:05<00:00]
    + Loaded 10,000 violations

[2/2] Aggregating buildings table...
    + Aggregated 8,234 buildings

[VERIFY] Checking data integrity...
    + Violations: 10,000
    + Buildings: 8,234
    + Records with geometry: 9,999 (99.9%)
```

### Step 6: Run SQL Queries

Query examples are in `sql_queries/`:

**Option A: Command line**
```bash
psql -U postgres -d nyc_housing_violations -f sql_queries/01_basic_queries.sql
```

**Option B: Python**
```python
from config.database import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT boro, COUNT(*) as violations
        FROM violations
        GROUP BY boro
        ORDER BY violations DESC;
    """))
    for row in result:
        print(row)
```

**Option C: pgAdmin 4**
1. Open pgAdmin 4
2. Connect to `nyc_housing_violations`
3. Open Query Tool
4. Paste SQL from files in `sql_queries/`

## Database Schema Overview

### `violations` Table
**Primary fact table** - Individual violation records

Key columns:
- `violationid` (PK)
- `buildingid` (FK to buildings)
- `violation_class` - A, B, C, or I
- `geom` - PostGIS Point geometry
- `is_open`, `is_severe`, `is_rent_impairing` - Boolean flags
- `inspection_year`, `inspection_month` - Temporal fields
- `severity_score` - 0-3 scale

Indexes:
- Primary key on `violationid`
- Composite indexes on `(boro, class)`, `(year, month)`
- Spatial index (GIST) on `geom`
- Full-text search on `novdescription`

### `buildings` Table
**Dimension table** - Aggregated building-level metrics

Key columns:
- `buildingid` (PK)
- `bin`, `bbl` - NYC building identifiers
- `total_violations`, `open_violations`
- `class_a_count`, `class_b_count`, `class_c_count`, `class_i_count`
- `severe_violations`, `rent_impairing_violations`
- `risk_score` - Composite risk metric
- `geom` - PostGIS Point geometry

## SQL Query Examples

### 1. Basic Queries (01_basic_queries.sql)
- Violations by borough
- Top violation types
- Building rankings
- Resolution rates

### 2. Window Functions (02_window_functions.sql)
- ROW_NUMBER, RANK, DENSE_RANK
- Moving averages
- Month-over-month growth
- Percentile analysis

### 3. CTEs & Subqueries (03_cte_subqueries.sql)
- Multi-level CTEs
- Recursive queries (violation escalation)
- Correlated subqueries
- Cohort analysis

### 4. Geospatial Queries (04_geospatial_queries.sql)
- Find violations within radius
- Spatial clustering
- Distance calculations
- Heat maps and density analysis

## SQL Skills Showcased

✅ Complex JOINs
✅ Window functions (OVER, PARTITION BY, LAG/LEAD)
✅ CTEs (WITH clause) including recursive CTEs
✅ Subqueries (correlated and nested)
✅ Aggregations with GROUP BY and HAVING
✅ Date/time manipulation
✅ CASE statements and conditional logic
✅ PostGIS geospatial functions
✅ Performance optimization (indexes, EXPLAIN)
✅ Statistical functions (PERCENTILE_CONT, STDDEV)

## Troubleshooting

**Error: "could not connect to server"**
- Ensure PostgreSQL service is running
- Check credentials in `.env`
- Verify database exists: `psql -U postgres -l`

**Error: "PostGIS not found"**
- Install PostGIS extension (see postgres_setup.md)
- Enable in database: `CREATE EXTENSION postgis;`

**Error: "relation does not exist"**
- Run setup script first: `python src/data_pipeline/setup_db.py`

**Slow queries**
- Run `ANALYZE violations;` and `ANALYZE buildings;`
- Check index usage: `EXPLAIN ANALYZE <your query>;`

## Next Steps

After setting up the database:

1. **Run exploratory analysis** in Jupyter notebooks
2. **Build FastAPI endpoints** to expose data via REST API
3. **Create visualizations** using the SQL query results
4. **Develop ML models** for violation prediction
5. **Deploy to cloud** (AWS RDS, Azure Database)

## Performance Tips

- Use `EXPLAIN ANALYZE` to profile queries
- Leverage indexes on frequently filtered columns
- Use CTEs for code readability, subqueries for performance
- Batch large INSERT operations (already done in load_data.py)
- Consider materialized views for complex aggregations

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostGIS Documentation](https://postgis.net/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
