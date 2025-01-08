import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';
import MainLayout from '../components/layout/MainLayout';
import { 
  HeartIcon, 
  ChatBubbleLeftIcon, 
  MapPinIcon,
  UserCircleIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartIconSolid } from '@heroicons/react/24/solid';

// Yorum Bileşeni
const CommentItem = ({ comment, onReply }) => {
  const { isAuthenticated } = useAuth();
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyContent, setReplyContent] = useState('');

  return (
    <div className="bg-gray-800/50 rounded-lg p-4">
      <div className="flex items-start space-x-4">
        <img
          src={comment.user.profile_picture || '/default-avatar.png'}
          alt={comment.user.full_name}
          className="w-10 h-10 rounded-full"
        />
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <span className="font-medium text-white">{comment.user.full_name}</span>
            <span className="text-sm text-gray-400">
              {new Date(comment.created_at).toLocaleDateString('tr-TR')}
            </span>
          </div>
          <p className="text-gray-300 mt-1">{comment.content}</p>

          {/* Yanıtla Butonu */}
          {isAuthenticated && (
            <button
              onClick={() => setShowReplyForm(!showReplyForm)}
              className="text-sm text-purple-500 mt-2 hover:text-purple-400"
            >
              Yanıtla {comment.reply_count > 0 && `(${comment.reply_count})`}
            </button>
          )}

          {/* Yanıt Formu */}
          {showReplyForm && (
            <div className="mt-4 pl-8 border-l-2 border-gray-700">
              <textarea
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                placeholder={`${comment.user.full_name}'e yanıt yaz...`}
                className="w-full bg-gray-700 text-white rounded-lg p-3 min-h-[80px]
                         focus:outline-none focus:ring-2 focus:ring-purple-600"
              />
              <div className="flex space-x-2 mt-2">
                <button
                  onClick={() => {
                    onReply(comment.id, replyContent);
                    setReplyContent('');
                    setShowReplyForm(false);
                  }}
                  className="px-4 py-1 bg-purple-600 text-white rounded-lg
                           hover:bg-purple-700 transition-colors"
                >
                  Yanıtla
                </button>
                <button
                  onClick={() => {
                    setShowReplyForm(false);
                    setReplyContent('');
                  }}
                  className="px-4 py-1 bg-gray-700 text-gray-300 rounded-lg
                           hover:bg-gray-600 transition-colors"
                >
                  İptal
                </button>
              </div>
            </div>
          )}

          {/* Alt Yorumlar - Recursive */}
          {comment.replies && comment.replies.length > 0 && (
            <div className="mt-4 space-y-4 pl-8 border-l-2 border-gray-700">
              {comment.replies.map(reply => (
                <CommentItem key={reply.id} comment={reply} onReply={onReply} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function PostDetail() {
  const { id } = useParams();
  const { tokens } = useAuth();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [liked, setLiked] = useState(false);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [replyTo, setReplyTo] = useState(null);
  const [replyContent, setReplyContent] = useState('');

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const response = await fetch(`http://localhost:8000/blog/posts/${id}/`, {
          headers: {
            'Authorization': `Bearer ${tokens?.access}`
          }
        });

        if (!response.ok) throw new Error('Post yüklenemedi');

        const data = await response.json();
        setPost(data);
        setLiked(data.like_status);
      } catch (error) {
        console.error('Post fetch error:', error);
        toast.error('Post yüklenirken bir hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [id, tokens]);

  const organizeComments = (comments) => {
    const parentComments = comments.filter(comment => !comment.parent);
    const childComments = comments.filter(comment => comment.parent);
    
    return parentComments.map(parent => ({
      ...parent,
      replies: childComments.filter(child => child.parent === parent.id)
    }));
  };

  useEffect(() => {
    const getComments = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/blog/posts/${id}/comments/`, {
          headers: {
            'Authorization': `Bearer ${tokens?.access}`
          }
        });

        if (!response.ok) throw new Error('Yorumlar yüklenemedi');
        const data = await response.json();
        const validComments = data.filter(comment => comment !== null);
        setComments(validComments);
      } catch (error) {
        toast.error('Yorumlar yüklenirken bir hata oluştu');
      }
    };

    if (id && tokens?.access) {
      getComments();
    }
  }, [id, tokens]);

  const handleLike = async () => {
    if (!tokens?.access) {
      toast.error('Beğenmek için giriş yapmalısınız');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/blog/posts/${id}/like/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access}`
        }
      });

      if (!response.ok) throw new Error('İşlem başarısız');

      setLiked(!liked);
      setPost(prev => ({
        ...prev,
        like_count: liked ? prev.like_count - 1 : prev.like_count + 1
      }));

      toast.success(liked ? 'Beğeni kaldırıldı' : 'Post beğenildi');
    } catch (error) {
      setLiked(liked);
      setPost(prev => ({
        ...prev,
        like_count: liked ? prev.like_count : prev.like_count - 1
      }));
      toast.error('Bir hata oluştu');
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      const response = await fetch(`http://127.0.0.1:8000/blog/posts/${id}/comments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens?.access}`
        },
        body: JSON.stringify({ content: newComment })
      });

      if (!response.ok) throw new Error('Yorum eklenemedi');
      
      const newCommentData = await response.json();
      setComments(prevComments => [newCommentData, ...prevComments]);
      setNewComment('');
      toast.success('Yorumunuz eklendi');
    } catch (error) {
      toast.error('Yorum eklenirken bir hata oluştu');
    }
  };

  const handleReply = async (parentId, content) => {
    if (!content.trim()) return;

    try {
      const response = await fetch(`http://127.0.0.1:8000/blog/posts/${id}/comments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens?.access}`
        },
        body: JSON.stringify({
          content: content,
          parent: parentId
        })
      });

      if (!response.ok) throw new Error('Yanıt eklenemedi');

      const newReply = await response.json();
      
      // State'i güncelle - yorumları recursive olarak kontrol et
      setComments(prevComments => {
        return prevComments.map(comment => {
          if (comment.id === parentId) {
            // Ana yoruma yanıt eklendi
            return {
              ...comment,
              replies: [...(comment.replies || []), newReply],
              reply_count: (comment.reply_count || 0) + 1
            };
          }
          // Alt yorumlarda yanıt var mı diye kontrol et
          if (comment.replies) {
            return {
              ...comment,
              replies: comment.replies.map(reply => {
                if (reply.id === parentId) {
                  // Alt yoruma yanıt eklendi
                  return {
                    ...reply,
                    replies: [...(reply.replies || []), newReply],
                    reply_count: (reply.reply_count || 0) + 1
                  };
                }
                return reply;
              })
            };
          }
          return comment;
        });
      });

      toast.success('Yanıtınız eklendi');
    } catch (error) {
      toast.error('Yanıt eklenirken bir hata oluştu');
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
        </div>
      </MainLayout>
    );
  }

  if (!post) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center min-h-screen">
          <div className="text-center text-gray-400">Post bulunamadı</div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <article className="max-w-4xl mx-auto px-4 py-8">
        {/* Post Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">
            {post.title}
          </h1>

          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <Link to={`/profile/${post.author.username}`} className="flex items-center space-x-3">
                <img
                  src={post.author.profile_picture || '/default-avatar.png'}
                  alt={post.author.username}
                  className="h-10 w-10 rounded-full object-cover"
                />
                <div>
                  <div className="text-white font-medium">{post.author.full_name || post.author.username}</div>
                  <div className="text-sm text-gray-400">@{post.author.username}</div>
                </div>
              </Link>
            </div>

            <div className="flex items-center space-x-6 text-gray-400">
              <div className="flex items-center space-x-2">
                <CalendarIcon className="h-5 w-5" />
                <span>{new Date(post.created_at).toLocaleDateString('tr-TR')}</span>
              </div>
              {post.location && (
                <div className="flex items-center space-x-2">
                  <MapPinIcon className="h-5 w-5" />
                  <span>{post.location}</span>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Post Cover Image */}
        {post.cover_image && (
          <div className="mb-8 rounded-2xl overflow-hidden">
            <img
              src={post.cover_image}
              alt={post.title}
              className="w-full h-[400px] object-cover"
            />
          </div>
        )}

        {/* Post Content */}
        <div className="prose prose-invert prose-lg max-w-none mb-8">
          <div dangerouslySetInnerHTML={{ __html: post.content }} />
        </div>

        {/* Post Footer */}
        <footer className="border-t border-gray-800 pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <button
                onClick={handleLike}
                className="flex items-center space-x-2 text-gray-400 hover:text-red-500 transition-colors"
              >
                {liked ? (
                  <HeartIconSolid className="h-6 w-6 text-red-500" />
                ) : (
                  <HeartIcon className="h-6 w-6" />
                )}
                <span>{post.like_count}</span>
              </button>
              <div className="flex items-center space-x-2 text-gray-400">
                <ChatBubbleLeftIcon className="h-6 w-6" />
                <span>{post.comment_count}</span>
              </div>
            </div>

            {post.tags_list && post.tags_list.length > 0 && (
              <div className="flex items-center space-x-2">
                {post.tags_list.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gray-800 text-gray-300 rounded-full text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </footer>
      </article>

      {/* Yorumlar Bölümü */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold text-white mb-6">
          Yorumlar {comments.length > 0 && `(${comments.length})`}
        </h2>

        {/* Yorum Formu */}
        {tokens?.access ? (
          <form onSubmit={handleAddComment} className="mb-8">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Yorumunuzu yazın..."
              className="w-full bg-gray-800 text-white rounded-lg p-4 min-h-[100px]
                       focus:outline-none focus:ring-2 focus:ring-purple-600"
            />
            <button
              type="submit"
              className="mt-2 px-6 py-2 bg-purple-600 text-white rounded-lg
                       hover:bg-purple-700 transition-colors"
            >
              Yorum Yap
            </button>
          </form>
        ) : (
          <div className="text-center text-gray-400 mb-8">
            Yorum yapmak için <Link to="/login" className="text-purple-500">giriş yapın</Link>
          </div>
        )}

        {/* Yorumlar Listesi */}
        <div className="space-y-6">
          {comments.map(comment => (
            <CommentItem 
              key={comment.id} 
              comment={comment} 
              onReply={handleReply}
            />
          ))}
        </div>
      </div>
    </MainLayout>
  );
}

export default PostDetail; 