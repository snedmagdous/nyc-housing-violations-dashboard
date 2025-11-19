# PostgreSQL Setup Guide

This guide will help you install PostgreSQL and PostGIS for the NYC Housing Violations project.

## Windows Installation

### Step 1: Download PostgreSQL

1. Go to https://www.postgresql.org/download/windows/
2. Download the PostgreSQL installer (recommended version 14 or higher)
3. Or use the direct link: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

### Step 2: Install PostgreSQL

1. Run the downloaded installer
2. During installation:
   - **Port**: Keep default `5432`
   - **Password**: Choose a password for the `postgres` superuser (remember this!)
   - **Locale**: Keep default
3. In "Select Components", make sure to check:
   - [x] PostgreSQL Server
   - [x] pgAdmin 4 (GUI tool)
   - [x] Command Line Tools
   - [x] Stack Builder (we'll use this for PostGIS)

### Step 3: Install PostGIS Extension

**Option A: Using Stack Builder (Recommended)**
1. After PostgreSQL installation completes, Stack Builder should launch
2. Select your PostgreSQL installation
3. Under "Spatial Extensions", select **PostGIS**
4. Follow the installation wizard

**Option B: Manual Installation**
1. Download PostGIS from: https://postgis.net/windows_downloads/
2. Run the installer and select your PostgreSQL installation directory

### Step 4: Verify Installation

Open Command Prompt or PowerShell and run:

```bash
psql --version
```

You should see something like: `psql (PostgreSQL) 14.x`

### Step 5: Create Project Database

1. Open pgAdmin 4 (installed with PostgreSQL)
2. Connect to your local PostgreSQL server (password you set earlier)
3. Right-click "Databases" → "Create" → "Database"
4. Database name: `nyc_housing_violations`
5. Click "Save"

**OR** use command line:

```bash
psql -U postgres
# Enter your password when prompted

CREATE DATABASE nyc_housing_violations;
\c nyc_housing_violations
CREATE EXTENSION postgis;
\q
```

### Step 6: Set Environment Variables (Optional but Recommended)

Add PostgreSQL bin directory to your PATH:
1. Search "Environment Variables" in Windows
2. Edit "Path" under System Variables
3. Add: `C:\Program Files\PostgreSQL\14\bin` (adjust version number)

---

## Database Configuration for This Project

Once installed, create a `.env` file in the project root with your credentials:

```env
# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nyc_housing_violations
DB_USER=postgres
DB_PASSWORD=your_password_here

# Optional: NYC Open Data API Token
NYC_OPEN_DATA_TOKEN=your_token_here
```

**IMPORTANT:** The `.env` file is already in `.gitignore` so your credentials won't be committed.

---

## Quick Test

Test your connection by running (after creating .env file):

```bash
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://postgres:your_password@localhost:5432/nyc_housing_violations'); print('Connection successful!' if engine else 'Connection failed')"
```

---

## Troubleshooting

**Issue: "psql: command not found"**
- PostgreSQL bin directory is not in PATH
- Use full path: `C:\Program Files\PostgreSQL\14\bin\psql.exe`

**Issue: "password authentication failed"**
- Double-check the password you set during installation
- Make sure you're using user `postgres`

**Issue: "could not connect to server"**
- Ensure PostgreSQL service is running
- Check Windows Services → "postgresql-x64-14" should be "Running"

---

## Next Steps

After installation, run:
```bash
python src/data_pipeline/setup_db.py
```

This will create all necessary tables and extensions.
