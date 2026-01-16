# Deployment Guide

## Overview

This project uses Docker for packaging and GitHub Container Registry for distribution. Deployment is intentionally local to avoid cloud costs while demonstrating MLOps principles.

## Prerequisites

- Docker & Docker Compose installed
- GitHub account
- Git configured

## First-Time Setup

### 1. Make Container Registry Packages Public

After the first CD run, make your packages public:

1. Go to GitHub → Your Profile → Packages
2. Find `recipe-suggester-backend` and `recipe-suggester-frontend`
3. Package Settings → Change visibility → Public

This allows pulling images without authentication.

### 2. Configure Local Environment

Create `.env` in project root:

```bash
cp .env.example .env
```

Edit `.env` and set your GitHub username:

```bash
GITHUB_REPO_OWNER=your-github-username
```

## Deployment Workflow

### Development Cycle

```bash
# 1. Create feature branch
git checkout -b feat/my-feature

# 2. Make changes
# ... edit code ...

# 3. Test locally
cd code/backend && uvicorn app.main:app --reload
cd code/frontend && npm run dev

# 4. Commit and push
git add .
git commit -m "feat: add my feature"
git push origin feat/my-feature

# 5. Open PR on GitHub
# CI runs automatically - must pass

# 6. Merge PR
# CD builds and pushes images to ghcr.io
```

### Deploy Latest Changes

After PR is merged and CD completes:

```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Common Commands

### Starting Services

```bash
# Start all services in background
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up -d backend
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last N lines
docker-compose logs --tail=100 backend
```

### Rebuilding Locally

If you want to test Docker builds locally:

```bash
# Backend
cd code/backend
docker build -t recipe-suggester-backend:local .

# Frontend
cd code/frontend
docker build -t recipe-suggester-frontend:local .
```

## Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Web interface |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Database | localhost:5432 | PostgreSQL |

## Eventual Troubleshooting

### Images Won't Pull

**Error:** `unauthorized: authentication required`

**Solution:** Make packages public (see First-Time Setup) or authenticate:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Port Already in Use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:** Stop conflicting service or change port in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Map to different host port
```

### Database Connection Failed

**Error:** Backend can't connect to database

**Solution:** Ensure postgres service is healthy:

```bash
docker-compose ps
docker-compose logs postgres
```

If needed, restart:

```bash
docker-compose restart postgres
docker-compose restart backend
```

### Service Won't Start

Check logs for errors:

```bash
docker-compose logs backend
docker-compose logs frontend
```

Common issues:
- Missing environment variables
- Database not ready (wait for healthcheck)
- Build errors (check Dockerfile)

### Clear Everything and Start Fresh

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker rmi ghcr.io/$GITHUB_REPO_OWNER/recipe-suggester-backend:latest
docker rmi ghcr.io/$GITHUB_REPO_OWNER/recipe-suggester-frontend:latest

# Pull and start fresh
docker-compose pull
docker-compose up -d
```

## Image Tagging Strategy

| Tag | When Created | Use Case |
|-----|--------------|----------|
| `latest` | Every main branch push | Normal deployment |
| `main-<sha>` | Every main branch push | Rollback to specific version |

### Rolling Back

To deploy a specific version:

```bash
# Find commit SHA from git log or GitHub
git log --oneline

# Update docker-compose.yml to use specific tag:
# image: ghcr.io/${GITHUB_REPO_OWNER}/recipe-suggester-backend:main-abc1234

# Pull and deploy
docker-compose pull
docker-compose up -d
```

## Production Considerations

This setup is for educational/local use. For a hypotetical production:

- Use secrets management (not .env files)
- Set up HTTPS/TLS
- Configure proper CORS origins
- Use managed database (not local volume)
- Set up monitoring and logging
- Implement backup strategy
- Use orchestration (Kubernetes, etc.)
