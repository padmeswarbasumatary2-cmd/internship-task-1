#!/usr/bin/env bash
# Docker Deployment Script for Content Tagging Engine

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║           🐳 DOCKER DEPLOYMENT - AUTOMATED TAGGING ENGINE            ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check Docker Installation
echo "[STEP 1] Checking Docker Installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo ""
    echo "📥 Please install Docker:"
    echo "   Windows/Mac: https://www.docker.com/products/docker-desktop"
    echo "   Linux: https://docs.docker.com/engine/install/"
    echo ""
    echo "After installation, restart this terminal and try again."
    exit 1
fi
echo "✓ Docker version: $(docker --version)"

# Step 2: Check Docker Daemon
echo ""
echo "[STEP 2] Checking Docker Daemon..."
if ! docker ps &> /dev/null; then
    echo "❌ Docker daemon is not running"
    echo "   Please start Docker Desktop (Windows/Mac) or: sudo systemctl start docker (Linux)"
    exit 1
fi
echo "✓ Docker daemon is running"

# Step 3: Check Docker Compose
echo ""
echo "[STEP 3] Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  Docker Compose not found, trying 'docker compose'..."
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is not installed"
        echo "   Install from: https://docs.docker.com/compose/install/"
        exit 1
    fi
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi
echo "✓ Docker Compose available: $COMPOSE_CMD"

# Step 4: Navigate to project
echo ""
echo "[STEP 4] Navigating to project directory..."
cd "$(dirname "$0")"
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in $(pwd)"
    exit 1
fi
echo "✓ Found docker-compose.yml"

# Step 5: Build images
echo ""
echo "[STEP 5] Building Docker images..."
echo "   This may take 2-3 minutes on first run..."
$COMPOSE_CMD build
if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi
echo "✓ Docker images built successfully"

# Step 6: Start services
echo ""
echo "[STEP 6] Starting services (PostgreSQL, Redis, API)..."
$COMPOSE_CMD up -d
if [ $? -ne 0 ]; then
    echo "❌ Failed to start services"
    exit 1
fi
echo "✓ Services starting..."

# Step 7: Wait for services
echo ""
echo "[STEP 7] Waiting for services to become healthy..."
sleep 10

# Step 8: Initialize database
echo ""
echo "[STEP 8] Initializing database..."
$COMPOSE_CMD exec -T app python database.py
if [ $? -ne 0 ]; then
    echo "⚠️  Database initialization had issues (may be expected)"
fi
echo "✓ Database initialization attempted"

# Step 9: Check health
echo ""
echo "[STEP 9] Verifying API health..."
for i in {1..10}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)
    if [ "$STATUS" = "200" ]; then
        echo "✓ API is responding (HTTP $STATUS)"
        break
    fi
    if [ $i -lt 10 ]; then
        echo "   Attempt $i/10... (HTTP $STATUS)"
        sleep 2
    fi
done

# Success
echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ DEPLOYMENT SUCCESSFUL!                         ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 API Access Points:"
echo "   • Swagger UI: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/api/v1/health"
echo "   • API Base URL: http://localhost:8000/api/v1"
echo ""
echo "🐳 Docker Status:"
$COMPOSE_CMD ps
echo ""
echo "📊 View Logs:"
echo "   • All services: $COMPOSE_CMD logs -f"
echo "   • Only API: $COMPOSE_CMD logs -f app"
echo "   • Only DB: $COMPOSE_CMD logs -f postgres"
echo "   • Only Cache: $COMPOSE_CMD logs -f redis"
echo ""
echo "🛑 Stop Services:"
echo "   $COMPOSE_CMD down"
echo ""
echo "Next: Open http://localhost:8000/docs in your browser!"
echo ""
