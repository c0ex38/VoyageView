import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';
import { MapPinIcon, PhotoIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import MainLayout from '../components/layout/MainLayout';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function CreatePost() {
  const navigate = useNavigate();
  const { tokens } = useAuth();
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [categories, setCategories] = useState([]);
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  const [coverImage, setCoverImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
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

  // Kategorileri yükle
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/blog/categories/`, {
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

    fetchCategories();
  }, [tokens]);

  // Otomatik konum alma
  const getCurrentLocation = useCallback(() => {
    setIsGettingLocation(true);
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            // Reverse Geocoding ile konum bilgilerini al
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
            setFormData(prev => ({
              ...prev,
              latitude: position.coords.latitude.toString(),
              longitude: position.coords.longitude.toString(),
              location: `${position.coords.latitude}, ${position.coords.longitude}`
            }));
            toast.warning('Konum alındı fakat detaylar getirilemedi');
          }
          setIsGettingLocation(false);
        },
        (error) => {
          console.error('Geolocation error:', error);
          toast.error('Konum alınamadı. Lütfen manuel girin.');
          setIsGettingLocation(false);
        }
      );
    } else {
      toast.error('Tarayıcınız konum özelliğini desteklemiyor');
      setIsGettingLocation(false);
    }
  }, []);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setCoverImage(file);
      setImagePreview(URL.createObjectURL(file));
      // Resim değiştiğinde AI önerilerini sıfırla
      setAiSuggestions(null);
    }
  };

  const analyzeImage = useCallback(async () => {
    if (!coverImage) {
      toast.error('Lütfen önce bir görsel yükleyin');
      return;
    }

    setAnalyzing(true);
    const formData = new FormData();
    formData.append('image', coverImage);

    try {
      const response = await axios.post(
        'http://localhost:8000/blog/analyze-image/',
        formData,
        {
          headers: {
            'Authorization': `Bearer ${tokens.access}`,
            'Content-Type': 'multipart/form-data',
          }
        }
      );

      if (response.data.status === 'success') {
        const suggestions = response.data.data;
        setAiSuggestions(suggestions);
        
        // AI önerilerini form alanlarına yerleştir
        setFormData(prev => ({
          ...prev,
          title: suggestions.title || '',
          content: suggestions.content || '',
          summary: suggestions.summary || '',
          category_id: categories.find(c => c.name === suggestions.suggested_category)?.id || '',
          tags: suggestions.keywords || [],
          location: suggestions.location?.name || '',
          latitude: suggestions.location?.latitude?.toString() || '',
          longitude: suggestions.location?.longitude?.toString() || '',
          location_details: {
            country: suggestions.location?.country || '',
            city: suggestions.location?.city || ''
          }
        }));

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
  }, [coverImage, tokens.access]);

  // AI önerilerini forma uygula
  const applyAiSuggestions = () => {
    if (aiSuggestions) {
      setFormData(prev => ({
        ...prev,
        title: aiSuggestions.title || '',
        content: aiSuggestions.content || '',
        summary: aiSuggestions.summary || '',
        tags: Array.isArray(aiSuggestions.keywords) ? aiSuggestions.keywords : [],
        category_id: categories.find(c => c.name === aiSuggestions.category)?.id || ''
      }));
      toast.success('AI önerileri uygulandı');
    }
  };

  const validateForm = () => {
    if (!formData.title.trim()) {
      toast.error('Başlık zorunludur');
      return false;
    }
    if (!formData.content.trim()) {
      toast.error('İçerik zorunludur');
      return false;
    }
    if (!formData.category_id) {
      toast.error('Kategori seçimi zorunludur');
      return false;
    }
    if (!coverImage) {
      toast.error('Kapak görseli zorunludur');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    setLoading(true);
    const postFormData = new FormData();
    
    // Form verilerini ekle
    Object.keys(formData).forEach(key => {
      if (key === 'tags') {
        postFormData.append('tags', JSON.stringify(formData.tags));
      } else if (key === 'location_details') {
        postFormData.append('location_details', JSON.stringify(formData.location_details));
      } else {
        postFormData.append(key, formData[key]);
      }
    });
    
    // Görseli ekle
    postFormData.append('cover_image', coverImage);

    try {
      const response = await fetch('http://localhost:8000/blog/posts/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access}`
        },
        body: postFormData
      });

      if (!response.ok) throw new Error('Post oluşturulamadı');

      const data = await response.json();
      toast.success('Post başarıyla oluşturuldu');
      navigate(`/post/${data.id}`);
    } catch (error) {
      toast.error(error.message);
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

  const handleTagsChange = (e) => {
    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(Boolean);
    setFormData(prev => ({
      ...prev,
      tags
    }));
  };

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
            <h1 className="text-2xl font-bold text-white">Yeni Post Oluştur</h1>
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
                      <span>Görsel Seç</span>
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
                  disabled={!coverImage || analyzing}
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

          {/* Post Oluşturma Formu */}
          <form onSubmit={handleSubmit} className="p-6 space-y-8">
            <h2 className="text-lg font-medium text-white">2. Post Detaylarını Gir</h2>
            
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

            {/* Özet (Opsiyonel) */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Özet (Boş bırakırsanız AI tarafından oluşturulacak)
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

            {/* Kategori - API'den gelen verilerle */}
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
                value={formData.tags}
                onChange={handleTagsChange}
                placeholder="örn: Seyahat, İstanbul, Tarih"
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
                    placeholder="örn: Sultanahmet Meydanı"
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
                      placeholder="41.0082"
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
                      placeholder="28.9784"
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
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={loading || !coverImage}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700
                         transition-colors disabled:opacity-50"
              >
                {loading ? 'Oluşturuluyor...' : 'Post Oluştur'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}

export default CreatePost;