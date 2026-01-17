import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const GoogleCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { handleGoogleCallback } = useAuth();

  useEffect(() => {
    const code = searchParams.get('code');
    if (code) {
      handleGoogleCallback(code)
        .then(() => {
          navigate('/dashboard');
        })
        .catch(() => {
          navigate('/login?error=google_auth_failed');
        });
    } else {
      navigate('/login?error=no_code');
    }
  }, [searchParams, navigate, handleGoogleCallback]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Completing sign in...</p>
      </div>
    </div>
  );
};

export default GoogleCallback;
