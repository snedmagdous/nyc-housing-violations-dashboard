# SQL Queries - NYC Housing Violations Analysis

This directory contains SQL queries demonstrating various analytical techniques for the NYC Housing Violations database.

## Query Categories

### 1. **basic_queries.sql**
- Simple SELECT statements
- Filtering and sorting
- Basic aggregations

### 2. **window_functions.sql**
- ROW_NUMBER, RANK, DENSE_RANK
- LAG/LEAD for temporal analysis
- Moving averages and cumulative stats

### 3. **cte_subqueries.sql**
- Common Table Expressions (CTEs)
- Nested subqueries
- Complex multi-step analysis

### 4. **geospatial_queries.sql**
- PostGIS spatial queries
- Distance calculations
- Geographic clustering
- Finding violations within radius

### 5. **repeat_offenders.sql**
- Identifying worst landlords
- Building violation patterns
- Temporal violation trends

### 6. **enforcement_analysis.sql**
- Response time analysis
- Enforcement gaps by neighborhood
- Status transition analysis

## How to Run

### Option 1: psql Command Line
```bash
psql -U postgres -d nyc_housing_violations -f sql_queries/basic_queries.sql
```

### Option 2: pgAdmin 4
1. Open pgAdmin 4
2. Connect to `nyc_housing_violations` database
3. Open Query Tool
4. Load and execute SQL file

### Option 3: Python
```python
from config.database import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    with open('sql_queries/basic_queries.sql', 'r') as f:
        sql = f.read()
    result = conn.execute(text(sql))
    for row in result:
        print(row)
```

## Skills Demonstrated

- ✅ Complex JOINs
- ✅ Window functions (OVER, PARTITION BY)
- ✅ CTEs (WITH clause)
- ✅ Subqueries
- ✅ Aggregations (GROUP BY, HAVING)
- ✅ Date/time functions
- ✅ String operations
- ✅ CASE statements
- ✅ PostGIS geospatial queries
- ✅ Performance optimization (indexes, EXPLAIN)
