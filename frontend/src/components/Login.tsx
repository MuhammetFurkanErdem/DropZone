import { useState, FormEvent } from 'react';
import { api } from '../services/api';

interface LoginProps {
  onLogin: (roomId: string, username: string, roomName?: string) => void;
}

export const Login = ({ onLogin }: LoginProps) => {
  const [activeTab, setActiveTab] = useState<'join' | 'create'>('join');
  const [roomCode, setRoomCode] = useState('');
  const [roomName, setRoomName] = useState('');
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [createdCode, setCreatedCode] = useState('');

  const handleJoinSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Oda kodunu kontrol et
      const response = await api.checkRoom(roomCode.trim().toUpperCase());
      
      if (response.exists) {
        onLogin(roomCode.trim().toUpperCase(), username.trim(), response.room_name);
      } else {
        setError('Bu oda kodu bulunamadı. Lütfen doğru kodu girdiğinizden emin olun.');
      }
    } catch (err) {
      setError('Oda kontrol edilirken hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Yeni oda oluştur
      const response = await api.createRoom(roomName.trim());
      
      if (response.success) {
        setCreatedCode(response.code);
        // 2 saniye bekle, sonra odaya gir
        setTimeout(() => {
          onLogin(response.code, username.trim(), response.room_name);
        }, 2000);
      } else {
        setError('Oda oluşturulamadı.');
      }
    } catch (err) {
      setError('Oda oluşturulurken hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">DropZone</h1>
          <p className="text-gray-600">
            Gerçek zamanlı not paylaşımı ve sohbet platformu
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-6">
          <button
            onClick={() => {
              setActiveTab('join');
              setError('');
              setCreatedCode('');
            }}
            className={`flex-1 py-3 px-4 font-medium transition ${
              activeTab === 'join'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Odaya Katıl
          </button>
          <button
            onClick={() => {
              setActiveTab('create');
              setError('');
              setCreatedCode('');
            }}
            className={`flex-1 py-3 px-4 font-medium transition ${
              activeTab === 'create'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Yeni Oda Oluştur
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Join Tab */}
        {activeTab === 'join' && (
          <form onSubmit={handleJoinSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="roomCode"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Oda Kodu
              </label>
              <input
                type="text"
                id="roomCode"
                value={roomCode}
                onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                placeholder="örn: A7X-29K"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition uppercase"
                required
                maxLength={7}
              />
              <p className="mt-1 text-xs text-gray-500">
                6 haneli oda kodunu giriniz (XXX-XXX formatında)
              </p>
            </div>

            <div>
              <label
                htmlFor="username-join"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Kullanıcı Adı
              </label>
              <input
                type="text"
                id="username-join"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Adınız"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-600 hover:to-purple-700 transition transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {loading ? 'Kontrol ediliyor...' : 'Odaya Katıl 🚀'}
            </button>
          </form>
        )}

        {/* Create Tab */}
        {activeTab === 'create' && (
          <form onSubmit={handleCreateSubmit} className="space-y-6">
            {createdCode ? (
              <div className="text-center py-8">
                <div className="mb-4">
                  <span className="text-sm text-gray-600">Oda Kodunuz:</span>
                  <div className="text-4xl font-bold text-blue-600 my-3 tracking-wider">
                    {createdCode}
                  </div>
                  <p className="text-sm text-gray-500">
                    Bu kodu arkadaşlarınızla paylaşın! 📋
                  </p>
                </div>
                <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                  <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  <span>Odaya yönlendiriliyorsunuz...</span>
                </div>
              </div>
            ) : (
              <>
                <div>
                  <label
                    htmlFor="roomName"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Oda Adı
                  </label>
                  <input
                    type="text"
                    id="roomName"
                    value={roomName}
                    onChange={(e) => setRoomName(e.target.value)}
                    placeholder="örn: Matematik 101 Çalışma Grubu"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    required
                  />
                </div>

                <div>
                  <label
                    htmlFor="username-create"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Kullanıcı Adı
                  </label>
                  <input
                    type="text"
                    id="username-create"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Adınız"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-green-500 to-teal-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-green-600 hover:to-teal-700 transition transform hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {loading ? 'Oda Oluşturuluyor...' : 'Yeni Oda Oluştur ✨'}
                </button>

                <div className="text-center text-sm text-gray-500">
                  <p>💡 Sistem otomatik olarak benzersiz bir kod üretecektir</p>
                </div>
              </>
            )}
          </form>
        )}
      </div>
    </div>
  );
};
