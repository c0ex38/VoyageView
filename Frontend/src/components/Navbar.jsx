import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';
import { 
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  Cog6ToothIcon,
  PencilSquareIcon,
  RssIcon,
  FireIcon,
  HomeIcon,
  BookOpenIcon
} from '@heroicons/react/24/outline';

function Navbar() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, tokens } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleLogout = async () => {
    if (!tokens?.access) {
      toast.error('Oturum bilgisi bulunamadı');
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/users/logout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens.access}`,
        },
        body: JSON.stringify({
          refresh_token: tokens.refresh
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Çıkış yapılırken bir hata oluştu');
      }

      // Context'ten çıkış yap
      logout();
      navigate('/login');
      toast.success('Başarıyla çıkış yapıldı');
    } catch (error) {
      console.error('Logout error:', error);
      // API hatası olsa bile local state'i temizle
      logout();
      navigate('/login');
      toast.error(error.message);
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-gray-900/95 backdrop-blur-sm border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Sol Kısım: Logo ve Ana Menü */}
          <div className="flex items-center">
            {/* Logo */}
            <Link to="/" className="flex items-center">
              <span className="text-xl font-bold text-white">VoyageView</span>
            </Link>

            {/* Ana Menü */}
            <div className="hidden md:flex items-center ml-8 space-x-4">
              <Link
                to="/popular"
                className="flex items-center px-4 py-2 text-sm font-medium text-gray-300 
                         hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
              >
                <FireIcon className="h-5 w-5 mr-2" />
                Popüler
              </Link>

              {isAuthenticated && (
                <Link
                  to="/feed"
                  className="flex items-center px-4 py-2 text-sm font-medium text-gray-300 
                           hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <RssIcon className="h-5 w-5 mr-2" />
                  Explore
                </Link>
              )}
            </div>
          </div>

          {/* Sağ Menü */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                {/* Yeni Post Butonu */}
                <Link
                  to="/create-post"
                  className="flex items-center px-4 py-2 text-sm font-medium text-white 
                           bg-purple-600 rounded-lg hover:bg-purple-700 transition-colors"
                >
                  <PencilSquareIcon className="h-5 w-5 mr-2" />
                  Yeni Post
                </Link>

                {/* Profil Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className="flex items-center space-x-3 p-2 hover:bg-gray-800 rounded-lg transition-colors"
                  >
                    <img
                      src={user?.profile_picture || '/default-avatar.png'}
                      alt={user?.username}
                      className="h-8 w-8 rounded-full object-cover"
                    />
                  </button>

                  {isDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-gray-800 rounded-xl shadow-lg py-1 
                                  ring-1 ring-black ring-opacity-5 focus:outline-none">
                      <Link
                        to={`/profile/${user?.username}`}
                        className="flex items-center px-4 py-2 text-sm text-gray-300 
                                 hover:bg-gray-700/50 transition-colors"
                      >
                        <UserCircleIcon className="h-5 w-5 mr-3" />
                        Profilim
                      </Link>
                      <Link
                        to="/profile/settings"
                        className="flex items-center px-4 py-2 text-sm text-gray-300 
                                 hover:bg-gray-700/50 transition-colors"
                      >
                        <Cog6ToothIcon className="h-5 w-5 mr-3" />
                        Ayarlar
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-2 text-sm text-red-400 
                                 hover:bg-gray-700/50 transition-colors"
                      >
                        <ArrowRightOnRectangleIcon className="h-5 w-5 mr-3" />
                        Çıkış Yap
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-300 hover:text-white px-3 py-2 text-sm font-medium"
                >
                  Giriş Yap
                </Link>
                <Link
                  to="/register"
                  className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium 
                           hover:bg-purple-700 transition-colors"
                >
                  Kayıt Ol
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar; 