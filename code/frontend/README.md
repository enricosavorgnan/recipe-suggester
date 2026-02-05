# Recipe Suggester - Frontend

React application for the Recipe Suggester. Represents the UI for uploading fridge photos, detecting ingredients, and generating recipes with AI.

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Fast build tool and dev server
- **TanStack Query** - Data fetching and caching
- **React Router** - Client-side routing
- **shadcn/ui** - UI component library
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx                    # App entry point
│   ├── App.tsx                     # Root component with routing
│   ├── pages/                      # Page components
│   │   ├── Dashboard.tsx           # Main recipe management page
│   │   ├── Login.tsx               # Login page
│   │   ├── Signup.tsx              # Registration page
│   │   └── GoogleCallback.tsx      # OAuth callback
│   ├── components/                 # Reusable components
│   │   ├── ImageUpload.tsx         # Image upload and ingredient detection
│   │   ├── RecipeDetail.tsx        # Recipe view and generation
│   │   ├── Sidebar.tsx             # Recipe list sidebar
│   │   ├── RecipeDisplay.tsx       # Display generated recipe
│   │   ├── IngredientItem.tsx      # Single ingredient display
│   │   └── ui/                     # shadcn/ui components
│   ├── contexts/
│   │   └── AuthContext.tsx         # Authentication state
│   ├── api/                        # API client functions
│   │   ├── auth.ts
│   │   ├── recipes.ts
│   │   ├── jobs.ts
│   │   └── categories.ts
│   └── lib/
│       └── utils.ts                # Utility functions
├── public/                         # Static assets
├── index.html
├── package.json
├── vite.config.ts
└── tailwind.config.ts
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000` (or configure `VITE_API_URL`)

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd code/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment** (optional)

   Create `.env` file if you need to override defaults:
   ```bash
   VITE_API_URL=http://localhost:8000
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

## Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

## Configuration

The frontend connects to the backend API. Configure the API URL using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` |

Create a `.env` file in the frontend directory to override defaults.

## How It Works

### User Flow

1. **Login/Signup**: User authenticates (email/password or Google OAuth)
2. **Recipe creation**: From the left sidebar, user can create a recipe and assign it to a category
3. **Upload Image**: User uploads a photo of their fridge/ingredients
4. **Detect Ingredients**: ML model detects ingredients from the image
5. **Edit Ingredients**: User can add, edit, or remove detected ingredients
6. **Generate Recipe**: LLM creates a recipe based on the ingredients
7. **View Recipe**: Display the generated recipe with instructions

### State Management

- **Authentication**: React Context (`AuthContext`)
- **Server State**: TanStack Query for API data
- **Local State**: React hooks for UI state

## API Integration

The frontend communicates with the backend through API modules in `src/api/`:

- **auth.ts**: Login, signup, Google OAuth
- **recipes.ts**: CRUD operations for recipes
- **jobs.ts**: Create and check status of ML/LLM jobs
- **categories.ts**: Organize recipes into categories

Each API call includes the JWT token from `AuthContext` for authentication.

## Contributing

### Code Organization

- **Keep components small**: Each component should do one thing
- **Use TypeScript**: Define interfaces for all props and data
- **Follow React Query patterns**: Use hooks for data fetching
- **Centralize API calls**: All backend communication goes through `src/api/`

### Adding a New Feature

1. Create API functions in `src/api/` if needed
2. Build UI components in `src/components/`
3. Add page component in `src/pages/` if needed
4. Update routing in `App.tsx` if needed
5. Use TanStack Query for server state
6. Handle loading and error states

### UI Components

This project uses [shadcn/ui](https://ui.shadcn.com/) for UI components. To add a new component:

```bash
npx shadcn@latest add [component-name]
```

All components are in `src/components/ui/` and can be customized.
