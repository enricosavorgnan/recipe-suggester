import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface SignupRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

const authApi = {
  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    const response = await axios.post(`${API_URL}/auth/signup`, data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await axios.post(`${API_URL}/auth/login`, data);
    return response.data;
  },

  getCurrentUser: async (token: string): Promise<User> => {
    const response = await axios.get(`${API_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  getGoogleAuthUrl: async (): Promise<string> => {
    const response = await axios.get(`${API_URL}/auth/google`);
    return response.data.authorization_url;
  },

  googleCallback: async (code: string): Promise<AuthResponse> => {
    const response = await axios.post(`${API_URL}/auth/google/callback`, { code });
    return response.data;
  },
};

export default authApi;
