import { useLocation } from 'react-router-dom';
import Navbar from './MainNavbar';
import Sidebar from './MainSidebar';

function MainLayout({ children }) {
  const location = useLocation();
  
  // Sadece profil ve ayarlar sayfalarında sidebar'ı göster
  const showSidebar = location.pathname.includes('/profile') || 
                     location.pathname.includes('/settings');

  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />
      <div className="pt-16 flex">
        {showSidebar && <Sidebar />}
        <main className={`flex-1 ${showSidebar ? 'ml-64' : ''}`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

export default MainLayout; 