import { Link, useLocation, useParams } from 'react-router-dom';
import { 
  UserIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../../context/AuthContext';

function Sidebar() {
  const location = useLocation();
  const { username } = useParams();
  const { user } = useAuth();
  
  const currentUsername = username || user?.username;

  const menuItems = [
    { 
      name: 'Profil', 
      icon: UserIcon, 
      path: `/profile/${currentUsername}` 
    },
    { 
      name: 'Yazılarım',
      icon: DocumentTextIcon, 
      path: `/profile/${currentUsername}/posts` 
    },
    { 
      name: 'Profil Düzenle', 
      icon: Cog6ToothIcon, 
      path: '/profile/settings' 
    }
  ];

  return (
    <div className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-gray-900 border-r border-gray-800">
      <div className="p-4">
        {/* Profil Özeti */}
        <div className="mb-8 p-4 bg-gray-800/50 rounded-xl">
          <div className="flex items-center space-x-3">
            <img
              src={user?.profile_picture || '/default-avatar.png'}
              alt={user?.username}
              className="h-12 w-12 rounded-full object-cover"
            />
            <div>
              <p className="text-sm text-gray-400">@{user?.username}</p>
            </div>
          </div>
        </div>

        {/* Navigasyon */}
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.name}
                to={item.path}
                className={`
                  flex items-center px-4 py-3 text-sm font-medium rounded-lg
                  ${isActive 
                    ? 'bg-purple-600 text-white' 
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'}
                `}
              >
                <Icon className="h-5 w-5 mr-3" />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}

export default Sidebar; 