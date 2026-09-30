#!/usr/bin/env python3
"""
Docker Deployment Guide - Step by Step Instructions
"""

def show_docker_deployment_guide():
    guide = """
╔══════════════════════════════════════════════════════════════════════════════╗
║              🐳 DOCKER DEPLOYMENT GUIDE - STEP BY STEP                       ║
║          Automated Content Tagging and Taxonomy Engine                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 CURRENT STATUS:
  ✓ 40 project files created
  ✓ FastAPI application configured
  ✓ docker-compose.yml prepared
  ✓ Dockerfile created
  ✓ Demo Dockerfile created (lightweight)
  ✓ Demo app running on port 8000

================================================================================
🎯 DEPLOYMENT OPTIONS
================================================================================

OPTION 1: Quick Demo Deployment (RECOMMENDED FOR TESTING)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Time: 1-2 minutes
Requirements: Docker and Docker Desktop installed
Size: ~300 MB

Steps:
  1. Install Docker Desktop (if not installed):
     → https://www.docker.com/products/docker-desktop
     → For Windows/Mac: Download and run installer
     → For Linux: curl -fsSL https://get.docker.com | sh

  2. Start Docker Desktop (Windows/Mac)
     → Open Docker Desktop application
     → Wait for Docker daemon to start

  3. Open Terminal/PowerShell in project directory:
     cd "c:\\Users\\radhi\\OneDrive\\Desktop\\intern 1"

  4. Deploy using demo configuration:
     docker-compose -f docker-compose.demo.yml up -d

  5. Wait 10-20 seconds for services to start

  6. Verify deployment:
     docker ps
     curl http://localhost:8000/api/v1/health

  7. Access the API:
     → Browser: http://localhost:8000/docs
     → API: http://localhost:8000/api/v1/tag-content

  8. Stop services when done:
     docker-compose -f docker-compose.demo.yml down

================================================================================

OPTION 2: Full Production Deployment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Time: 5-10 minutes (includes PyTorch, Transformers, spaCy)
Requirements: Docker and Docker Desktop installed, 3-4 GB disk space
Size: ~3-4 GB

Steps:
  1. Install Docker Desktop (same as above)

  2. Open Terminal/PowerShell in project directory:
     cd "c:\\Users\\radhi\\OneDrive\\Desktop\\intern 1"

  3. Deploy using full configuration:
     docker-compose up -d

  4. Wait 5-10 minutes for images to build and services to start

  5. Initialize database:
     docker-compose exec app python database.py

  6. Verify deployment:
     docker ps
     curl http://localhost:8000/api/v1/health

  7. Access the API:
     → Browser: http://localhost:8000/docs
     → API: http://localhost:8000/api/v1/tag-content

  8. Stop services when done:
     docker-compose down

================================================================================
📊 DOCKER COMMANDS CHEAT SHEET
================================================================================

# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View logs
docker-compose logs -f           # All services
docker-compose logs -f app       # Just API
docker-compose logs -f postgres  # Just database
docker-compose logs -f redis     # Just Redis

# Stop services
docker-compose down

# Stop services and remove volumes
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Execute command in container
docker-compose exec app python test_api.py

# View container resource usage
docker stats

# Clean up all unused Docker resources
docker system prune -a

================================================================================
🔍 TROUBLESHOOTING
================================================================================

Problem: "Docker daemon is not running"
Solution: 
  Windows/Mac: Open Docker Desktop application
  Linux: sudo systemctl start docker

Problem: "Port 8000 already in use"
Solution Option 1: Find and stop the process
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F

  # Mac/Linux
  lsof -i :8000
  kill -9 <PID>

Solution Option 2: Use different port (edit docker-compose.yml)
  ports:
    - "8001:8000"  # Access at http://localhost:8001

Problem: "Insufficient disk space"
Solution:
  docker system df          # Check usage
  docker system prune -a    # Remove unused images

Problem: Build fails with "module not found"
Solution:
  docker-compose build --no-cache
  docker-compose pull

Problem: Database connection error
Solution: Wait longer for services to start (30-60 seconds)
  docker-compose logs postgres
  docker-compose logs redis

================================================================================
✅ VERIFICATION CHECKLIST
================================================================================

After deployment, verify:

  □ docker ps shows 3 running containers:
    - tagging-db (PostgreSQL)
    - tagging-cache (Redis)
    - tagging-engine (FastAPI)

  □ Health check returns 200:
    curl http://localhost:8000/api/v1/health

  □ API Swagger UI loads:
    Browser: http://localhost:8000/docs

  □ Can POST to tagging endpoint:
    curl -X POST http://localhost:8000/api/v1/tag-content \\
      -H "Content-Type: application/json" \\
      -d '{"title":"Test","content":"Sample content"}'

  □ Database is accessible:
    docker-compose exec postgres psql -U user -d tagging_db -c "\\dt"

  □ Redis is accessible:
    docker-compose exec redis redis-cli ping

================================================================================
🚀 NEXT STEPS AFTER DEPLOYMENT
================================================================================

1. Access the API Documentation:
   → Open http://localhost:8000/docs in your browser
   → Explore all 8 endpoints interactively

2. Test with Sample Content:
   → Use Swagger UI to send test content
   → Get back tagged results

3. Integrate with Your CMS:
   → Use REST API calls from your platform
   → POST to /api/v1/tag-content
   → Get categories, tags, entities in response

4. Monitor Performance:
   → Check logs: docker-compose logs -f app
   → View container stats: docker stats
   → Test load: ab -n 1000 -c 10 http://localhost:8000/api/v1/health

5. Production Deployment:
   → Change default passwords in .env
   → Enable HTTPS/SSL
   → Use managed database (RDS/Azure Database)
   → Use managed Redis (ElastiCache/Azure Cache)
   → Set up monitoring and logging
   → Configure backups

================================================================================
📞 SUPPORT RESOURCES
================================================================================

Documentation:
  • README.md - Full project documentation
  • DEPLOY_NOW.md - Master deployment guide
  • DOCKER_SETUP.md - Docker setup instructions
  • API Swagger UI: http://localhost:8000/docs

Docker Documentation:
  • Docker Getting Started: https://docs.docker.com/get-started/
  • Docker Compose: https://docs.docker.com/compose/
  • Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/

Project Repository:
  • Files: 40 total
  • Endpoints: 8 REST APIs
  • Dependencies: 21 packages
  • Database: PostgreSQL 15
  • Cache: Redis 7

================================================================================

Ready to deploy? Choose your option above and follow the steps!

For demo deployment (quickest):
  docker-compose -f docker-compose.demo.yml up -d

For full production deployment:
  docker-compose up -d

╔══════════════════════════════════════════════════════════════════════════════╗
║                     Questions? Check the documentation!                      ║
║               All guides available in project root directory                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    return guide

if __name__ == "__main__":
    print(show_docker_deployment_guide())
