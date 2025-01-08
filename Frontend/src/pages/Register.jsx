import { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast, Toaster } from 'react-hot-toast';

function Register() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirm_password: '',
    full_name: '',
    date_of_birth: '',
    location: '',
    latitude: '',
    longitude: ''
  });
  const [profilePicture, setProfilePicture] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);

  // Profil fotoğrafı seçimi
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
        toast.error('Lütfen jpg, jpeg veya png formatında dosya seçin');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Dosya boyutu 5MB\'dan küçük olmalıdır');
        return;
      }
      setProfilePicture(file);
      setPreviewImage(URL.createObjectURL(file));
    }
  };

  // Konum alma
  const getLocation = () => {
    if ("geolocation" in navigator) {
      setLoading(true);
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          
          try {
            const response = await fetch(
              `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`
            );
            const data = await response.json();
            
            const city = data.address.city || 
                        data.address.town || 
                        data.address.county || 
                        'Bilinmeyen Şehir';
            
            setFormData(prev => ({
              ...prev,
              location: city,
              latitude: latitude.toString(),
              longitude: longitude.toString()
            }));

            toast.success('Konum başarıyla alındı');
          } catch (error) {
            toast.error('Konum detayları alınamadı');
          }
          setLoading(false);
        },
        (error) => {
          toast.error('Konum alınamadı');
          setLoading(false);
        }
      );
    } else {
      toast.error('Tarayıcınız konum özelliğini desteklemiyor');
    }
  };

  // Form gönderimi
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    // Form verilerini hazırla
    const formDataToSend = new FormData();
    formDataToSend.append('username', formData.username);
    formDataToSend.append('email', formData.email);
    formDataToSend.append('password', formData.password);
    formDataToSend.append('confirm_password', formData.confirm_password);
    formDataToSend.append('full_name', formData.full_name);
    formDataToSend.append('date_of_birth', formData.date_of_birth);
    formDataToSend.append('location', formData.location);
    formDataToSend.append('latitude', formData.latitude);
    formDataToSend.append('longitude', formData.longitude);
    if (profilePicture) {
      formDataToSend.append('profile_picture', profilePicture);
    }

    try {
      const response = await fetch('http://localhost:8000/users/register/', {
        method: 'POST',
        body: formDataToSend,
      });

      const data = await response.json();
      console.log('Register response:', data); // Response'u kontrol edelim

      if (!response.ok) {
        setErrors(data);
        toast.error('Kayıt işlemi başarısız oldu');
        return;
      }

      toast.success('Kayıt başarılı! Email doğrulama kodunuz gönderildi.');
      
      // Kullanıcı ID'sini ve email'i state ile birlikte gönder
      navigate('/verify-email', { 
        state: { 
          email: formData.email,
          userId: data.user_id // Backend'den gelen user_id
        } 
      });

    } catch (error) {
      console.error('Kayıt hatası:', error);
      toast.error('Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full bg-gray-800/50 backdrop-blur-xl p-8 rounded-2xl shadow-xl">
        {/* Form Başlığı */}
        <div className="text-center mb-8">
          <div className="mx-auto h-16 w-16 bg-purple-600/20 backdrop-blur-xl rounded-full flex items-center justify-center">
            <svg className="h-8 w-8 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-white">
            Hesap Oluştur
          </h2>
          <p className="mt-2 text-sm text-gray-400">
            Veya{' '}
            <Link to="/login" className="font-medium text-purple-400 hover:text-purple-300">
              zaten hesabın var mı?
            </Link>
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Sol Kolon */}
            <div className="space-y-4">
              {/* Kullanıcı Adı */}
              <div>
                <label className="block text-sm font-medium text-gray-300">
                  Kullanıcı Adı
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 bg-gray-700/50 border border-gray-600 
                           rounded-lg text-gray-300 placeholder-gray-500
                           focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                  placeholder="username"
                  required
                  minLength={3}
                  maxLength={150}
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-300">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 bg-gray-700/50 border border-gray-600 
                           rounded-lg text-gray-300 placeholder-gray-500
                           focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                  placeholder="ornek@email.com"
                  required
                />
              </div>

              {/* Şifre */}
              <div>
                <label className="block text-sm font-medium text-gray-300">
                  Şifre
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 bg-gray-700/50 border border-gray-600 
                           rounded-lg text-gray-300 placeholder-gray-500
                           focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                  placeholder="En az 8 karakter"
                  required
                  minLength={8}
                />
              </div>

              {/* Şifre Tekrar */}
              <div>
                <label className="block text-sm font-medium text-gray-300">
                  Şifre Tekrar
                </label>
                <input
                  type="password"
                  name="confirm_password"
                  value={formData.confirm_password}
                  onChange={(e) => setFormData({...formData, confirm_password: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 bg-gray-700/50 border border-gray-600 
                           rounded-lg text-gray-300 placeholder-gray-500
                           focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                  placeholder="Şifrenizi tekrar girin"
                  required
                />
              </div>
            </div>

            {/* Sağ Kolon */}
            <div className="space-y-4">
              {/* Ad Soyad */}
              <div>
                <label className="block text-sm font-medium text-gray-300">
                  Ad Soyad
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 bg-gray-700/50 border border-gray-600 
                           rounded-lg text-gray-300 placeholder-gray-500
                           focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                  placeholder="Ad Soyad"
                  required
                />
              </div>

              {/* Doğum Tarihi */}
              <div>
                <label className="block text-sm font-medium text-gray-300">
                  Doğum Tarihi
                </label>
                <input
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
                  className="mt-1 block w-full px-3 py-2 bg-gray-700/50 border border-gray-600 
                           rounded-lg text-gray-300 placeholder-gray-500
                           focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                  required
                />
              </div>

              {/* Konum */}
              <div>
                <label className="block text-sm font-medium text-gray-300">
                  Konum
                </label>
                <div className="mt-1 flex gap-2">
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={(e) => setFormData({...formData, location: e.target.value})}
                    className="block w-full px-3 py-2 bg-gray-700/50 border border-gray-600 
                             rounded-lg text-gray-300 placeholder-gray-500
                             focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                    placeholder="Şehir"
                    required
                  />
                  <button
                    type="button"
                    onClick={getLocation}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700
                             focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2
                             disabled:opacity-50"
                    disabled={loading}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Profil Fotoğrafı */}
              <div>
                <label className="block text-sm font-medium text-gray-300">
                  Profil Fotoğrafı
                </label>
                <div className="mt-1 flex items-center space-x-4">
                  {previewImage ? (
                    <div className="relative">
                      <img
                        src={previewImage}
                        alt="Profil önizleme"
                        className="h-20 w-20 rounded-full object-cover"
                      />
                      <button
                        type="button"
                        onClick={() => {
                          setProfilePicture(null);
                          setPreviewImage(null);
                        }}
                        className="absolute -top-2 -right-2 bg-red-500 rounded-full p-1"
                      >
                        <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="h-20 w-20 rounded-full border-2 border-dashed border-gray-600 
                               flex items-center justify-center hover:border-purple-500"
                    >
                      <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                    </button>
                  )}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/jpg"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </div>
                <p className="mt-2 text-xs text-gray-400">
                  JPG, JPEG veya PNG (max. 5MB)
                </p>
              </div>
            </div>
          </div>

          {/* Hata Mesajları */}
          {Object.keys(errors).length > 0 && (
            <div className="mt-6 bg-red-500/10 border border-red-500/50 rounded-lg p-4">
              <div className="text-sm text-red-400">
                {Object.entries(errors).map(([key, value]) => (
                  <div key={key}>{Array.isArray(value) ? value.join(', ') : value}</div>
                ))}
              </div>
            </div>
          )}

          {/* Kayıt Ol Butonu */}
          <div className="mt-8">
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg
                       text-sm font-medium text-white bg-purple-600 hover:bg-purple-700
                       focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transition-all duration-200"
            >
              {loading ? 'Kaydediliyor...' : 'Kayıt Ol'}
            </button>
          </div>
        </form>
      </div>
      <Toaster position="top-center" />
    </div>
  );
}

export default Register;
