import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import MainLayout from '../components/layout/MainLayout';
import { HeartIcon, ChatBubbleLeftIcon } from '@heroicons/react/24/outline';

function Popular() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const observer = useRef();
  const PAGE_SIZE = 10;

  // Sonsuz kaydırma için son elementi gözlemle
  const lastPostElementRef = useCallback(node => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prevPage => prevPage + 1);
      }
    });

    if (node) observer.current.observe(node);
  }, [loading, hasMore]);

  const fetchPosts = async (pageNumber) => {
    if (loading) return;

    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/blog/posts/popular/?page=${pageNumber}&page_size=${PAGE_SIZE}`
      );

      if (!response.ok) throw new Error('Postlar yüklenemedi');

      const data = await response.json();
      
      if (data && Array.isArray(data)) {
        if (pageNumber === 1) {
          setPosts(data);
        } else {
          const existingIds = new Set(posts.map(post => post.id));
          const newPosts = data.filter(post => !existingIds.has(post.id));
          setPosts(prev => [...prev, ...newPosts]);
        }
        setHasMore(data.length === PAGE_SIZE);
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Posts fetch error:', error);
      toast.error('Postlar yüklenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  // Sayfa yüklendiğinde ilk postları getir
  useEffect(() => {
    setPosts([]);
    setPage(1);
    fetchPosts(1);
  }, []);

  // Sayfa değiştiğinde yeni postları getir
  useEffect(() => {
    if (page > 1) {
      fetchPosts(page);
    }
  }, [page]);

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-white mb-8">Popüler Gönderiler</h1>

        {posts.length > 0 ? (
          <div className="space-y-6">
            {posts.map((post, index) => (
              <Link
                ref={posts.length === index + 1 ? lastPostElementRef : null}
                to={`/post/${post.id}`}
                key={post.id}
                className="block bg-gray-800/50 backdrop-blur-sm rounded-xl overflow-hidden hover:bg-gray-800/70 transition-colors"
              >
                <div className="flex">
                  {post.cover_image && (
                    <div className="w-48 h-48">
                      <img
                        src={post.cover_image}
                        alt={post.title}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}
                  <div className="flex-1 p-6">
                    <div className="flex items-center space-x-2 mb-3">
                      <img
                        src={post.author.profile_picture || '/default-avatar.png'}
                        alt={post.author.username}
                        className="h-6 w-6 rounded-full"
                      />
                      <span className="text-sm text-gray-400">
                        {post.author.username}
                      </span>
                      <span className="text-gray-500">•</span>
                      <span className="text-sm text-gray-500">
                        {new Date(post.created_at).toLocaleDateString('tr-TR')}
                      </span>
                    </div>

                    <h2 className="text-xl font-semibold text-white mb-2">
                      {post.title}
                    </h2>
                    <p className="text-gray-400 line-clamp-2 mb-4">
                      {post.summary}
                    </p>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-sm text-gray-400">
                        <span className="flex items-center space-x-1">
                          <HeartIcon className={`h-5 w-5 ${post.like_status ? 'text-red-500 fill-red-500' : ''}`} />
                          <span>{post.like_count}</span>
                        </span>
                        <span className="flex items-center space-x-1">
                          <ChatBubbleLeftIcon className="h-5 w-5" />
                          <span>{post.comment_count}</span>
                        </span>
                      </div>
                      {post.location && (
                        <span className="text-sm text-gray-500">
                          {post.location}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : loading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
          </div>
        ) : (
          <div className="text-center text-gray-400">
            Henüz hiç post paylaşılmamış.
          </div>
        )}

        {loading && posts.length > 0 && (
          <div className="flex justify-center mt-8">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-500"></div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}

export default Popular; 