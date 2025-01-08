import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { toast } from 'react-hot-toast';
import { 
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  Cog6ToothIcon,
  PencilSquareIcon,
  RssIcon,
  FireIcon,
  HomeIcon,
  BookOpenIcon,
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';

function Navbar() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, tokens } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [categories, setCategories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    category: '',
    latitude: '',
    longitude: '',
    distance: '',
    ordering: '-created_at'
  });
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const searchTimeout = useRef(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/blog/categories/');
        if (!response.ok) throw new Error('Kategoriler yüklenemedi');
        
        const data = await response.json();
        setCategories(data);
      } catch (error) {
        console.error('Categories fetch error:', error);
        toast.error('Kategoriler yüklenirken bir hata oluştu');
      }
    };

    fetchCategories();
  }, []);

  const handleLogout = async () => {
    if (!tokens?.access || !tokens?.refresh) {
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

      logout();
      navigate('/');
      toast.success('Başarıyla çıkış yapıldı');
    } catch (error) {
      console.error('Logout error:', error);
      logout();
      navigate('/');
      toast.error(error.message);
    }
  };

  const handleCreatePost = () => {
    navigate('/create-post');
  };

  const handleSearch = async (e) => {
    e?.preventDefault();
    
    setIsSearching(true);
    try {
      const params = new URLSearchParams({
        q: searchQuery
      });

      const response = await fetch(`http://localhost:8000/blog/search/?${params}`, {
        headers: {
          'Authorization': `Bearer ${tokens?.access}`
        }
      });

      if (!response.ok) throw new Error('Arama yapılırken bir hata oluştu');

      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      toast.error(error.message);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    
    if (searchTimeout.current) {
      clearTimeout(searchTimeout.current);
    }

    searchTimeout.current = setTimeout(() => {
      handleSearch();
    }, 1000);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.search-container')) {
        setSearchResults([]);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-gray-900/95 backdrop-blur-sm border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
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
                  Bana Özel
                </Link>
              )}
            </div>
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-xl mx-8 search-container relative">
            <form onSubmit={handleSearch} className="relative">
              <div className="flex items-center">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={handleInputChange}
                    placeholder="Seyahat deneyimlerini ara..."
                    className="w-full bg-gray-800 text-white rounded-l-lg pl-4 pr-10 py-2 
                             focus:outline-none focus:ring-2 focus:ring-purple-600"
                  />
                  <button
                    type="button"
                    onClick={() => setShowFilters(!showFilters)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 
                             hover:text-white transition-colors"
                  >
                    <AdjustmentsHorizontalIcon className="h-5 w-5" />
                  </button>
                </div>
                <button
                  type="submit"
                  className="bg-purple-600 text-white px-4 py-2 rounded-r-lg 
                           hover:bg-purple-700 transition-colors"
                >
                  <MagnifyingGlassIcon className="h-5 w-5" />
                </button>
              </div>

              {/* Filtreler Dropdown */}
              {showFilters && (
                <div className="absolute mt-2 w-full bg-gray-800 rounded-lg shadow-lg p-4 space-y-3 z-50">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Kategori</label>
                    <select
                      value={filters.category}
                      onChange={(e) => setFilters({...filters, category: e.target.value})}
                      className="w-full bg-gray-700 text-white rounded px-3 py-2"
                    >
                      <option value="">Tümü</option>
                      {categories.map(category => (
                        <option key={category.id} value={category.slug}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Enlem</label>
                      <input
                        type="text"
                        value={filters.latitude}
                        onChange={(e) => setFilters({...filters, latitude: e.target.value})}
                        placeholder="41.0082"
                        className="w-full bg-gray-700 text-white rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Boylam</label>
                      <input
                        type="text"
                        value={filters.longitude}
                        onChange={(e) => setFilters({...filters, longitude: e.target.value})}
                        placeholder="28.9784"
                        className="w-full bg-gray-700 text-white rounded px-3 py-2"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Mesafe (km)</label>
                    <input
                      type="number"
                      value={filters.distance}
                      onChange={(e) => setFilters({...filters, distance: e.target.value})}
                      placeholder="5"
                      className="w-full bg-gray-700 text-white rounded px-3 py-2"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Sıralama</label>
                    <select
                      value={filters.ordering}
                      onChange={(e) => setFilters({...filters, ordering: e.target.value})}
                      className="w-full bg-gray-700 text-white rounded px-3 py-2"
                    >
                      <option value="-created_at">En Yeni</option>
                      <option value="created_at">En Eski</option>
                      <option value="-like_count">En Çok Beğenilen</option>
                      <option value="-comment_count">En Çok Yorumlanan</option>
                    </select>
                  </div>
                </div>
              )}

              {/* Arama Sonuçları Dropdown */}
              {searchQuery && (searchResults.length > 0 || isSearching) && (
                <div className="absolute mt-2 w-full bg-gray-800 rounded-lg shadow-lg overflow-hidden z-50">
                  {isSearching ? (
                    <div className="p-4 text-center text-gray-400">
                      <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-purple-500 mx-auto"></div>
                    </div>
                  ) : (
                    <div className="max-h-[400px] overflow-y-auto">
                      {searchResults.map(post => (
                        <Link
                          key={post.id}
                          to={`/post/${post.slug}`}
                          className="block p-4 hover:bg-gray-700/50 border-b border-gray-700 last:border-0"
                          onClick={() => {
                            setSearchResults([]);
                            setSearchQuery('');
                          }}
                        >
                          <div className="flex items-start space-x-4">
                            {post.cover_image && (
                              <img
                                src={post.cover_image}
                                alt={post.title}
                                className="w-16 h-16 object-cover rounded"
                              />
                            )}
                            <div className="flex-1 min-w-0">
                              <h3 className="text-white font-medium truncate">{post.title}</h3>
                              <p className="text-sm text-gray-400 line-clamp-2">{post.summary}</p>
                              <div className="flex items-center mt-1 text-xs text-gray-500">
                                <span>{post.author.username}</span>
                                <span className="mx-1">•</span>
                                <span>{new Date(post.created_at).toLocaleDateString('tr-TR')}</span>
                              </div>
                            </div>
                          </div>
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </form>
          </div>

          {/* Sağ Menü */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                {/* Yeni Post Butonu */}
                <button
                  onClick={handleCreatePost}
                  className="flex items-center px-4 py-2 text-sm font-medium text-white 
                           bg-purple-600 rounded-lg hover:bg-purple-700 transition-colors"
                >
                  <PencilSquareIcon className="h-5 w-5 mr-2" />
                  Yeni Post
                </button>

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