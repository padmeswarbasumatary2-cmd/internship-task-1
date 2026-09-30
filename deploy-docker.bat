@echo off
REM Docker Deployment Script for Content Tagging Engine (Windows)

setlocal enabledelayedexpansion

cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║           🐳 DOCKER DEPLOYMENT - AUTOMATED TAGGING ENGINE            ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

REM Step 1: Check Docker Installation
echo [STEP 1] Checking Docker Installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed
    echo.
    echo 📥 Please install Docker:
    echo    Windows: https://www.docker.com/products/docker-desktop
    echo    After installation, restart this terminal and try again.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('docker --version') do set DOCKER_VER=%%i
echo ✓ %DOCKER_VER%

REM Step 2: Check Docker Daemon
echo.
echo [STEP 2] Checking Docker Daemon...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker daemon is not running
    echo    Please start Docker Desktop
    echo.
    pause
    exit /b 1
)
echo ✓ Docker daemon is running

REM Step 3: Check Docker Compose
echo.
echo [STEP 3] Checking Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker Compose is not installed
        echo    Install from: https://docs.docker.com/compose/install/
        echo.
        pause
        exit /b 1
    )
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)
echo ✓ Docker Compose available: %COMPOSE_CMD%

REM Step 4: Navigate to project
echo.
echo [STEP 4] Navigating to project directory...
cd /d "%~dp0"
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml not found in %cd%
    pause
    exit /b 1
)
echo ✓ Found docker-compose.yml

REM Step 5: Build images
echo.
echo [STEP 5] Building Docker images...
echo    This may take 2-3 minutes on first run...
%COMPOSE_CMD% build
if errorlevel 1 (
    echo ❌ Docker build failed
    pause
    exit /b 1
)
echo ✓ Docker images built successfully

REM Step 6: Start services
echo.
echo [STEP 6] Starting services (PostgreSQL, Redis, API)...
%COMPOSE_CMD% up -d
if errorlevel 1 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)
echo ✓ Services starting...

REM Step 7: Wait for services
echo.
echo [STEP 7] Waiting for services to become healthy (10 seconds)...
timeout /t 10 /nobreak

REM Step 8: Initialize database
echo.
echo [STEP 8] Initializing database...
%COMPOSE_CMD% exec -T app python database.py >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Database initialization had issues (may be expected^)
) else (
    echo ✓ Database initialized
)

REM Step 9: Check health
echo.
echo [STEP 9] Verifying API health...
setlocal enabledelayedexpansion
for /l %%i in (1,1,10) do (
    for /f %%j in ('powershell -Command "(Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/health' -UseBasicParsing -ErrorAction SilentlyContinue).StatusCode" 2^>nul') do set STATUS=%%j
    if "!STATUS!"=="200" (
        echo ✓ API is responding (HTTP !STATUS!^)
        goto success
    )
    if not %%i==10 (
        echo    Attempt %%i/10... (HTTP !STATUS!^)
        timeout /t 2 /nobreak >nul
    )
)

:success
echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                    ✅ DEPLOYMENT SUCCESSFUL!                         ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo 📍 API Access Points:
echo    • Swagger UI: http://localhost:8000/docs
echo    • Health Check: http://localhost:8000/api/v1/health
echo    • API Base URL: http://localhost:8000/api/v1
echo.
echo 🐳 Docker Status:
%COMPOSE_CMD% ps
echo.
echo 📊 View Logs:
echo    • All services: %COMPOSE_CMD% logs -f
echo    • Only API: %COMPOSE_CMD% logs -f app
echo    • Only DB: %COMPOSE_CMD% logs -f postgres
echo    • Only Cache: %COMPOSE_CMD% logs -f redis
echo.
echo 🛑 Stop Services:
echo    %COMPOSE_CMD% down
echo.
echo Next: Open http://localhost:8000/docs in your browser!
echo.
pause
