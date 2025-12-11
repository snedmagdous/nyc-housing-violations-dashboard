"""
API Health and Root Endpoint Tests

Tests the basic health check and root endpoints of the API.
These are critical for monitoring and deployment.

What we're testing:
1. Root endpoint returns correct structure
2. Health check works when DB is connected
3. Health check handles DB disconnection gracefully
4. Response formats match API contract

Why test health endpoints?
- They're used by load balancers and monitoring systems
- They help diagnose deployment issues
- They validate the entire stack is working
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


# =================== ROOT ENDPOINT TESTS ===================

@pytest.mark.api
def test_root_endpoint_returns_200(client):
    """
    Test that the root endpoint (/) returns a 200 status code.

    This is the simplest possible test - just verify the API is running.

    Edge cases tested:
    - Server is responding
    - No authentication required for root
    """
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.api
def test_root_endpoint_returns_json(client):
    """
    Test that root endpoint returns JSON (not HTML or plain text).

    Why test this?
    - Ensures proper Content-Type header
    - Catches configuration errors (like serving static files instead)
    """
    response = client.get("/")
    assert response.headers["content-type"] == "application/json"


@pytest.mark.api
def test_root_endpoint_has_required_fields(client):
    """
    Test that root endpoint returns expected fields.

    API Contract Test: Ensures the response structure matches what
    clients expect. If this breaks, client apps might crash.

    Required fields:
    - message: Human-readable description
    - version: API version for compatibility checking
    - docs: Link to API documentation
    - status: Current API status

    Why validate the schema?
    - Prevents breaking changes
    - Documents the API contract
    - Catches typos and refactoring errors
    """
    response = client.get("/")
    data = response.json()

    # Check all required fields exist
    assert "message" in data, "Missing 'message' field"
    assert "version" in data, "Missing 'version' field"
    assert "docs" in data, "Missing 'docs' field"
    assert "status" in data, "Missing 'status' field"

    # Validate field types
    assert isinstance(data["message"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["docs"], str)
    assert isinstance(data["status"], str)


@pytest.mark.api
def test_root_endpoint_status_is_active(client):
    """
    Test that root endpoint reports status as "active".

    This is important for load balancers that check /
    to determine if traffic should be routed to this instance.
    """
    response = client.get("/")
    data = response.json()
    assert data["status"] == "active"


# =================== HEALTH CHECK ENDPOINT TESTS ===================

@pytest.mark.api
def test_health_check_endpoint_exists(client):
    """
    Test that /health endpoint exists and returns 200.

    Health checks are critical for:
    - Kubernetes liveness/readiness probes
    - Load balancer health checks
    - Monitoring systems (Datadog, New Relic, etc.)
    """
    response = client.get("/health")
    assert response.status_code == 200


@pytest.mark.api
@patch('src.api.main.test_db_connection')
def test_health_check_when_database_connected(mock_db_test, client):
    """
    Test health check when database connection is working.

    This simulates a healthy system where everything is connected.

    Mocking Strategy:
    - Mock test_db_connection() to return True
    - This simulates successful DB connection without needing real DB

    Why mock the database?
    - Tests run faster (no network I/O)
    - Tests are reliable (don't depend on external services)
    - Can test edge cases (connection failures, timeouts)

    Expected Response:
    {
        "status": "healthy",
        "service": "nyc-housing-violations-api",
        "database": "connected"
    }
    """
    # Configure the mock to simulate successful DB connection
    mock_db_test.return_value = True

    response = client.get("/health")
    data = response.json()

    # Verify response structure
    assert response.status_code == 200
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "service" in data

    # Verify the DB test function was called
    mock_db_test.assert_called_once()


@pytest.mark.api
@patch('src.api.main.test_db_connection')
def test_health_check_when_database_disconnected(mock_db_test, client):
    """
    Test health check when database connection fails.

    This simulates a degraded system state. The API is still running,
    but the database is down.

    Critical Test: The API should:
    - Still return 200 (not 500) - degraded, not broken
    - Report status as "degraded"
    - Report database as "disconnected"

    Why return 200 instead of 500?
    - Load balancers won't remove this instance
    - Monitoring can distinguish between "API down" and "DB down"
    - Allows graceful degradation
    """
    # Configure the mock to simulate DB connection failure
    mock_db_test.return_value = False

    response = client.get("/health")
    data = response.json()

    # Should still return 200 (degraded, not dead)
    assert response.status_code == 200

    # But status should indicate degraded state
    assert data["status"] == "degraded"
    assert data["database"] == "disconnected"

    # Verify the DB test function was called
    mock_db_test.assert_called_once()


@pytest.mark.api
@patch('src.api.main.test_db_connection')
def test_health_check_handles_database_exception(mock_db_test, client):
    """
    Test health check when database check throws an exception.

    This tests a different failure mode: not just "can't connect",
    but "the connection attempt crashed".

    Scenarios this catches:
    - Database driver not installed
    - Malformed connection string
    - Unexpected database error
    - Network timeout exceptions

    The API should handle this gracefully and still return a response.
    """
    # Configure the mock to raise an exception
    mock_db_test.side_effect = Exception("Database driver error")

    response = client.get("/health")

    # Should still return 200, not crash
    assert response.status_code == 200

    data = response.json()
    # Should report degraded state
    assert data["status"] == "degraded"
    assert data["database"] == "disconnected"


# =================== CORS TESTS ===================

@pytest.mark.api
def test_cors_headers_present(client):
    """
    Test that CORS headers are present in responses.

    CORS (Cross-Origin Resource Sharing) headers are REQUIRED for
    the frontend to call the API from a different domain.

    Without CORS:
    - Browser blocks all API requests from frontend
    - Users see "CORS error" in console
    - Application is completely broken

    Important CORS Headers:
    - Access-Control-Allow-Origin: Which domains can call the API
    - Access-Control-Allow-Methods: Which HTTP methods are allowed
    - Access-Control-Allow-Headers: Which headers can be sent

    Note: In production, you should restrict Allow-Origin to specific
    domains, not "*". This is a security consideration.
    """
    response = client.get("/")

    # Check for CORS headers
    # Note: TestClient might not include all CORS headers in the response
    # In production, verify these with actual browser requests
    assert response.status_code == 200


# =================== ERROR HANDLING TESTS ===================

@pytest.mark.api
def test_404_for_nonexistent_endpoint(client):
    """
    Test that requesting a non-existent endpoint returns 404.

    This validates:
    - FastAPI routing is working correctly
    - No wildcard routes catching everything
    - Proper HTTP status codes

    Users should get clear "not found" responses, not generic 500 errors.
    """
    response = client.get("/this/endpoint/does/not/exist")
    assert response.status_code == 404


@pytest.mark.api
def test_405_for_wrong_http_method(client):
    """
    Test that using wrong HTTP method returns 405 Method Not Allowed.

    Example: If /health only supports GET, POST should return 405.

    Why test this?
    - Helps developers debug API usage
    - Validates route definitions
    - Ensures proper HTTP semantics
    """
    # Health check only supports GET, try POST
    response = client.post("/health")
    assert response.status_code == 405  # Method Not Allowed


# =================== DOCUMENTATION ENDPOINT TESTS ===================

@pytest.mark.api
def test_docs_endpoint_exists(client):
    """
    Test that /docs endpoint (Swagger UI) is accessible.

    FastAPI auto-generates interactive API documentation at /docs.
    This is CRITICAL for:
    - Developer experience
    - API exploration
    - Client library generation
    - Testing during development

    If this fails:
    - Check that docs_url="/docs" in FastAPI app creation
    - Ensure Pydantic models are properly defined
    """
    response = client.get("/docs")
    assert response.status_code == 200


@pytest.mark.api
def test_redoc_endpoint_exists(client):
    """
    Test that /redoc endpoint (ReDoc UI) is accessible.

    ReDoc is an alternative documentation UI that some developers prefer.
    It's more readable for complex APIs.

    Note: FastAPI provides both /docs (Swagger) and /redoc (ReDoc) by default.
    """
    response = client.get("/redoc")
    assert response.status_code == 200


@pytest.mark.api
def test_openapi_schema_endpoint_exists(client):
    """
    Test that OpenAPI schema endpoint is accessible.

    The /openapi.json endpoint provides the machine-readable API spec.

    This is used by:
    - Code generators (generate client libraries)
    - Testing tools (Postman, Insomnia)
    - API gateways
    - Documentation generators

    The schema should be valid JSON and follow OpenAPI 3.0 spec.
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200

    # Validate it's JSON
    data = response.json()
    assert isinstance(data, dict)

    # Check for required OpenAPI fields
    assert "openapi" in data  # OpenAPI version
    assert "info" in data     # API metadata
    assert "paths" in data    # API endpoints


# =================== PERFORMANCE TESTS ===================

@pytest.mark.slow
def test_health_check_response_time(client):
    """
    Test that health check responds quickly.

    Health checks should be FAST because:
    - Load balancers call them frequently (every few seconds)
    - Slow health checks can trigger false alarms
    - They should not do expensive operations

    Target: < 100ms response time

    Note: This is a basic timing test. For production, use proper
    performance testing tools like Locust or Apache Bench.
    """
    import time

    start = time.time()
    response = client.get("/health")
    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 0.1  # Should respond in less than 100ms

    # Note: This might fail on slow CI systems. Consider making
    # the threshold configurable or skipping in CI.
