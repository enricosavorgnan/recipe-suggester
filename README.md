# Recipe Suggester
A Recipe Suggester Tool developed as the final project for the course of 440MI - Machine Learning Operations @ University of Trieste.

Students:
- Baratto Luca
- Moro Tommaso
- Savorgnan Enrico

## Quick Start

### Local Development
See individual component READMEs for detailed explanations:
- [Backend](./code/backend/README.md)
- [Frontend](./code/frontend/README.md)

### Deployment (Docker)

#### Prerequisites
Before deploying with Docker, you need to obtain:
1. **Google OAuth credentials** from [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 Client ID
   - Add `http://localhost:8000/auth/google/callback` to authorized redirect URIs
2. **OpenAI API key** from [OpenAI Platform](https://platform.openai.com/api-keys)

#### Deployment Steps

1. **Configure environment variables**:

   a. **Root `.env`** (for Docker Compose - optional):
   ```bash
   cp .env.example .env
   # Edit if needed - only contains GITHUB_REPO_OWNER and database credentials
   ```

   b. **Backend `.env`** (REQUIRED - contains OAuth, OpenAI, etc.):
   ```bash
   cp code/backend/.env.example code/backend/.env
   # Edit and fill in REQUIRED credentials:
   # - GOOGLE_CLIENT_ID
   # - GOOGLE_CLIENT_SECRET
   # - OPENAI_API_KEY
   # - SECRET_KEY (generate with: openssl rand -hex 32)
   ```

2. **Pull latest images** from GitHub Container Registry:
   ```bash
   docker-compose pull
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

#### Possible errors

**Google OAuth not configured error:**
- Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in `code/backend/.env`
- Verify the redirect URI `http://localhost:8000/auth/google/callback` is added in Google Cloud Console

**Recipe generation fails:**
- Ensure `OPENAI_API_KEY` is valid and has sufficient credits in `code/backend/.env`
- Check backend logs: `docker-compose logs backend`

**Database connection errors:**
- Wait for postgres container to be healthy: `docker-compose ps`
- Check logs: `docker-compose logs postgres`

## Project Structure
```
recipe-suggester/
├── README.md
├── docker-compose.yml       # Local deployment
├── .github/
│   └── workflows/
│       ├── ci.yml          # PR validation
│       └── cd.yml          # Build & push images
├── docs/
│   ├── requirements.md
│   ├── project_proposal.md
│   └── cicd.md            # CI/CD documentation
└── code/
    ├── backend/           # FastAPI backend
    ├── frontend/          # React frontend
    └── models/            # ML models
```

## CI/CD Pipeline

**CI (Pull Requests):**
- Backend: Tests, lint, type check
- Frontend: Build, lint, type check
- Docker: Build validation

**CD (Main branch):**
- Build Docker images
- Tag: `latest` and `main-<sha>`
- Push to GitHub Container Registry

See [CI/CD docs](./docs/cicd.md) for details.

## Datasets
- Vegetables Dataset: [https://images.cv/dataset/vegetables-image-classification-dataset]
- Fruits Dataset: [https://www.kaggle.com/datasets/moltean/fruits]
- Fish Dataset: [https://www.kaggle.com/datasets/markdaniellampa/fish-dataset]
- Meat Dataset: [https://universe.roboflow.com/sages/meat-a9qkz/dataset/1/images?split=train]
- Fridgy Dataset: [https://universe.roboflow.com/workspace01-ae0oa/fridgify/dataset/4] [https://universe.roboflow.com/project/cook-ai/dataset/2]
