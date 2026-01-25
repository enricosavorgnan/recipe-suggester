import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Recipe {
  id: number;
  title: string;
  image_url: string | null;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface UpdateRecipeTitleRequest {
  title: string;
}

const recipesApi = {
  getRecipes: async (token: string): Promise<Recipe[]> => {
    const response = await axios.get(`${API_URL}/recipes`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  updateRecipeTitle: async (
    recipeId: number,
    data: UpdateRecipeTitleRequest,
    token: string
  ): Promise<Recipe> => {
    const response = await axios.put(`${API_URL}/recipes/${recipeId}`, data, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  deleteRecipe: async (recipeId: number, token: string): Promise<void> => {
    await axios.delete(`${API_URL}/recipes/${recipeId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },
};

export default recipesApi;
