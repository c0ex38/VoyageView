import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import MainLayout from '../components/layout/MainLayout';
import ProfileHeader from '../components/profile/ProfileHeader';
import ProfileStats from '../components/profile/ProfileStats';
import ProfileProgress from '../components/profile/ProfileProgress';
import ProfileTabs from '../components/profile/ProfileTabs';
import AboutSection from '../components/profile/AboutSection';
import UserPostsSection from '../components/profile/UserPostsSection';

function Profile() {
  const { username } = useParams();
  const navigate = useNavigate();
  const { tokens, user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('about');
  const [isFollowing, setIsFollowing] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch(`http://localhost:8000/users/profile/${username}/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            ...(tokens && { 'Authorization': `Bearer ${tokens.access}` })
          }
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Profil yüklenemedi');
        }

        setProfile(data.profile);
        setMeta(data.meta);
      } catch (err) {
        setError(err.message);
        toast.error(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchProfile();
    }
  }, [username, tokens]);
    
  useEffect(() => {
    if (profile) {
      setIsFollowing(profile.is_following);
    }
  }, [profile]);

  const handleLike = async (postId) => {
    if (!tokens) {
      toast.error('Beğenmek için giriş yapmalısınız');
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/blog/posts/${postId}/like/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Beğeni işlemi başarısız');
      }
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleFollowToggle = async () => {
    if (!tokens) {
      toast.error('Takip etmek için giriş yapmalısınız');
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/users/${profile.id}/follow/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('İşlem başarısız');
      }

      // Toggle following state
      setIsFollowing(prev => !prev);
      
      // Update follower count in meta
      setMeta(prev => ({
        ...prev,
        follower_count: isFollowing ? prev.follower_count - 1 : prev.follower_count + 1
      }));

      toast.success(isFollowing ? 'Takipten çıkıldı' : 'Takip edildi');
    } catch (error) {
      toast.error(error.message);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-red-500">{error}</div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="h-[calc(100vh-64px)]">
        <div className="max-w-6xl mx-auto h-full px-4 sm:px-6 lg:px-8 py-4">
          <div className="grid grid-cols-3 gap-6 h-[600px]">
            <div className="col-span-1 bg-gray-800 rounded-xl shadow-lg h-full">
              <div className="p-4">
                <ProfileHeader 
                  profile={profile} 
                  meta={meta} 
                  onEditClick={() => navigate('/settings/profile')}
                  showFollowButton={user?.id !== profile?.id}
                  isFollowing={isFollowing}
                  onFollowToggle={handleFollowToggle}
                />
              </div>

              <div className="border-t border-gray-700 mt-2">
                <div className="p-4">
                  <ProfileStats profile={profile} />
                </div>
              </div>

              <div className="px-4 pb-4">
                <ProfileProgress profile={profile} meta={meta} />
              </div>
            </div>

            <div className="col-span-2 bg-gray-800 rounded-xl shadow-lg flex flex-col h-full">
              <div>
                <ProfileTabs 
                  activeTab={activeTab} 
                  onTabChange={setActiveTab} 
                />
              </div>
              
              <div className="p-4 flex-1">
                {activeTab === 'about' ? (
                  <AboutSection profile={profile} meta={meta} />
                ) : (
                  <UserPostsSection username={username} />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}

export default Profile; 