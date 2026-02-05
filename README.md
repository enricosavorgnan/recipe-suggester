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
```bash
# 1. Set GitHub username
echo "GITHUB_REPO_OWNER=your-username" > .env

# 2. Pull latest images from registry
docker-compose pull

# 3. Start services
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

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
    └── models/            # ML models (TODO)
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
