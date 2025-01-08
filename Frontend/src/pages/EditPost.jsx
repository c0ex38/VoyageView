import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';
import { MapPinIcon, PhotoIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import MainLayout from '../components/layout/MainLayout';
import axios from 'axios';

function EditPost() {
  const navigate = useNavigate();
  const { postId } = useParams();
  const { tokens } = useAuth();
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  const [coverImage, setCoverImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState(null);
  
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    summary: '',
    category_id: '',
    tags: [],
    location: '',
    latitude: '',
    longitude: '',
    location_details: {
      country: '',
      city: ''
    }
  });

  // Post verilerini yükle
  useEffect(() => {
    const fetchPost = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/blog/posts/${postId}/`, {
          headers: {
            'Authorization': `Bearer ${tokens.access}`
          }
        });

        if (!response.ok) throw new Error('Post yüklenemedi');
        
        const post = await response.json();
        
        setFormData({
          title: post.title,
          content: post.content,
          summary: post.summary,
          category_id: post.category.id,
          tags: post.tags_list,
          location: post.location || '',
          latitude: post.latitude || '',
          longitude: post.longitude || '',
          location_details: post.location_details || {
            country: '',
            city: ''
          }
        });

        if (post.cover_image) {
          setImagePreview(post.cover_image);
        }

      } catch (error) {
        toast.error('Post yüklenirken bir hata oluştu');
        console.error('Post fetch error:', error);
        navigate('/profile/posts');
      }
    };

    const fetchCategories = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/blog/categories/', {
          headers: {
            'Authorization': `Bearer ${tokens.access}`
          }
        });

        if (!response.ok) throw new Error('Kategoriler yüklenemedi');
        const data = await response.json();
        setCategories(data);
      } catch (error) {
        toast.error('Kategoriler yüklenirken bir hata oluştu');
        console.error('Category fetch error:', error);
      }
    };

    Promise.all([fetchPost(), fetchCategories()])
      .finally(() => setInitialLoading(false));
  }, [postId, tokens.access, navigate]);

  const getCurrentLocation = () => {
    setIsGettingLocation(true);
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            const response = await fetch(
              `https://nominatim.openstreetmap.org/reverse?lat=${position.coords.latitude}&lon=${position.coords.longitude}&format=json`
            );
            
            const data = await response.json();
            
            setFormData(prev => ({
              ...prev,
              latitude: position.coords.latitude.toString(),
              longitude: position.coords.longitude.toString(),
              location: data.display_name || `${position.coords.latitude}, ${position.coords.longitude}`,
              location_details: {
                country: data.address?.country || '',
                city: data.address?.city || data.address?.town || data.address?.state || ''
              }
            }));
            
            toast.success('Konum başarıyla alındı');
          } catch (error) {
            console.error('Geocoding error:', error);
            toast.warning('Konum alındı fakat detaylar getirilemedi');
          }
          setIsGettingLocation(false);
        },
        (error) => {
          console.error('Geolocation error:', error);
          toast.error('Konum alınamadı');
          setIsGettingLocation(false);
        }
      );
    } else {
      toast.error('Tarayıcınız konum özelliğini desteklemiyor');
      setIsGettingLocation(false);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setCoverImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const postFormData = new FormData();
    
    // Form verilerini ekle
    Object.keys(formData).forEach(key => {
      if (key === 'tags') {
        postFormData.append('tags', formData.tags.join(','));
      } else if (key === 'location_details') {
        postFormData.append('location_details', JSON.stringify(formData.location_details));
      } else {
        postFormData.append(key, formData[key]);
      }
    });
    
    // Post durumunu güncelle: yayınlanmış ama onay bekliyor
    postFormData.append('is_published', true);
    postFormData.append('is_approved', false); // İnceleme için false yapıldı
    
    // Yeni görsel yüklendiyse ekle
    if (coverImage) {
      postFormData.append('cover_image', coverImage);
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/blog/posts/${postId}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${tokens.access}`
        },
        body: postFormData
      });

      if (!response.ok) throw new Error('Post güncellenemedi');

      const data = await response.json();
      toast.success('Post güncellendi ve incelemeye alındı');
      navigate(`/post/${data.id}`);
    } catch (error) {
      toast.error('Post güncellenirken bir hata oluştu');
      console.error('Post update error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  // AI Analiz fonksiyonu
  const analyzeImage = async () => {
    if (!coverImage && !imagePreview) {
      toast.error('Görsel bulunamadı');
      return;
    }

    setAnalyzing(true);
    const formData = new FormData();

    try {
      let response;
      
      if (coverImage) {
        // Yeni yüklenen görsel varsa onu kullan
        formData.append('image', coverImage);
        response = await axios.post(
          'http://localhost:8000/blog/analyze-image/',
          formData,
          {
            headers: {
              'Authorization': `Bearer ${tokens.access}`,
              'Content-Type': 'multipart/form-data',
            }
          }
        );
      } else {
        // Mevcut görselin URL'sini kullan
        response = await axios.post(
          'http://localhost:8000/blog/analyze-image/',
          { image_url: imagePreview },
          {
            headers: {
              'Authorization': `Bearer ${tokens.access}`,
              'Content-Type': 'application/json',
            }
          }
        );
      }

      if (response.data.status === 'success') {
        const suggestions = response.data.data;
        setAiSuggestions(suggestions);
        toast.success('Görsel analizi başarılı');
      } else {
        throw new Error(response.data.message || 'Görsel analizi başarısız oldu');
      }
    } catch (error) {
      console.error('Görsel analizi hatası:', error);
      toast.error(error.response?.data?.message || 'Görsel analizi başarısız oldu');
    } finally {
      setAnalyzing(false);
    }
  };

  // AI önerilerini uygula
  const applyAiSuggestions = () => {
    if (aiSuggestions) {
      setFormData(prev => ({
        ...prev,
        title: aiSuggestions.title || prev.title,
        content: aiSuggestions.content || prev.content,
        summary: aiSuggestions.summary || prev.summary,
        category_id: categories.find(c => c.name === aiSuggestions.category)?.id || prev.category_id,
        tags: Array.isArray(aiSuggestions.keywords) ? aiSuggestions.keywords : prev.tags
      }));
      toast.success('AI önerileri uygulandı');
    }
  };

  if (initialLoading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Üst Başlık */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <ArrowLeftIcon className="h-6 w-6 text-gray-400" />
            </button>
            <h1 className="text-2xl font-bold text-white">Post Düzenle</h1>
          </div>
        </div>

        {/* Form */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl shadow-xl">
          {/* Görsel Yükleme ve AI Analizi */}
          <div className="mb-8 p-6 bg-gray-800/50 rounded-xl">
            <div className="space-y-4">
              <h2 className="text-lg font-medium text-white">1. Görsel Yükle ve Analiz Et</h2>
              
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Kapak Görseli
                  </label>
                  <div className="flex items-center space-x-4">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="hidden"
                      id="cover-image"
                    />
                    <label
                      htmlFor="cover-image"
                      className="flex items-center px-4 py-2 bg-gray-700 rounded-lg cursor-pointer
                               hover:bg-gray-600 transition-colors"
                    >
                      <PhotoIcon className="h-5 w-5 mr-2" />
                      <span>Görsel Değiştir</span>
                    </label>
                    {imagePreview && (
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="h-20 w-20 object-cover rounded-lg"
                      />
                    )}
                  </div>
                </div>
                
                <button
                  type="button"
                  onClick={analyzeImage}
                  disabled={(!coverImage && !imagePreview) || analyzing}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700
                           transition-colors disabled:opacity-50"
                >
                  {analyzing ? 'Analiz Ediliyor...' : 'AI ile Analiz Et'}
                </button>
              </div>
            </div>
          </div>

          {/* AI Analiz Sonuçları */}
          {aiSuggestions && (
            <div className="mb-8 p-6 bg-gray-800/50 rounded-xl">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-medium text-white">AI Analiz Sonuçları</h2>
                  <button
                    type="button"
                    onClick={applyAiSuggestions}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700
                             transition-colors text-sm"
                  >
                    Önerileri Uygula
                  </button>
                </div>

                <div className="grid gap-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-400">Önerilen Başlık</h3>
                    <p className="text-white mt-1">{aiSuggestions.title}</p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-gray-400">Önerilen İçerik</h3>
                    <p className="text-white mt-1 line-clamp-3">{aiSuggestions.content}</p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-gray-400">Önerilen Özet</h3>
                    <p className="text-white mt-1">{aiSuggestions.summary}</p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-gray-400">Önerilen Etiketler</h3>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {aiSuggestions.keywords.map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-gray-700 rounded-lg text-sm text-gray-300"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-gray-400">Önerilen Kategori</h3>
                    <p className="text-white mt-1">{aiSuggestions.category}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Mevcut form içeriği */}
          <form onSubmit={handleSubmit} className="p-6 space-y-8">
            <h2 className="text-lg font-medium text-white">2. Post Detaylarını Düzenle</h2>
            {/* Başlık */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Başlık
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                         text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* İçerik */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                İçerik
              </label>
              <textarea
                name="content"
                value={formData.content}
                onChange={handleChange}
                required
                rows={10}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                         text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Özet */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Özet
              </label>
              <textarea
                name="summary"
                value={formData.summary}
                onChange={handleChange}
                rows={3}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                         text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Kategori */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Kategori
              </label>
              <select
                name="category_id"
                value={formData.category_id}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                         text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">Kategori Seçin</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Etiketler */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Etiketler (virgülle ayırın)
              </label>
              <input
                type="text"
                name="tags"
                value={formData.tags.join(', ')}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  tags: e.target.value.split(',').map(tag => tag.trim()).filter(Boolean)
                }))}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                         text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Konum Bilgileri */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="block text-sm font-medium text-gray-300">
                  Konum Bilgileri
                </label>
                <button
                  type="button"
                  onClick={getCurrentLocation}
                  disabled={isGettingLocation}
                  className="text-sm text-purple-400 hover:text-purple-300 
                           flex items-center space-x-2 disabled:opacity-50"
                >
                  <MapPinIcon className="h-5 w-5" />
                  <span>{isGettingLocation ? 'Konum Alınıyor...' : 'Otomatik Konum Al'}</span>
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Konum Adı
                  </label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                             text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Enlem
                    </label>
                    <input
                      type="text"
                      name="latitude"
                      value={formData.latitude}
                      onChange={handleChange}
                      className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                               text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Boylam
                    </label>
                    <input
                      type="text"
                      name="longitude"
                      value={formData.longitude}
                      onChange={handleChange}
                      className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                               text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Ülke
                  </label>
                  <input
                    type="text"
                    name="location_details.country"
                    value={formData.location_details.country}
                    onChange={handleChange}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                             text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Şehir
                  </label>
                  <input
                    type="text"
                    name="location_details.city"
                    value={formData.location_details.city}
                    onChange={handleChange}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg
                             text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="px-6 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600
                         transition-colors"
              >
                İptal
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700
                         transition-colors disabled:opacity-50"
              >
                {loading ? 'Güncelleniyor...' : 'Güncelle'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}

export default EditPost; 