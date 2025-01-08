import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast, Toaster } from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { ArrowLeftIcon, CameraIcon, MapPinIcon } from '@heroicons/react/24/outline';
import MainLayout from '../components/layout/MainLayout';

function EditProfile() {
  const navigate = useNavigate();
  const { tokens } = useAuth();
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    date_of_birth: '',
    profile_picture: null,
    location: '',
    latitude: '',
    longitude: ''
  });
  const [previewImage, setPreviewImage] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/users/profile/', {
          headers: {
            'Authorization': `Bearer ${tokens.access}`
          }
        });

        if (!response.ok) throw new Error('Profil bilgileri alınamadı');

        const data = await response.json();
        const { profile } = data;
        
        setFormData({
          username: profile.username || '',
          email: profile.email || '',
          full_name: profile.full_name || '',
          date_of_birth: profile.date_of_birth || '',
          location: profile.location || '',
          latitude: profile.latitude || '',
          longitude: profile.longitude || '',
          profile_picture: null
        });
        setPreviewImage(profile.profile_picture);
      } catch (error) {
        toast.error(error.message);
        navigate(-1);
      } finally {
        setInitialLoading(false);
      }
    };

    fetchProfile();
  }, [tokens, navigate]);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        toast.error('Dosya boyutu 5MB\'dan küçük olmalıdır');
        return;
      }
      setFormData(prev => ({ ...prev, profile_picture: file }));
      setPreviewImage(URL.createObjectURL(file));
    }
  };

  const handleLocationSelect = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          }));
          // Reverse geocoding için örnek (Google Maps API veya başka bir servis kullanılabilir)
          fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${position.coords.latitude}&lon=${position.coords.longitude}`)
            .then(res => res.json())
            .then(data => {
              setFormData(prev => ({
                ...prev,
                location: data.display_name.split(',')[0] || ''
              }));
            })
            .catch(() => {
              toast.error('Konum bilgisi alınamadı');
            });
        },
        () => {
          toast.error('Konum izni reddedildi');
        }
      );
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const form = new FormData();
      
      // Sadece değişen alanları gönder
      Object.keys(formData).forEach(key => {
        if (formData[key] !== null && formData[key] !== '') {
          form.append(key, formData[key]);
        }
      });

      const response = await fetch('http://127.0.0.1:8000/users/profile/', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${tokens.access}`
        },
        body: form
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Profil güncellenemedi');
      }

      toast.success('Profil başarıyla güncellendi');
      navigate(`/profile/${formData.username}`);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) {
    return (
      <MainLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="min-h-screen">
        <div className="max-w-4xl mx-auto">
          {/* Üst Başlık */}
          <div className="mb-8 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                <ArrowLeftIcon className="h-6 w-6 text-gray-400" />
              </button>
              <h1 className="text-2xl font-bold text-white">Profili Düzenle</h1>
            </div>
          </div>

          {/* Form */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl shadow-xl">
            <form onSubmit={handleSubmit} className="p-6 space-y-8">
              {/* Profil Fotoğrafı */}
              <div className="flex items-center space-x-6">
                <div className="relative">
                  <img
                    src={previewImage || '/default-avatar.png'}
                    alt="Profile"
                    className="h-24 w-24 rounded-xl object-cover"
                  />
                  <label
                    htmlFor="profile_picture"
                    className="absolute -bottom-2 -right-2 p-2 bg-purple-600 rounded-lg
                             text-white cursor-pointer hover:bg-purple-700 transition-colors"
                  >
                    <CameraIcon className="h-5 w-5" />
                    <input
                      type="file"
                      id="profile_picture"
                      name="profile_picture"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="hidden"
                    />
                  </label>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-white">Profil Fotoğrafı</h3>
                  <p className="text-sm text-gray-400">
                    JPG, GIF veya PNG. Max 5MB.
                  </p>
                </div>
              </div>

              {/* Form Alanları */}
              <div className="grid grid-cols-1 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Kullanıcı Adı
                  </label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                    className="w-full px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg
                             text-white placeholder-gray-400 focus:outline-none focus:ring-2
                             focus:ring-purple-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    E-posta
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                    className="w-full px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg
                             text-white placeholder-gray-400 focus:outline-none focus:ring-2
                             focus:ring-purple-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Ad Soyad
                  </label>
                  <input
                    type="text"
                    value={formData.full_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, full_name: e.target.value }))}
                    className="w-full px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg
                             text-white placeholder-gray-400 focus:outline-none focus:ring-2
                             focus:ring-purple-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Doğum Tarihi
                  </label>
                  <input
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => setFormData(prev => ({ ...prev, date_of_birth: e.target.value }))}
                    className="w-full px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg
                             text-white placeholder-gray-400 focus:outline-none focus:ring-2
                             focus:ring-purple-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Konum
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                      className="flex-1 px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg
                               text-white placeholder-gray-400 focus:outline-none focus:ring-2
                               focus:ring-purple-500 focus:border-transparent"
                      placeholder="Konumunuz"
                    />
                    <button
                      type="button"
                      onClick={handleLocationSelect}
                      className="px-4 py-2 bg-gray-700 rounded-lg text-gray-400 hover:text-white
                               transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <MapPinIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Kaydet Butonu */}
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700
                         transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500
                         focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50
                         disabled:cursor-not-allowed"
                >
                  {loading ? 'Kaydediliyor...' : 'Değişiklikleri Kaydet'}
                </button>
              </div>
            </form>
          </div>
        </div>
        <Toaster position="top-center" />
      </div>
    </MainLayout>
  );
}

export default EditProfile; 