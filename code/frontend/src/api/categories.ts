import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Category {
  id: number;
  name: string;
  created_at: string;
}

export interface CategoryCreateRequest {
  name: string;
}

export interface CategoryUpdateRequest {
  name: string;
}

export interface AssignCategoryRequest {
  recipe_ids: number[];
  category_id: number | null;
}

const categoriesApi = {
  getCategories: async (token: string): Promise<Category[]> => {
    const response = await axios.get(`${API_URL}/categories`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  createCategory: async (data: CategoryCreateRequest, token: string): Promise<Category> => {
    const response = await axios.post(`${API_URL}/categories`, data, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  updateCategory: async (
    categoryId: number,
    data: CategoryUpdateRequest,
    token: string
  ): Promise<Category> => {
    const response = await axios.patch(`${API_URL}/categories/${categoryId}`, data, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  deleteCategory: async (categoryId: number, token: string): Promise<void> => {
    await axios.delete(`${API_URL}/categories/${categoryId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  assignCategories: async (data: AssignCategoryRequest, token: string): Promise<any> => {
    const response = await axios.post(`${API_URL}/categories/assign`, data, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },
};

export default categoriesApi;
