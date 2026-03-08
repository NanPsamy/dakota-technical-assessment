@echo off
setlocal enabledelayedexpansion

REM =====================================================
REM Dakota Pipeline Runner (Idempotent)
REM - First run: setup deps, .env, build containers, run pipeline
REM - Subsequent runs: skip completed setup/pipeline unless --force
REM =====================================================

set "ROOT=%~dp0"
cd /d "%ROOT%"

set "STATE_DIR=logs\state"
set "LOG_DIR=logs"
set "LOG_FILE=%LOG_DIR%\run.log"
set "FORCE_RUN=0"
set "COMPOSE_CMD="

if /I "%~1"=="--force" set "FORCE_RUN=1"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%STATE_DIR%" mkdir "%STATE_DIR%"

echo =====================================================
echo Dakota pipeline runner starting...
echo Log file: %LOG_FILE%
echo Force run: %FORCE_RUN%
echo =====================================================
echo [START] %date% %time%>>"%LOG_FILE%"

where docker-compose >nul 2>&1
if not errorlevel 1 (
    set "COMPOSE_CMD=docker-compose"
) else (
    where docker >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker CLI not found in PATH.
        echo [ERROR] Docker CLI not found in PATH.>>"%LOG_FILE%"
        exit /b 1
    )
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Neither docker-compose nor docker compose is available.
        echo [ERROR] Neither docker-compose nor docker compose is available.>>"%LOG_FILE%"
        exit /b 1
    )
    set "COMPOSE_CMD=docker compose"
)

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH.
    echo [ERROR] Python not found in PATH.>>"%LOG_FILE%"
    exit /b 1
)

echo [1/8] Checking .env setup...
if not exist ".env" (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >>"%LOG_FILE%" 2>&1
        if errorlevel 1 goto error
        echo [OK] Created .env from .env.example
        echo [OK] Created .env from .env.example>>"%LOG_FILE%"
    ) else (
        echo [ERROR] .env.example not found.
        echo [ERROR] .env.example not found.>>"%LOG_FILE%"
        exit /b 1
    )
) else (
    echo [SKIP] .env already exists
)

echo [2/8] Ensuring dbt dependencies...
if not exist "dbt\.venv\Scripts\dbt.exe" (
    echo [SETUP] Creating dbt virtual environment...
    python -m venv dbt\.venv >>"%LOG_FILE%" 2>&1
    if errorlevel 1 goto error
    dbt\.venv\Scripts\python.exe -m pip install --upgrade pip >>"%LOG_FILE%" 2>&1
    if errorlevel 1 goto error
    dbt\.venv\Scripts\python.exe -m pip install dbt-core dbt-postgres >>"%LOG_FILE%" 2>&1
    if errorlevel 1 goto error
    echo [OK] dbt dependencies installed
) else (
    echo [SKIP] dbt dependencies already installed
)

echo [3/8] Ensuring orchestration dependencies...
if not exist "orchestration\.venv\Scripts\python.exe" (
    echo [SETUP] Creating orchestration virtual environment...
    python -m venv orchestration\.venv >>"%LOG_FILE%" 2>&1
    if errorlevel 1 goto error
)
orchestration\.venv\Scripts\python.exe -m pip install --upgrade pip >>"%LOG_FILE%" 2>&1
if errorlevel 1 goto error
orchestration\.venv\Scripts\python.exe -m pip install -e orchestration >>"%LOG_FILE%" 2>&1
if errorlevel 1 goto error
echo [OK] orchestration dependencies ready

echo [4/8] Building containers (first-time only)...
if "%FORCE_RUN%"=="1" (
    echo [RUN] Force mode enabled, rebuilding containers...
    %COMPOSE_CMD% build >>"%LOG_FILE%" 2>&1
    if errorlevel 1 goto error
    echo %date% %time%>"%STATE_DIR%\containers_built.ok"
) else (
    if not exist "%STATE_DIR%\containers_built.ok" (
        %COMPOSE_CMD% build >>"%LOG_FILE%" 2>&1
        if errorlevel 1 goto error
        echo %date% %time%>"%STATE_DIR%\containers_built.ok"
        echo [OK] Containers built
    ) else (
        echo [SKIP] Containers already built
    )
)

echo [5/8] Starting core services...
%COMPOSE_CMD% up -d postgres api orchestration >>"%LOG_FILE%" 2>&1
if errorlevel 1 goto error

echo [6/8] Waiting for service health...
set /a "MAX_ATTEMPTS=60"
set /a "attempt=0"
:wait_postgres
set /a "attempt+=1"
%COMPOSE_CMD% ps postgres | findstr /I "healthy" >nul
if errorlevel 1 (
    if !attempt! GEQ !MAX_ATTEMPTS! (
        echo [ERROR] postgres did not become healthy in time.
        echo [ERROR] postgres did not become healthy in time.>>"%LOG_FILE%"
        goto error
    )
    timeout /t 2 >nul
    goto wait_postgres
)

set /a "attempt=0"
:wait_api
set /a "attempt+=1"
%COMPOSE_CMD% ps api | findstr /I "healthy" >nul
if errorlevel 1 (
    if !attempt! GEQ !MAX_ATTEMPTS! (
        echo [ERROR] api did not become healthy in time.
        echo [ERROR] api did not become healthy in time.>>"%LOG_FILE%"
        goto error
    )
    timeout /t 2 >nul
    goto wait_api
)
echo [OK] Core services are healthy

echo [7/8] Running pipeline end-to-end...
if "%FORCE_RUN%"=="0" if exist "%STATE_DIR%\pipeline_completed.ok" (
    echo [SKIP] Pipeline already completed previously. Use --force to rerun.
    goto done
)

echo [RUN] Ingestion...
%COMPOSE_CMD% up ingestion --abort-on-container-exit --exit-code-from ingestion >>"%LOG_FILE%" 2>&1
if errorlevel 1 goto error

echo [RUN] dbt run...
dbt\.venv\Scripts\dbt.exe run --project-dir dbt --profiles-dir dbt >>"%LOG_FILE%" 2>&1
if errorlevel 1 goto error

echo [RUN] dbt test...
dbt\.venv\Scripts\dbt.exe test --project-dir dbt --profiles-dir dbt >>"%LOG_FILE%" 2>&1
if errorlevel 1 goto error

echo [RUN] Generating markdown report...
orchestration\.venv\Scripts\python.exe orchestration\scripts\generate_reports.py >>"%LOG_FILE%" 2>&1
if errorlevel 1 goto error

echo [RUN] Generating PDF report...
orchestration\.venv\Scripts\python.exe orchestration\scripts\generate_pdf_report.py >>"%LOG_FILE%" 2>&1
if errorlevel 1 goto error

echo %date% %time%>"%STATE_DIR%\pipeline_completed.ok"
echo [OK] Pipeline execution completed

:done
echo [8/8] Finished successfully.
echo [END] %date% %time%>>"%LOG_FILE%"
echo Done. See %LOG_FILE% for full details.
exit /b 0

:error
echo [ERROR] Pipeline failed. Capturing service logs...
echo [ERROR] Pipeline failed at %date% %time%>>"%LOG_FILE%"
%COMPOSE_CMD% logs >>"%LOG_FILE%" 2>&1
echo [ERROR] See %LOG_FILE% for details.
exit /b 1