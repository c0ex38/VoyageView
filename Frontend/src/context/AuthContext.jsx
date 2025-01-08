import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [tokens, setTokens] = useState(() => {
    const savedTokens = localStorage.getItem('tokens');
    return savedTokens ? JSON.parse(savedTokens) : null;
  });

  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Kullanıcı bilgilerini getir
  useEffect(() => {
    const fetchUserData = async () => {
      if (!tokens?.access) {
        setLoading(false);
        setIsAuthenticated(false);
        setUser(null);
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:8000/users/profile/', {
          headers: {
            'Authorization': `Bearer ${tokens.access}`
          }
        });

        if (!response.ok) {
          throw new Error('Kullanıcı bilgileri alınamadı');
        }

        const data = await response.json();
        setUser(data.profile);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Profile fetch error:', error);
        // Token geçersiz veya hata durumunda
        setTokens(null);
        setUser(null);
        setIsAuthenticated(false);
        localStorage.removeItem('tokens');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [tokens]);

  // Token'ları localStorage'a kaydet
  useEffect(() => {
    if (tokens) {
      localStorage.setItem('tokens', JSON.stringify(tokens));
    }
  }, [tokens]);

  const login = async (accessToken, refreshToken) => {
    try {
      const newTokens = {
        access: accessToken,
        refresh: refreshToken
      };
      setTokens(newTokens);
      
      // Login sonrası hemen kullanıcı bilgilerini getir
      const response = await fetch('http://127.0.0.1:8000/users/profile/', {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      if (!response.ok) {
        throw new Error('Kullanıcı bilgileri alınamadı');
      }

      const data = await response.json();
      setUser(data.profile);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Login error:', error);
      logout();
      throw error; // Hata yönetimi için dışarı at
    }
  };

  const logout = () => {
    setTokens(null);
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('tokens');
  };

  const value = {
    tokens,
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    setUser // Profil güncellemesi için gerekebilir
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 