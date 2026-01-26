import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface IngredientsJob {
  id: number;
  recipe_id: number;
  status: 'running' | 'completed' | 'failed';
  ingredients_json: string | null;
  start_time: string;
  end_time: string | null;
}

export interface RecipeJob {
  id: number;
  recipe_id: number;
  status: 'running' | 'completed' | 'failed';
  recipe_json: string | null;
  start_time: string;
  end_time: string | null;
}

const jobsApi = {
  createIngredientsJob: async (recipeId: number, token: string): Promise<IngredientsJob> => {
    const response = await axios.post(`${API_URL}/jobs/ingredients/${recipeId}`, {}, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  getIngredientsJob: async (jobId: number, token: string): Promise<IngredientsJob> => {
    const response = await axios.get(`${API_URL}/jobs/ingredients/${jobId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  createRecipeJob: async (recipeId: number, token: string): Promise<RecipeJob> => {
    const response = await axios.post(`${API_URL}/jobs/recipe/${recipeId}`, {}, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  getRecipeJob: async (jobId: number, token: string): Promise<RecipeJob> => {
    const response = await axios.get(`${API_URL}/jobs/recipe/${jobId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },
};

export default jobsApi;
