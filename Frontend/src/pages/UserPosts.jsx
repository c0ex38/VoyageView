import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import MainLayout from '../components/layout/MainLayout';
import { 
  HeartIcon, 
  ChatBubbleLeftIcon,
  PencilSquareIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import DeleteConfirmationModal from '../components/common/DeleteConfirmationModal';

function UserPosts() {
  const navigate = useNavigate();
  const { username } = useParams();
  const { tokens } = useAuth();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [pagination, setPagination] = useState({
    count: 0,
    currentPage: 1,
    totalPages: 1
  });
  const [deleteModal, setDeleteModal] = useState({
    isOpen: false,
    postId: null
  });

  useEffect(() => {
    const fetchUserPosts = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/blog/posts/', {
          headers: {
            'Authorization': `Bearer ${tokens.access}`
          }
        });

        if (!response.ok) {
          throw new Error('Postlar yüklenemedi');
        }

        const data = await response.json();
        setPosts(data.results);
        setPagination({
          count: data.count,
          currentPage: data.current_page,
          totalPages: data.total_pages
        });
      } catch (error) {
        toast.error('Postlar yüklenirken bir hata oluştu');
        console.error('Post fetch error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserPosts();
  }, [tokens.access]);

  const openDeleteModal = (postId, e) => {
    e.preventDefault();
    e.stopPropagation();
    setDeleteModal({ isOpen: true, postId });
  };

  const closeDeleteModal = () => {
    setDeleteModal({ isOpen: false, postId: null });
  };

  const handleDelete = async () => {
    if (!deleteModal.postId) return;

    setDeleting(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/blog/posts/${deleteModal.postId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${tokens.access}`
        }
      });

      if (!response.ok) {
        throw new Error('Post silinemedi');
      }

      setPosts(posts.filter(post => post.id !== deleteModal.postId));
      setPagination(prev => ({
        ...prev,
        count: prev.count - 1
      }));
      
      toast.success('Post başarıyla silindi');
      closeDeleteModal();
    } catch (error) {
      toast.error('Post silinirken bir hata oluştu');
      console.error('Post delete error:', error);
    } finally {
      setDeleting(false);
    }
  };

  const handleEdit = (postId, e) => {
    e.preventDefault(); // Link tıklamasını engelle
    e.stopPropagation(); // Event bubbling'i engelle
    navigate(`/post/edit/${postId}`);
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-white">Yazılarım</h1>
          <div className="text-sm text-gray-400">
            Toplam: {pagination.count} yazı
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
          </div>
        ) : posts.length > 0 ? (
          <div className="space-y-6">
            {posts.map(post => (
              <Link
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
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-400">
                          {new Date(post.created_at).toLocaleDateString('tr-TR')}
                        </span>
                        <span className="text-gray-500">•</span>
                        <span className="text-sm text-gray-400">
                          {post.read_time} dk okuma
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs px-2 py-1 rounded ${
                          !post.is_published 
                            ? 'bg-gray-500/20 text-gray-300'
                            : !post.is_approved
                            ? 'bg-yellow-500/20 text-yellow-300'
                            : 'bg-green-500/20 text-green-300'
                        }`}>
                          {!post.is_published 
                            ? 'Taslak' 
                            : !post.is_approved 
                            ? 'İncelemede' 
                            : 'Yayında'}
                        </span>
                        
                        {/* İşlem Düğmeleri */}
                        <div className="flex items-center space-x-2" onClick={e => e.stopPropagation()}>
                          <button
                            onClick={(e) => handleEdit(post.id, e)}
                            className="p-1 hover:bg-gray-700 rounded transition-colors"
                            title="Düzenle"
                          >
                            <PencilSquareIcon className="h-5 w-5 text-gray-400 hover:text-white" />
                          </button>
                          <button
                            onClick={(e) => openDeleteModal(post.id, e)}
                            className="p-1 hover:bg-gray-700 rounded transition-colors"
                            title="Sil"
                          >
                            <TrashIcon className="h-5 w-5 text-red-400 hover:text-red-500" />
                          </button>
                        </div>
                      </div>
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
        ) : (
          <div className="text-center text-gray-400">
            Henüz hiç post paylaşmamışsınız.
          </div>
        )}
      </div>
      
      <DeleteConfirmationModal
        isOpen={deleteModal.isOpen}
        onClose={closeDeleteModal}
        onConfirm={handleDelete}
        loading={deleting}
        title="Postu Sil"
      />
    </MainLayout>
  );
}

export default UserPosts; 