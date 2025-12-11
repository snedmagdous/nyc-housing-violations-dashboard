"""
FastAPI Application

REST API for NYC Housing Violations data and analysis.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import our route modules
from src.api.routes import violations, buildings, analysis
from src.api.database import test_db_connection

# Initialize FastAPI app
app = FastAPI(
    title="NYC Housing Violations API",
    description="""
    REST API for accessing and analyzing NYC housing violation data.

    ## Features
    - **Violations**: Search and filter housing violations
    - **Buildings**: Aggregate building statistics and rankings
    - **Analysis**: Hotspot and trend analysis (coming soon)

    ## Data Source
    Data from NYC Open Data - HPD Housing Maintenance Code Violations
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# These connect our route files to the main app
app.include_router(violations.router)
app.include_router(buildings.router)
app.include_router(analysis.router)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "NYC Housing Violations Dashboard API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Checks if API and database are working.
    """
    db_connected = test_db_connection()

    return {
        "status": "healthy" if db_connected else "degraded",
        "service": "nyc-housing-violations-api",
        "database": "connected" if db_connected else "disconnected"
    }


# Note: Violations, buildings, and analysis endpoints are now in their respective route files
# They're automatically included via app.include_router() above


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

