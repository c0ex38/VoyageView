import { Link } from 'react-router-dom';
import { ArrowRightIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../context/AuthContext';
import { useState, useEffect } from 'react';

function Home() {
  const { isAuthenticated } = useAuth();
  const [popularPosts, setPopularPosts] = useState([]);

  useEffect(() => {
    const fetchPopularPosts = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/blog/posts/popular/');
        const data = await response.json();
        setPopularPosts(data);
      } catch (error) {
        console.error('Popular posts fetch error:', error);
      }
    };

    fetchPopularPosts();
  }, []);
  
  return (
    <div className="flex flex-col bg-gray-900 text-white" data-scroll-section>
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center" data-scroll>
        {/* Animasyonlu Gradient Arka Plan */}
        <div className="absolute inset-0 bg-gradient-to-r from-purple-800 via-violet-900 to-purple-800 opacity-50 animate-gradient"></div>
        
        {/* Dekoratif Elementler */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-600/30 rounded-full mix-blend-multiply filter blur-xl animate-blob"></div>
          <div className="absolute top-1/3 right-1/4 w-64 h-64 bg-pink-600/30 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000"></div>
          <div className="absolute bottom-1/4 left-1/3 w-64 h-64 bg-blue-600/30 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000"></div>
        </div>

        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-5xl mx-auto text-center">
            <div className="mb-8 inline-block">
              <span className="bg-purple-500/10 text-purple-300 px-4 py-2 rounded-full 
                             text-sm font-medium border border-purple-500/20 hover:border-purple-500/40 
                             transition-all duration-300 cursor-default">
                🚀 Yapay Zeka Destekli Blog Platformu
              </span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
                Deneyiminizi Yapay Zeka ile
              </span>
              <br />
              <span className="text-white">
                3 Basit Adımda Anlatın
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
              Görselinizi yükleyin, AI önerilerini alın ve benzersiz blog içeriğinizi oluşturun. 
              <span className="text-purple-400">30 saniyede</span> ücretsiz hesap açarak başlayın.
            </p>

            <div className="flex flex-col md:flex-row gap-6 justify-center items-center mb-16">
              {isAuthenticated ? (
                <Link
                  to="/feed"
                  className="group relative px-8 py-4 w-64 rounded-full bg-gradient-to-r 
                           from-purple-600 to-pink-600 text-white font-semibold text-lg
                           hover:shadow-lg hover:shadow-purple-500/25 transition-all duration-300
                           transform hover:scale-105 active:scale-95"
                >
                  <span className="relative z-10">Keşfet</span>
                  <div className="absolute inset-0 rounded-full bg-gradient-to-r from-pink-600 to-purple-600 
                              opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </Link>
              ) : (
                <Link
                  to="/register"
                  className="group relative px-8 py-4 w-64 rounded-full bg-gradient-to-r 
                           from-purple-600 to-pink-600 text-white font-semibold text-lg
                           hover:shadow-lg hover:shadow-purple-500/25 transition-all duration-300
                           transform hover:scale-105 active:scale-95"
                >
                  <span className="relative z-10">Hemen Başla</span>
                  <div className="absolute inset-0 rounded-full bg-gradient-to-r from-pink-600 to-purple-600 
                              opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </Link>
              )}

              <a href="#nasil-calisir" className="group flex items-center space-x-2 text-gray-300 
                                                hover:text-white transition-colors duration-300">
                <span>Nasıl Çalışır?</span>
                <svg className="w-5 h-5 transform group-hover:translate-x-1 transition-transform duration-300" 
                     fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>

            {/* Öne Çıkan Özellikler */}
            <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
              {quickFeatures.map((feature, index) => (
                <div key={index} className="flex items-center space-x-3 bg-gray-800/50 
                                          backdrop-blur-sm rounded-xl p-4 border border-gray-700/50
                                          hover:border-purple-500/50 transition-all duration-300
                                          transform hover:-translate-y-1">
                  <span className="text-2xl">{feature.icon}</span>
                  <span className="text-sm text-gray-300">{feature.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <svg className="w-6 h-6 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>

        {/* Gradient Overlay */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-gray-900 to-transparent"></div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-900" data-scroll>
        <div className="container mx-auto px-4" data-scroll data-scroll-speed="1">
          <h2 className="text-4xl font-bold text-center mb-16 bg-clip-text text-transparent 
                       bg-gradient-to-r from-purple-400 to-pink-600">
            Platform Özellikleri
          </h2>
          <div className="grid md:grid-cols-3 gap-12">
            {features.map((feature, index) => (
              <div key={index} 
                   className="bg-gray-800 p-8 rounded-2xl transform hover:-translate-y-2 
                            transition duration-300 border border-gray-700"
                   data-scroll
                   data-scroll-speed={0.1 * (index + 1)}>
                <div className="text-5xl mb-6">{feature.icon}</div>
                <h3 className="text-2xl font-semibold mb-4 text-purple-400">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Posts Section */}
      <section className="py-20 bg-gray-800 relative overflow-hidden" data-scroll>
        {/* Dekoratif Arka Plan */}
        <div className="absolute inset-0">
          <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full mix-blend-multiply filter blur-3xl"></div>
          <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-pink-600/10 rounded-full mix-blend-multiply filter blur-3xl"></div>
        </div>

        <div className="container mx-auto px-4 relative z-10" data-scroll data-scroll-speed="1">
          <div className="text-center mb-16">
            <Link 
              to="/popular"
              className="group inline-block"
            >
              <h2 className="text-4xl font-bold mb-4 bg-clip-text text-transparent 
                           bg-gradient-to-r from-purple-400 to-pink-600
                           group-hover:from-pink-600 group-hover:to-purple-400 transition-all">
                Popüler Gönderiler
              </h2>
            </Link>
            <p className="text-gray-400 max-w-2xl mx-auto">
              En çok okunan ve beğenilen konum tabanlı blog yazılarını keşfedin.
              Farklı yerlerden ilham verici deneyimler ve hikayeler.
            </p>
          </div>

          {/* Popular Posts Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {popularPosts.slice(0, 3).map((post) => (
              <Link
                key={post.id}
                to={`/post/${post.id}`}
                className="group bg-gray-800/50 backdrop-blur-sm rounded-xl overflow-hidden 
                         hover:bg-gray-800/70 transition-all duration-300 
                         transform hover:-translate-y-1"
              >
                <div className="aspect-w-16 aspect-h-9 bg-gray-900">
                  <img
                    src={post.cover_image || ``}
                    alt={post.title}
                    className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <div className="p-6">
                  <div className="flex items-center space-x-2 mb-3">
                    <img
                      src={post.author.profile_picture || "/default-avatar.png"}
                      alt={post.author.full_name}
                      className="h-6 w-6 rounded-full"
                    />
                    <span className="text-sm text-gray-400">{post.author.full_name}</span>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">
                    {post.title}
                  </h3>
                  <p className="text-gray-400 text-sm line-clamp-2 mb-4">
                    {post.summary}
                  </p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{post.location}</span>
                    <span>{new Date(post.created_at).toLocaleDateString('tr-TR')}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* "Tümünü Gör" Butonu */}
          <div className="text-center">
            <Link
              to="/popular"
              className="inline-flex items-center px-6 py-3 bg-purple-600/10 text-purple-400 
                       rounded-lg hover:bg-purple-600/20 transition-colors group"
            >
              <span>Tüm Popüler Gönderileri Gör</span>
              <ArrowRightIcon className="w-5 h-5 ml-2 transform group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section id="nasil-calisir" className="py-20 bg-gray-900" data-scroll>
        <div className="container mx-auto px-4" data-scroll data-scroll-speed="1">
          <h2 className="text-4xl font-bold text-center mb-16 bg-clip-text text-transparent 
                       bg-gradient-to-r from-purple-400 to-pink-600">
            Nasıl Çalışır?
          </h2>
          <div className="max-w-5xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              {steps.map((step, index) => (
                <div key={index} className="relative" data-scroll data-scroll-speed={0.2 * (index + 1)}>
                  <div className="bg-gray-800 p-8 rounded-2xl h-full border border-gray-700">
                    <div className="absolute -top-4 left-4 w-8 h-8 bg-purple-600 rounded-full 
                                  flex items-center justify-center text-lg font-bold">
                      {index + 1}
                    </div>
                    <h3 className="text-xl font-semibold mb-4 text-purple-400 mt-4">{step.title}</h3>
                    <p className="text-gray-400">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

// Sabit veriler
const quickFeatures = [
  {
    icon: "⚡️",
    text: "30 Saniyede Hesap Oluştur"
  },
  {
    icon: "🤖",
    text: "AI Destekli İçerik Önerileri"
  },
  {
    icon: "🎯",
    text: "Konum Tabanlı İlham"
  }
];

const features = [
  {
    icon: "🚀",
    title: "Hızlı Başlangıç",
    description: "Saniyeler içinde hesabınızı oluşturun ve içerik üretmeye başlayın."
  },
  {
    icon: "🤖",
    title: "AI Asistan",
    description: "Yapay zeka modellerimiz konumunuza özel içerik önerileri sunar."
  },
  {
    icon: "📍",
    title: "Konum Tabanlı",
    description: "Bulunduğunuz yerin özelliklerini ve hikayelerini keşfedin."
  }
];

const steps = [
  {
    title: "Konumu Seç",
    description: "Bulunduğunuz yerin görselini yükleyin."
  },
  {
    title: "AI Önerileri Al",
    description: "Yapay zeka sizin için gerekli her şeyi yapsın"
  },
  {
    title: "İçerik Oluştur",
    description: "Benzersiz blog yazılarınızı oluşturun ve paylaşın."
  }
];

export default Home;