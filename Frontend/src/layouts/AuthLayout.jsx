import { Link } from 'react-router-dom';
import { Outlet } from 'react-router-dom';

function AuthLayout() {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Auth Navbar */}
      <nav className="bg-transparent absolute top-0 left-0 right-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex-shrink-0">
              <Link to="/" className="flex items-center">
                <span className="text-2xl font-bold bg-clip-text text-transparent 
                               bg-gradient-to-r from-purple-400 to-pink-600
                               hover:from-pink-600 hover:to-purple-400 
                               transition-all duration-300">
                  VoyageView
                </span>
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-300 hover:text-white px-4 py-2 text-sm 
                         hover:bg-gray-800/50 rounded-lg transition-all duration-300"
              >
                Giriş Yap
              </Link>
              <Link
                to="/register"
                className="bg-gradient-to-r from-purple-600 to-pink-600
                         hover:from-purple-700 hover:to-pink-700
                         text-white px-4 py-2 rounded-lg text-sm
                         transition-all duration-300 hover:shadow-lg 
                         hover:shadow-purple-500/25"
              >
                Kayıt Ol
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        <Outlet />
      </main>
    </div>
  );
}

export default AuthLayout; 