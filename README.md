# Recipe Suggester

A smart recipe recommendation system that helps you create recipes from the ingredients in your fridge. Take a photo of your fridge, and the app will detect the ingredients and suggest complete recipes using AI.

The project is currently hosted on the net is available at the [following link](https://recipe-suggester-frontend-production.up.railway.app).
A public available video of the working product is available at the [following link](https://drive.google.com/file/d/1Wyz_gT-FHCGT5w7Ww_xG_3vV4ZQyfCFI/view?usp=sharing)

**Course Project:** 440MI - Machine Learning Operations @ University of Trieste

**Team members:**
- Baratto Luca
- Moro Tommaso
- Savorgnan Enrico

## What Does It Do?

1. **Upload a fridge photo** - Take a picture of your fridge or ingredients
2. **AI detects ingredients** - YOLO model identifies what you have
3. **Edit if needed** - Review and modify the detected ingredients
4. **Get a recipe** - OpenAI generates a complete recipe with instructions
5. **Cook and enjoy!** 

## Architecture

The application is built using a **microservice architecture** with three main services:

```
┌─────────────────┐
│   Frontend      │  React + TypeScript (Port 3000)
│   (React SPA)   │  - User interface
└────────┬────────┘  - Image upload
         │           - Recipe display
         ▼
┌─────────────────┐
│   Backend       │  FastAPI + Python (Port 8000)
│   (REST API)    │  - Authentication (Google OAuth)
└────┬───────┬────┘  - Database operations
     │       │       - Job orchestration
     │       │       - Calls Models & LLM services
     │       │
     │       └──────────────────┐
     │                          ▼
     │                 ┌─────────────────┐
     │                 │  Models Service │  FastAPI + YOLO (Port 8001)
     │                 │  (ML Service)   │  - Ingredient detection
     │                 └─────────────────┘  - YOLO inference
     │                                      - Image processing
     │
     ▼
┌─────────────────┐
│   PostgreSQL    │  Database (Port 5432)
│   (Database)    │  - Users & recipes
└─────────────────┘  - Detection jobs
```

## How It Works - Complete Flow

### Step 1: User Uploads Fridge Photo

1. Frontend → Backend: 
```
POST /recipes (with image file)
```
- Saves image to shared volume (uploads/recipes/)
- Creates Recipe in database
- Creates IngredientsJob (status: running)
- Returns recipe_id and job_id to frontend

### Step 2: Ingredient Detection (Background)

1. Backend → Models Service: 
```
POST /predict
Body: {"image_path": "uploads/recipes/photo.jpg"}
```
- Models service loads image from shared volume
- Runs YOLOv11 inference
- Returns: `{"ingredients": [{"name": "Tomato", "confidence": 0.95}, ...]}`
2. Backend saves ingredients to IngredientsJob
3. Updates job status to "completed"

**Note:** Frontend polls the backend every second to check if the job is complete.

### Step 3: User Reviews Ingredients

1. Frontend displays detected ingredients
2. User can add, edit, or remove ingredients
3. User clicks "Confirm & Generate Recipe"

### Step 4: Recipe Generation

Frontend → Backend: 
```
POST /recipes/{id}/recipe-job
Body: {ingredients: [...]}
```
1. Backend creates RecipeJob (status: running)
2. Calls OpenAI API with ingredient list
3. OpenAI generates recipe with:
- Title
- Difficulty level
- Cooking time
- Ingredients list
- Step-by-step instructions
4. Saves recipe JSON to RecipeJob
5. Updates Recipe.title with generated title
6. Updates job status to "completed"

**Note:** Frontend polls until recipe generation is complete.

### Step 5: Display Recipe

1. Frontend fetches completed RecipeJob
2. Displays the complete recipe to the user
3. User can view ingredients, cooking time, difficulty, and instructions

### Extra: old recipes visualization

1. The Recipe table contains the recipes
2. In the frontend, in the sidebar user can see the list of past recipes and visualize them
3. User can manage recipes assigning them to categories for more organization

## Quick Start

### Local Development

To run the application locally for development:

1. **Start the database:**
   ```bash
   docker-compose up postgres -d
   ```

2. **Start the models service:**
   ```bash
   cd code/models
   pip install -r requirements.txt
   uvicorn app:app --reload --port 8001
   ```

3. **Start the backend:**
   ```bash
   cd code/backend
   cp .env.example .env
   # Edit .env with your credentials
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload --port 8000
   ```

4. **Start the frontend:**
   ```bash
   cd code/frontend
   npm install
   npm run dev
   ```

5. **Access the app:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - Models Service: http://localhost:8001/docs

See individual component READMEs for more details:
- [Backend](./code/backend/README.md)
- [Frontend](./code/frontend/README.md)
- [Models](./code/models/README.md)

### Deployment (Docker)

Deploy the entire application with Docker Compose. This will run all services (frontend, backend, models, database) in containers.

#### Prerequisites

You need to obtain API credentials:

1. **Google OAuth credentials** from [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 Client ID
   - Add `http://localhost:8000/auth/google/callback` to authorized redirect URIs

2. **OpenAI API key** from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Used for recipe generation

#### Deployment Steps

1. **Configure environment variables:**

   a. Root `.env` (optional - for Docker Compose settings):
   ```bash
   cp .env.example .env
   # Only needed if you want to change GITHUB_REPO_OWNER or database credentials
   ```

   b. Backend `.env` (REQUIRED - API credentials):
   ```bash
   cp code/backend/.env.example code/backend/.env
   ```

   Edit `code/backend/.env` and fill in:
   - `GOOGLE_CLIENT_ID` - Your Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET` - Your Google OAuth client secret
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `SECRET_KEY` - Generate with: `openssl rand -hex 32`

2. **Pull the latest Docker images:**
   ```bash
   docker-compose pull
   ```

   This downloads pre-built images from GitHub Container Registry (frontend, backend, models).

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

   Docker Compose will start:
   - PostgreSQL database (port 5432)
   - Models service (port 8001)
   - Backend API (port 8000)
   - Frontend (port 3000)

4. **Access the application:**
   - **Frontend**: http://localhost:3000
   - **Backend API docs**: http://localhost:8000/docs
   - **Models API docs**: http://localhost:8001/docs

### Possible errors

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
├── docker-compose.yml              # Orchestrates all services
├── .env.example                    # Docker Compose config template
├── .github/
│   └── workflows/
│       ├── ci.yml                 # CI: Tests, linting, Docker builds
│       └── cd.yml                 # CD: Build & push images to registry
├── docs/                          # Project documentation
└── code/
    ├── backend/                   # Backend API service
    ├── frontend/                  # Frontend web application 
    └── models/                    # ML models service
```

## CI/CD Pipeline

### Continuous Integration (Pull Requests)

On every pull request to `main`:
- **Backend**: Unit tests, linting (Ruff), test coverage
- **Frontend**: TypeScript type checking, build validation
- **Models**: Python syntax validation, file checks, model quality
- **Docker**: Build validation for all 3 services (backend, frontend, models)

All checks must pass before merging.

### Continuous Deployment (Main Branch)

On every push to `main`:
1. **Build** Docker images for all services
2. **Tag** with `latest` and `main-<git-sha>`
3. **Push** to GitHub Container Registry at `ghcr.io/{owner}/recipe-suggester-{service}:latest`

Published images:
- `ghcr.io/{owner}/recipe-suggester-backend:latest`
- `ghcr.io/{owner}/recipe-suggester-frontend:latest`
- `ghcr.io/{owner}/recipe-suggester-models:latest`

See [CI/CD docs](./docs/cicd.md) for details.

## Datasets

The dataset used to fine-tune the detection model (YOLOv11 nano) is made up of 4 different datasets provided by Roboflow.

- [Roboflow – group_work dataset](https://universe.roboflow.com/computer-vision-group-ji0bm/group_work/dataset/3)
- [Roboflow – Food Item Detection](https://universe.roboflow.com/coretus/food-item-detection-fggyf/dataset/1)
- [Roboflow – Fridgify](https://universe.roboflow.com/workspace01-ae0oa/fridgify/dataset/3)
- [Roboflow – Cook AI](https://universe.roboflow.com/fridgedetector/cook-ai/dataset/2)
