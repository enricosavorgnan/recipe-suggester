import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import authApi, { User, SignupRequest, LoginRequest } from '../api/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  signup: (data: SignupRequest) => Promise<void>;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => void;
  loginWithGoogle: () => Promise<void>;
  handleGoogleCallback: (code: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await authApi.getCurrentUser(token);
          setUser(userData);
        } catch (error) {
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const signup = async (data: SignupRequest) => {
    const response = await authApi.signup(data);
    setToken(response.access_token);
    setUser(response.user);
    localStorage.setItem('token', response.access_token);
  };

  const login = async (data: LoginRequest) => {
    const response = await authApi.login(data);
    setToken(response.access_token);
    setUser(response.user);
    localStorage.setItem('token', response.access_token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };

  const loginWithGoogle = async () => {
    const authUrl = await authApi.getGoogleAuthUrl();
    window.location.href = authUrl;
  };

  const handleGoogleCallback = async (code: string) => {
    const response = await authApi.googleCallback(code);
    setToken(response.access_token);
    setUser(response.user);
    localStorage.setItem('token', response.access_token);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, signup, login, logout, loginWithGoogle, handleGoogleCallback }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
