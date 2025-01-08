import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { HeartIcon, ChatBubbleLeftIcon, MapPinIcon } from '@heroicons/react/24/outline';

function UserPostsSection({ username }) {
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    count: 0,
    currentPage: 1,
    totalPages: 1
  });
  const { tokens } = useAuth();

  useEffect(() => {
    const fetchUserPosts = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/blog/posts/?author=${username}`,
          {
            headers: {
              'Authorization': `Bearer ${tokens.access}`
            }
          }
        );

        if (!response.ok) throw new Error('Postlar yüklenemedi');
        
        const data = await response.json();
        setPosts(data.results);
        setPagination({
          count: data.count,
          currentPage: data.current_page,
          totalPages: data.total_pages
        });
      } catch (error) {
        console.error('Post fetch error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserPosts();
  }, [username, tokens]);

  const handlePostClick = async (postId) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/blog/posts/${postId}/`,
        {
          headers: {
            'Authorization': `Bearer ${tokens.access}`
          }
        }
      );

      if (!response.ok) throw new Error('Post detayları yüklenemedi');
      
      const data = await response.json();
      navigate(`/post/${data.id}`);
    } catch (error) {
      console.error('Post detail fetch error:', error);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-full">
      <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-500"></div>
    </div>;
  }

  if (posts.length === 0) {
    return <div className="text-center text-gray-400">
      Henüz hiç gönderi paylaşılmamış.
    </div>;
  }

  return (
    <div className="grid grid-cols-2 gap-4 h-full overflow-y-auto pr-2">
      {posts.map(post => (
        <div 
          key={post.id} 
          onClick={() => handlePostClick(post.id)}
          className="bg-gray-700/50 rounded-lg overflow-hidden hover:bg-gray-700/70 transition-colors cursor-pointer"
        >
          {post.cover_image && (
            <img 
              src={post.cover_image} 
              alt={post.title}
              className="w-full h-32 object-cover"
            />
          )}
          <div className="p-4">
            <h3 className="font-medium text-white mb-2 line-clamp-1">{post.title}</h3>
            <p className="text-sm text-gray-400 mb-3 line-clamp-2">{post.summary}</p>
            
            <div className="flex items-center justify-between text-sm text-gray-400">
              <div className="flex items-center space-x-3">
                <span className="flex items-center">
                  <HeartIcon className={`h-4 w-4 mr-1 ${post.like_status ? 'text-red-500 fill-red-500' : ''}`} />
                  {post.like_count}
                </span>
                <span className="flex items-center">
                  <ChatBubbleLeftIcon className="h-4 w-4 mr-1" />
                  {post.comment_count}
                </span>
              </div>
              {post.location && (
                <span className="flex items-center text-xs">
                  <MapPinIcon className="h-3 w-3 mr-1" />
                  {post.location}
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default UserPostsSection; 