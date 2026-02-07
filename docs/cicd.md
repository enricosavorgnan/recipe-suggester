# CI/CD Pipeline Documentation

## Overview

This project uses GitHub Actions for continuous integration and deployment.

## Architecture

```
1. Pull Request
2. CI (test, lint, build)
3. Review
4. Merge
5. Main Branch
6. CD (build images, push to registry)
7. Local Deployment (docker-compose pull & up)
```

## Workflows

### CI Workflow (`.github/workflows/ci.yml`)

**Triggers:** Pull requests to `main` branch

**Jobs:**

1. **Backend Tests & Lint**
   - Python 3.11
   - Install dependencies
   - Lint with Ruff
   - Run tests (placeholder for pytest)
   - Type checking (placeholder for mypy)

2. **Frontend Build & Lint**
   - Node.js 20
   - Install dependencies
   - Lint (placeholder for ESLint)
   - Type check with TypeScript
   - Build with Vite
   - Upload build artifacts

3. **Docker Build Test**
   - Test backend Docker build
   - Test frontend Docker build
   - Use build cache for speed

### CD Workflow (`.github/workflows/cd.yml`)

**Triggers:** Pushes to `main` branch

**Jobs:**

1. **Build & Push Backend Image**
   - Build backend Docker image
   - Tag with `latest` and `main-<sha>`
   - Push to GitHub Container Registry

2. **Build & Push Frontend Image**
   - Build frontend Docker image
   - Tag with `latest` and `main-<sha>`
   - Push to GitHub Container Registry

3. **Deployment Summary**
   - Print deployment information
   - Show docker-compose commands

## Container Registry

Images are published to **GitHub Container Registry (ghcr.io)**:

- Backend: `ghcr.io/enricosavorgnan/recipe-suggester-backend:latest`
- Frontend: `ghcr.io/enricosavorgnan/recipe-suggester-frontend:latest`

## Tagging Strategy

| Tag | Description | Example |
|-----|-------------|---------|
| `latest` | Latest build from main | `latest` |
| `main-<sha>` | Specific commit from main | `main-a1b2c3d` |

## Local Deployment

After images are published by CD, deploy locally:

1. **Set GitHub username in environment:**
   ```bash
   echo "GITHUB_REPO_OWNER=enricosavorgnan" >> .env
   ```

2. **Authenticate with GitHub Container Registry:**
   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
   ```

   Or use a Personal Access Token with `read:packages` permission.

3. **Pull latest images:**
   ```bash
   docker-compose pull
   ```

4. **Start services:**
   ```bash
   docker-compose up -d
   ```

5. **View logs:**
   ```bash
   docker-compose logs -f
   ```

6. **Stop services:**
   ```bash
   docker-compose down
   ```

## Docker Images

### Backend (`code/backend/Dockerfile`)

- Base: `python:3.11-slim`
- Multi-stage build for smaller image
- Includes PostgreSQL client
- Runs uvicorn on port 8000
- Health check on `/health` endpoint

### Frontend (`code/frontend/Dockerfile`)

- Build stage: `node:20-alpine`
- Production: `nginx:alpine`
- Builds React app with Vite
- Serves static files on port 80
- Health check via wget

## Environment Variables

See `docker-compose.yml` for configuration:

- `GITHUB_REPO_OWNER` - Your GitHub username (required)
- `POSTGRES_USER` - Database user (default: postgres)
- `POSTGRES_PASSWORD` - Database password (default: postgres)
- `POSTGRES_DB` - Database name (default: recipe_suggester)
- `DEBUG` - Debug mode (default: False in deployment)

## Making Changes

1. **Create feature branch:**
   ```bash
   git checkout -b feat/your-feature
   ```

2. **Make changes and commit**

3. **Push and open PR:**
   ```bash
   git push origin feat/your-feature
   ```

4. **CI runs automatically** - checks must pass

5. **After merge to main:**
   - CD builds and pushes images
   - Pull and deploy locally

