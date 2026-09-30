# 🐳 Docker Deployment Checklist

## Step 1: Install Docker (if not already installed)

### Windows 10/11:
1. Download: https://www.docker.com/products/docker-desktop
2. Run installer (Docker Desktop Setup.exe)
3. Enable WSL 2 (Windows Subsystem for Linux)
4. Restart computer
5. Launch Docker Desktop
6. Wait for Docker to start (~2-3 minutes)

### Mac:
1. Download: https://www.docker.com/products/docker-desktop
2. Open DMG file
3. Drag Docker icon to Applications
4. Launch Docker from Applications

### Linux:
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

## Step 2: Verify Installation

```bash
docker --version
docker-compose --version
docker ps
```

All three should return output without errors.

## Step 3: Deploy with Docker

### Option A: Full Production Deploy (with all ML dependencies)
```bash
cd "c:\Users\radhi\OneDrive\Desktop\intern 1"
docker-compose up -d
```
**Time**: 5-10 minutes (builds all dependencies)
**Size**: ~3-4 GB disk space

### Option B: Quick Demo Deploy (lightweight, no ML dependencies)
```bash
cd "c:\Users\radhi\OneDrive\Desktop\intern 1"
docker-compose -f docker-compose.demo.yml up -d
```
**Time**: 1-2 minutes
**Size**: ~300 MB disk space
**Includes**: PostgreSQL, Redis, API (demo mode)

## Step 4: Verify Deployment

Wait 10-20 seconds, then check:

```bash
# See running containers
docker ps

# Check API health
curl http://localhost:8000/api/v1/health

# View logs
docker-compose logs -f app

# Stop containers
docker-compose down
```

## Step 5: Access the Application

Open browser: **http://localhost:8000/docs**

You can:
- See all 8 API endpoints
- Try endpoints interactively
- Send test content for tagging
- View response schemas

## Troubleshooting

### Issue: "Docker daemon is not running"
- Windows: Start Docker Desktop from Start Menu
- Linux: `sudo systemctl start docker`

### Issue: "Port 8000 already in use"
Option 1: Stop the conflicting service
```bash
# Find what's using port 8000
netstat -ano | findstr :8000  (Windows)
lsof -i :8000  (Mac/Linux)

# Kill the process
taskkill /PID <PID> /F  (Windows)
kill -9 <PID>  (Mac/Linux)
```

Option 2: Use a different port
Edit docker-compose.yml:
```yaml
ports:
  - "8001:8000"  # Access at http://localhost:8001
```

### Issue: "Insufficient disk space"
- Full deploy: Need 3-4 GB
- Demo deploy: Need 300-500 MB
- Check: `docker system df`
- Cleanup: `docker system prune -a`

### Issue: Build fails
Try pulling the latest images:
```bash
docker-compose pull
docker-compose build --no-cache
```

### Issue: Database connection error
Wait longer for services to start (30-60 seconds):
```bash
docker-compose logs postgres
docker-compose logs redis
```

## Command Reference

```bash
# Start containers (demo)
docker-compose -f docker-compose.demo.yml up -d

# Start containers (full)
docker-compose up -d

# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View logs
docker-compose logs -f         # All services
docker-compose logs -f app     # Just API
docker-compose logs -f postgres  # Just database

# Execute command in container
docker-compose exec app python test_api.py

# Stop containers
docker-compose down

# Remove all volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Push image to registry
docker tag tagging-engine:latest myregistry/tagging-engine:latest
docker push myregistry/tagging-engine:latest
```

## Production Checklist

Before going to production:
- [ ] Change default passwords in .env
- [ ] Enable HTTPS/SSL
- [ ] Set DEBUG=False
- [ ] Configure proper database credentials
- [ ] Set up backups
- [ ] Configure monitoring/logging
- [ ] Load test the API
- [ ] Use production-grade database (managed RDS/Azure Database)
- [ ] Use production-grade Redis (ElastiCache/Azure Cache)
- [ ] Enable container restart policies
- [ ] Set up CI/CD pipeline
- [ ] Document deployment procedure

## Next Steps

1. Install Docker if needed (5-10 minutes)
2. Run deployment command (1-10 minutes depending on option)
3. Open http://localhost:8000/docs
4. Test the API with sample content
5. Integrate with your CMS platform

---

**Ready to deploy?**

```bash
# Quick demo (recommended for testing)
docker-compose -f docker-compose.demo.yml up -d

# Full production
docker-compose up -d
```
