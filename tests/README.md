# Test Suite for NYC Housing Violations Dashboard

## Overview

This directory contains comprehensive unit tests, integration tests, and API tests for the NYC Housing Violations Dashboard. The test suite ensures code quality, catches regressions, and documents expected behavior.

## Current Test Coverage

### ✅ Completed Tests

1. **`test_api_health.py`** - API Health & Root Endpoints
   - Root endpoint structure and response format
   - Health check with database connected/disconnected
   - CORS headers validation
   - Error handling (404, 405)
   - API documentation endpoints (/docs, /redoc, /openapi.json)
   - Response time performance tests

2. **`test_schemas.py`** - Pydantic Model Validation
   - ViolationBase schema validation
   - BuildingBase and BuildingDetail schemas
   - Optional field handling
   - Field aliasing (e.g., "class" → violation_class)
   - Type validation and coercion
   - Response wrapper models (ViolationListResponse, BuildingListResponse)
   - Edge cases (negative values, coordinate validation)

3. **`test_data_cleaning.py`** - Data Pipeline Functions
   - Date parsing from ISO strings
   - Violation class standardization
   - Address cleaning and full_address creation
   - Duplicate removal logic
   - Derived feature creation (temporal, binary flags, severity scores)
   - Data validation (coordinates, future dates)
   - Full pipeline integration test
   - Empty DataFrame handling

### 🚧 Tests To Be Added

4. **`test_api_violations.py`** - Violations API Endpoints
   - GET /api/violations (list with pagination)
   - Query parameter validation (borough, class, date ranges)
   - Filtering logic
   - Sorting validation
   - Error cases (invalid parameters, malformed requests)

5. **`test_api_buildings.py`** - Buildings API Endpoints
   - GET /api/buildings (list with filters)
   - GET /api/buildings/search (search functionality)
   - GET /api/buildings/{id} (single building detail)
   - GET /api/buildings/{id}/violations (building's violations)
   - GET /api/buildings/stats/top-offenders
   - Route ordering (static before dynamic routes)

6. **`test_api_analysis.py`** - Analysis API Endpoints
   - Temporal analysis endpoints
   - Geospatial hotspot detection
   - Landlord rankings
   - Risk score calculations
   - Dashboard summary stats

7. **`test_database.py`** - Database Operations
   - Connection handling
   - Query execution
   - Session management
   - Connection pool behavior
   - Error recovery

8. **`test_geospatial_analysis.py`** - Geospatial Functions
   - Hotspot detection algorithms
   - Building clustering
   - Borough comparisons
   - Coordinate validation

9. **`test_temporal_analysis.py`** - Temporal Functions
   - Seasonal pattern detection
   - Trend analysis
   - Day-of-week patterns

10. **`test_predictive_model.py`** - ML Model Functions
    - Risk score calculation
    - At-risk building identification
    - Forecasting logic

## Test Organization

### Test Markers

Tests are categorized using pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Skip slow tests
pytest -m "not slow"
```

### Fixtures

Shared test fixtures are defined in `conftest.py`:
- `client`: FastAPI TestClient for API testing
- `sample_violation_data`: Mock violation data
- `sample_building_data`: Mock building aggregation data
- `sample_raw_violation_csv`: Temporary CSV file with raw data
- `mock_db_session`: Mock database session

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api_health.py

# Run specific test function
pytest tests/test_api_health.py::test_health_check_success

# Stop on first failure
pytest -x

# Run tests matching a pattern
pytest -k "health"
```

### Coverage Reports

```bash
# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Watch Mode (Development)

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw
```

## Testing Best Practices Used

1. **AAA Pattern** - Arrange, Act, Assert
   - Set up test data (Arrange)
   - Execute the function (Act)
   - Verify results (Assert)

2. **Descriptive Test Names**
   - Test names describe WHAT is being tested and WHY
   - Example: `test_health_check_when_database_disconnected`

3. **Comprehensive Comments**
   - Every test has detailed docstrings
   - Edge cases are documented
   - "Why" is explained, not just "what"

4. **Mocking External Dependencies**
   - Database calls are mocked in unit tests
   - External APIs are mocked
   - Tests run fast and don't require infrastructure

5. **Test Isolation**
   - Each test is independent
   - Tests can run in any order
   - No shared state between tests

6. **Edge Case Testing**
   - Null/None values
   - Empty lists
   - Invalid inputs
   - Boundary conditions
   - Error conditions

## Edge Cases Covered

### Data Quality Issues
- ✅ Missing values (None, NaN)
- ✅ Duplicate records
- ✅ Malformed dates
- ✅ Invalid coordinates
- ✅ Unexpected violation classes
- ✅ Future dates
- ✅ Whitespace in strings
- ✅ Mixed case text

### API Edge Cases
- ✅ Database disconnection
- ✅ Invalid query parameters
- ✅ Nonexistent resources (404)
- ✅ Wrong HTTP methods (405)
- ✅ Empty result sets
- ✅ Pagination edge cases

### Business Logic Edge Cases
- ✅ Buildings with zero violations
- ✅ Violations with no building association
- ✅ Negative date ranges (status before inspection)
- ✅ Coordinates outside NYC bounds

## Test Metrics

Target metrics:
- **Code Coverage**: > 80%
- **Test Execution Time**: < 10 seconds for full suite
- **Test Count**: 50+ tests
- **Pass Rate**: 100%

## CI/CD Integration (Planned)

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Contributing

When adding new features:
1. Write tests FIRST (TDD approach)
2. Ensure tests cover happy path AND edge cases
3. Add descriptive comments explaining the test
4. Update this README with test description
5. Maintain > 80% code coverage

## Testing Philosophy

> "Tests are not just about finding bugs - they're about:
> - Documenting expected behavior
> - Enabling confident refactoring
> - Catching regressions early
> - Serving as executable examples
> - Building confidence in the codebase"

## Future Enhancements

- [ ] Add property-based testing (Hypothesis library)
- [ ] Add mutation testing (validate test quality)
- [ ] Add performance benchmarks
- [ ] Add contract testing for API
- [ ] Add visual regression tests for frontend
- [ ] Set up test coverage tracking (Codecov)
- [ ] Add security testing (SQL injection, XSS)
- [ ] Add load testing (Locust)
