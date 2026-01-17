import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <nav className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Recipe Suggester
            </h1>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center text-white font-semibold">
                  {(user?.full_name || user?.email || 'U')[0].toUpperCase()}
                </div>
                <span className="text-gray-700 font-medium hidden sm:block">
                  {user?.full_name || user?.email}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-semibold text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-gray-100">
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Hello World
          </h2>
          <p className="text-gray-600 text-lg">Welcome to your dashboard!</p>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
