@echo off
setlocal enabledelayedexpansion

REM Check for .env
if not exist .env (
    echo Setting up environment...
    copy .env.example .env
    pause
)

REM Start PostgreSQL database first
echo Starting PostgreSQL database...
docker-compose up -d postgres || goto error

REM Wait for database to be healthy
echo Waiting for database to be healthy...
:wait_db
timeout /t 5 > nul
docker-compose ps postgres | find "healthy" > nul
if errorlevel 1 (
    echo Database not healthy yet, waiting...
    goto wait_db
)

REM Install deps if needed (e.g., uv sync in api/)
if not exist api\.venv (
    echo Installing API deps...
    cd api && uv sync || goto error
    cd ..
)

REM Build and start remaining services
docker-compose build || goto error
docker-compose up -d || goto error

REM Wait for all services to be healthy
echo Waiting for all services to be healthy...
:wait
timeout /t 5 > nul
docker-compose ps | find "healthy" > nul
if errorlevel 1 (
    echo Services not healthy yet, waiting...
    goto wait
)

REM Services are healthy, proceed with pipeline

REM Initialize database (e.g., run migrations)
echo Initializing database...
python database/initialize.py || goto error

REM Run ingestion
echo Running data ingestion...
docker-compose up ingestion || goto error

REM Generate reports
echo Generating reports...
python reports/generate.py || goto error

echo Pipeline complete.
goto end

:error
echo Error occurred. Check logs.
docker-compose logs > error.log
exit /b 1

:end