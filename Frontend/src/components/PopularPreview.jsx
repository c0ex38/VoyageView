import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';

function PopularPreview() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await fetch('http://localhost:8000/blog/posts/popular/?page=1&page_size=3');
        if (!response.ok) throw new Error('Postlar yüklenemedi');
        const data = await response.json();
        setPosts(data);
      } catch (error) {
        console.error('Posts fetch error:', error);
        toast.error('Postlar yüklenirken bir hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  if (loading) {
    return <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
      {[1, 2, 3].map((_, index) => (
        <div key={index} className="animate-pulse bg-gray-800/50 rounded-xl overflow-hidden">
          <div className="aspect-w-16 aspect-h-9 bg-gray-700"></div>
          <div className="p-6 space-y-4">
            <div className="h-4 bg-gray-700 rounded w-3/4"></div>
            <div className="h-4 bg-gray-700 rounded"></div>
            <div className="h-4 bg-gray-700 rounded w-1/2"></div>
          </div>
        </div>
      ))}
    </div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
      {posts.map((post) => (
        <Link
          key={post.id}
          to={`/post/${post.id}`}
          className="group bg-gray-800/50 backdrop-blur-sm rounded-xl overflow-hidden 
                   hover:bg-gray-800/70 transition-all duration-300 
                   transform hover:-translate-y-1"
        >
          {/* ... kart içeriği ... */}
        </Link>
      ))}
    </div>
  );
}

export default PopularPreview; 