import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { toast, Toaster } from 'react-hot-toast';

function VerifyEmail() {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [verificationCode, setVerificationCode] = useState('');
  const email = location.state?.email || '';
  const userId = location.state?.userId || '';

  const handleResendCode = async () => {
    if (!userId || resendLoading) return;
    
    setResendLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/users/resend-verification-code/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId })
      });

      const data = await response.json();

      if (!response.ok) {
        toast.error(data.error || 'Kod gönderme başarısız oldu');
        return;
      }

      toast.success('Yeni doğrulama kodu gönderildi!');
      setVerificationCode('');

    } catch (error) {
      console.error('Kod gönderme hatası:', error);
      toast.error('Bir hata oluştu');
    } finally {
      setResendLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    if (!userId) {
      toast.error('Kullanıcı bilgisi bulunamadı');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/users/verify-email/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: verificationCode.trim(),
          user_id: userId
        })
      });

      const data = await response.json();
      console.log('Response:', data);

      if (!response.ok) {
        if (data.error) {
          toast.error(data.error);
        } else {
          toast.error('Doğrulama başarısız oldu');
        }
        return;
      }

      toast.success(data.message || 'Email başarıyla doğrulandı!');
      setTimeout(() => {
        navigate('/login');
      }, 2000);

    } catch (error) {
      console.error('Doğrulama hatası:', error);
      toast.error('Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleCodeChange = (e) => {
    const value = e.target.value.replace(/\D/g, '');
    if (value.length <= 6) {
      setVerificationCode(value);
    }
  };

  if (!email || !userId) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-gray-800/50 backdrop-blur-xl p-8 rounded-2xl shadow-xl">
          <div className="text-center text-white">
            <h2 className="text-2xl font-bold mb-4">Geçersiz Erişim</h2>
            <p className="text-gray-400 mb-4">
              Bu sayfaya doğrudan erişim yapılamaz.
            </p>
            <button
              onClick={() => navigate('/register')}
              className="w-full py-2 px-4 bg-purple-600 text-white rounded-lg 
                       hover:bg-purple-700 transition-colors"
            >
              Kayıt Sayfasına Dön
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-gray-800/50 backdrop-blur-xl p-8 rounded-2xl shadow-xl">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-purple-600/20 backdrop-blur-xl rounded-full 
                         flex items-center justify-center mb-6">
            <svg className="h-8 w-8 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-white">
            Email Doğrulama
          </h2>
          <p className="mt-2 text-sm text-gray-400">
            Email adresinize gönderilen 6 haneli kodu giriniz
          </p>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300">
              Doğrulama Kodu
            </label>
            <input
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              maxLength="6"
              value={verificationCode}
              onChange={handleCodeChange}
              className="mt-1 block w-full px-3 py-2 bg-gray-700/50 border border-gray-600 
                       rounded-lg text-gray-300 text-center text-2xl tracking-widest
                       focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500
                       placeholder:text-gray-500"
              placeholder="000000"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading || verificationCode.length !== 6}
            className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg
                     text-sm font-medium text-white bg-purple-600 hover:bg-purple-700
                     focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-all duration-200"
          >
            {loading ? 'Doğrulanıyor...' : 'Doğrula'}
          </button>

          {email && (
            <div className="text-center space-y-4">
              <p className="text-sm text-gray-400">
                Doğrulama kodu <span className="text-purple-400">{email}</span> adresine gönderildi
              </p>
              
              <button
                type="button"
                onClick={handleResendCode}
                disabled={resendLoading}
                className="text-sm text-purple-400 hover:text-purple-300 transition-colors
                         disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {resendLoading ? 'Kod gönderiliyor...' : 'Yeni kod gönder'}
              </button>
            </div>
          )}
        </form>
      </div>
      <Toaster position="top-center" />
    </div>
  );
}

export default VerifyEmail; 