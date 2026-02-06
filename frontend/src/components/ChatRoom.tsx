import { useState, useRef, useEffect, ChangeEvent } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { api } from '../services/api';
import { Message } from './Message';

interface ChatRoomProps {
  roomId: string;
  username: string;
  onLeave: () => void;
}

export const ChatRoom = ({ roomId, username, onLeave }: ChatRoomProps) => {
  const [messageInput, setMessageInput] = useState('');
  const [uploading, setUploading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const { messages, isConnected, error, sendMessage, connect, disconnect, loadHistory, typingUsers: wsTypingUsers } =
    useWebSocket();

  // Load chat history when room is opened
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        setLoadingHistory(true);
        const response = await api.getChatHistory(roomId, 50);
        if (response.messages && response.messages.length > 0) {
          loadHistory(response.messages);
        }
      } catch (err) {
        console.error('Failed to load chat history:', err);
      } finally {
        setLoadingHistory(false);
      }
    };

    loadChatHistory();
  }, [roomId, loadHistory]);

  // Connect to WebSocket after loading history
  useEffect(() => {
    if (!loadingHistory) {
      connect(roomId, username);
    }
    return () => disconnect();
  }, [roomId, username, loadingHistory, connect, disconnect]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Sync typing users from WebSocket
  useEffect(() => {
    setTypingUsers(wsTypingUsers);
  }, [wsTypingUsers]);

  // Handle input change with typing indicator
  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setMessageInput(value);

    // Send typing_start if not already typing
    if (!isTyping && value.length > 0) {
      setIsTyping(true);
      sendMessage({ type: 'typing_start', username });
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set new timeout for typing_stop (1.5 seconds after last keystroke)
    if (value.length > 0) {
      typingTimeoutRef.current = setTimeout(() => {
        setIsTyping(false);
        sendMessage({ type: 'typing_stop', username });
      }, 1500);
    } else {
      // If input is cleared, stop typing immediately
      setIsTyping(false);
      sendMessage({ type: 'typing_stop', username });
    }
  };

  const handleSendMessage = () => {
    if (messageInput.trim()) {
      // Clear typing indicator before sending
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      setIsTyping(false);
      sendMessage({ type: 'typing_stop', username });
      
      // Send actual message
      sendMessage(messageInput.trim());
      setMessageInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const response = await api.uploadFile(file, roomId, username);
      
      // Send file message via WebSocket
      sendMessage({
        type: 'file',
        username: username,
        file_url: response.file_url,
        file_name: response.file_name,
        file_size: response.file_size,
        file_type: response.file_type,
      });
    } catch (err) {
      alert(`Dosya yükleme hatası: ${err}`);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleLeave = () => {
    disconnect();
    onLeave();
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-4 shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">{roomId}</h2>
            <p className="text-sm opacity-90">
              {isConnected ? '🟢 Bağlı' : '🔴 Bağlantı kesildi'} • {username}
            </p>
          </div>
          <button
            onClick={handleLeave}
            className="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition"
          >
            Çıkış 👋
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {error && (
          <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
            ⚠️ {error}
          </div>
        )}
        {messages.map((msg, idx) => (
          <Message key={idx} message={msg} currentUsername={username} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Typing Indicator */}
      {typingUsers.length > 0 && (
        <div className="px-4 py-2 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
            </div>
            <span className="italic">
              {typingUsers.length === 1
                ? `${typingUsers[0]} yazıyor...`
                : typingUsers.length === 2
                ? `${typingUsers[0]} ve ${typingUsers[1]} yazıyor...`
                : `${typingUsers.length} kişi yazıyor...`}
            </span>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="bg-white border-t border-gray-300 p-4">
        <div className="flex items-center gap-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            accept=".pdf,.jpg,.jpeg,.png,.gif,.doc,.docx"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading || !isConnected}
            className="bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed p-3 rounded-lg transition"
            title="Dosya yükle"
          >
            {uploading ? '⏳' : '📎'}
          </button>
          <input
            type="text"
            value={messageInput}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Mesajınızı yazın..."
            disabled={!isConnected}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:opacity-50"
          />
          <button
            onClick={handleSendMessage}
            disabled={!isConnected || !messageInput.trim()}
            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-semibold"
          >
            Gönder 🚀
          </button>
        </div>
      </div>
    </div>
  );
};
