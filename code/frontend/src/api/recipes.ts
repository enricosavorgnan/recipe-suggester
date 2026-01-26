import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Recipe {
  id: number;
  title: string;
  image: string | null;
  user_id: number;
  category_id: number | null;
  created_at: string;
}

export interface UpdateRecipeTitleRequest {
  title: string;
}

const recipesApi = {
  getRecipes: async (token: string, categoryId?: number | null): Promise<Recipe[]> => {
    const params = categoryId !== undefined && categoryId !== null ? { category_id: categoryId } : {};
    const response = await axios.get(`${API_URL}/recipes`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      params,
    });
    return response.data;
  },

  updateRecipeTitle: async (
    recipeId: number,
    data: UpdateRecipeTitleRequest,
    token: string
  ): Promise<Recipe> => {
    const response = await axios.patch(`${API_URL}/recipes/${recipeId}`, data, {
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

  createRecipe: async (token: string): Promise<Recipe> => {
    const response = await axios.post(`${API_URL}/recipes`, {}, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  uploadImage: async (recipeId: number, file: File, token: string): Promise<Recipe> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_URL}/recipes/${recipeId}/upload`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default recipesApi;
