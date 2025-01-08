import { useState, useEffect } from 'react';
import { blogService } from '../services/blogService';

function PopularPosts() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPopularPosts = async () => {
      try {
        const data = await blogService.getPopularPosts();
        setPosts(data);
        setLoading(false);
      } catch (err) {
        setError('Popüler gönderiler yüklenirken bir hata oluştu.');
        setLoading(false);
      }
    };

    fetchPopularPosts();
  }, []);

  if (loading) {
    return (
      <div className="grid md:grid-cols-3 gap-8">
        {[1, 2, 3].map((item) => (
          <div key={item} className="bg-gray-800 rounded-xl overflow-hidden shadow-lg animate-pulse">
            <div className="h-48 bg-gray-700"></div>
            <div className="p-6">
              <div className="h-4 bg-gray-700 rounded w-3/4 mb-4"></div>
              <div className="h-4 bg-gray-700 rounded w-1/2"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-400">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-4 bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-full"
        >
          Tekrar Dene
        </button>
      </div>
    );
  }

  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
      {posts.map((post) => (
        <div key={post.id} 
             className="bg-gray-800 rounded-xl overflow-hidden shadow-lg 
                      transform hover:-translate-y-2 transition duration-300 border border-gray-700">
          {post.image && (
            <div className="h-48 overflow-hidden">
              <img 
                src={post.image} 
                alt={post.title}
                className="w-full h-full object-cover hover:scale-110 transition duration-300"
              />
            </div>
          )}
          <div className="p-6">
            <h3 className="text-xl font-semibold mb-3 text-white hover:text-purple-400 
                         transition duration-300">
              {post.title}
            </h3>
            <p className="text-gray-400 mb-4 line-clamp-3">
              {post.content}
            </p>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <span>📍 {post.location || 'Konum belirtilmemiş'}</span>
              </div>
              <div className="flex items-center space-x-4 text-sm text-gray-400">
                <span className="flex items-center space-x-1">
                  <span>👁️</span>
                  <span>{post.views || 0}</span>
                </span>
                <span className="flex items-center space-x-1">
                  <span>❤️</span>
                  <span>{post.likes || 0}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default PopularPosts; 