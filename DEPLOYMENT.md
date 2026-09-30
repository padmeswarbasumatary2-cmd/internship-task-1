# Deployment Guide: Automated Content Tagging Engine

## Option 1: Local Docker Deployment (Recommended)

### Prerequisites
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
  - Download: https://www.docker.com/products/docker-desktop
  - Windows: Includes Docker and Docker Compose
  - After installation, restart your machine

### Step 1: Verify Installation
```powershell
docker --version
docker-compose --version
```

### Step 2: Start Services
```powershell
cd "c:\Users\radhi\OneDrive\Desktop\intern 1"
docker-compose up -d
```

This will:
- Pull PostgreSQL 15 image
- Pull Redis 7 image  
- Build tagging engine image
- Start all 3 services in the background

### Step 3: Initialize Database
```powershell
docker-compose exec app python database.py
```

### Step 4: Access the Application
- **API Docs**: http://localhost:8000/docs
- **Direct API**: http://localhost:8000
- **Database**: postgresql://localhost:5432 (user: user, password: password)
- **Redis**: redis://localhost:6379

### Step 5: View Logs
```powershell
docker-compose logs -f app
```

### Step 6: Stop Services
```powershell
docker-compose down
```

### Step 7: Clean Up
```powershell
docker-compose down -v  # Remove volumes
docker system prune      # Clean unused images
```

---

## Option 2: Local Development (Without Docker)

### Prerequisites
- Python 3.11+
- PostgreSQL 15 running locally
- Redis 7 running locally

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Configure Environment
```powershell
cp .env.example .env
# Edit .env with your local database/Redis URLs
```

Update `.env` to match your local setup:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/tagging_db
REDIS_URL=redis://localhost:6379/0
```

### Step 3: Initialize Database
```powershell
python database.py
```

### Step 4: Start Application
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Test the API
Visit: http://localhost:8000/docs

---

## Option 3: Deploy to Vercel (Cloud - Serverless)

### Prerequisites
- Vercel Account (https://vercel.com)
- GitHub repository with your code

### Step 1: Create Vercel Configuration
```powershell
# File: vercel.json (create in project root)
```

### Step 2: Modify FastAPI for Serverless
The API needs a serverless handler. Update `app/main.py` to export for Vercel.

### Step 3: Deploy
```powershell
npm install -g vercel
vercel login
vercel
```

**Note**: Vercel requires external PostgreSQL/Redis (e.g., AWS RDS, Railway, Supabase)

---

## Option 4: Deploy to AWS

### Prerequisites
- AWS Account
- AWS CLI configured
- ECR access

### Step 1: Push Image to ECR
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t tagging-engine .
docker tag tagging-engine:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/tagging-engine:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/tagging-engine:latest
```

### Step 2: Launch on ECS/Fargate
1. Create ECS cluster
2. Create task definition (use ECR image)
3. Create service
4. Link RDS PostgreSQL database
5. Link ElastiCache Redis

### Step 3: Configure Load Balancer
- Set up Application Load Balancer (ALB)
- Route traffic to ECS service

---

## Option 5: Deploy to Google Cloud Run (Recommended for Small Projects)

### Prerequisites
- Google Cloud Project
- gcloud CLI installed
- Docker image ready

### Step 1: Authenticate
```bash
gcloud auth login
gcloud config set project <project-id>
```

### Step 2: Push to Google Artifact Registry
```bash
gcloud builds submit --tag gcr.io/<project-id>/tagging-engine
```

### Step 3: Deploy to Cloud Run
```bash
gcloud run deploy tagging-engine \
  --image gcr.io/<project-id>/tagging-engine \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=postgresql://...,REDIS_URL=redis://... \
  --allow-unauthenticated
```

### Step 4: Configure External Services
- Link Cloud SQL (PostgreSQL)
- Link Memorystore (Redis)

---

## Quick Testing After Deployment

### Test Health Endpoint
```powershell
curl http://localhost:8000/api/v1/health
```

### Test Tagging Endpoint
```powershell
$body = @{
    title = "Getting Started with PyTorch"
    content = "PyTorch is a machine learning framework..."
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/tag-content `
  -ContentType "application/json" `
  -Body $body
```

### Access Interactive Docs
Open in browser: http://localhost:8000/docs

---

## Troubleshooting

### Docker won't start
```powershell
docker-compose restart
docker-compose logs app
```

### Database connection failed
```powershell
docker-compose logs postgres
# Check connection string in .env
```

### Redis connection failed
```powershell
docker-compose logs redis
redis-cli ping  # Test Redis directly
```

### Port already in use
```powershell
# Find process using port 8000
Get-NetTcpConnection -LocalPort 8000
# Kill it or use different port in docker-compose.yml
```

### Models not loading
```powershell
docker-compose exec app python -m spacy download en_core_web_sm
```

---

## Production Deployment Checklist

- [ ] Set `DEBUG=False` in production `.env`
- [ ] Use strong database password (not default)
- [ ] Use strong Redis password (if exposed)
- [ ] Enable HTTPS/SSL
- [ ] Set up proper logging and monitoring
- [ ] Configure rate limiting
- [ ] Set up database backups
- [ ] Monitor disk space for model cache
- [ ] Use environment-specific `.env` files
- [ ] Set up CI/CD pipeline
- [ ] Configure health checks
- [ ] Set up alerts for errors
- [ ] Use secrets manager (AWS Secrets, Azure Key Vault)
- [ ] Test disaster recovery procedures

---

## Performance Optimization

### Caching
```powershell
# Redis is automatically integrated
# Tagging results cached for 1 hour (configurable)
```

### Model Optimization
- Convert models to ONNX format (reduces inference time 60-80%)
- Use quantization (INT8) for smaller model size
- Batch inference for multiple documents

### Database Optimization
- Add indexes on frequently queried columns
- Use connection pooling (SQLAlchemy does this by default)
- Monitor slow queries with `django-extensions` or similar

### API Optimization
- Use async endpoints (already implemented)
- Enable gzip compression
- Add CDN for static assets (if applicable)

---

## Monitoring & Logging

### Application Logs
```powershell
docker-compose logs -f app
```

### Database Performance
```sql
-- Connect to PostgreSQL
SELECT * FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;
```

### Redis Monitoring
```bash
redis-cli INFO
redis-cli MONITOR
```

### Metrics to Track
- API response time
- Cache hit rate
- Database query time
- Model inference time
- Error rates
- Uptime

---

## Support & Issues

For deployment issues:
1. Check logs: `docker-compose logs`
2. Verify environment: `.env` file
3. Test services independently
4. Consult documentation in `README.md`

Happy deploying! 🚀
