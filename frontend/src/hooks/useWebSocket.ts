import { useState, useEffect, useRef, useCallback } from 'react';
import type { Message } from '../types/index';

const WS_URL = 'ws://localhost:8000';

interface UseWebSocketReturn {
  messages: Message[];
  isConnected: boolean;
  error: string | null;
  sendMessage: (content: string | object) => void;
  connect: (roomId: string, username: string) => void;
  disconnect: () => void;
  loadHistory: (history: Message[]) => void;
  typingUsers: string[];
}

export const useWebSocket = (): UseWebSocketReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const roomIdRef = useRef<string>('');
  const usernameRef = useRef<string>('');

  const connect = useCallback((roomId: string, username: string) => {
    roomIdRef.current = roomId;
    usernameRef.current = username;

    try {
      const ws = new WebSocket(`${WS_URL}/ws/${roomId}?username=${username}`);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const message: Message = JSON.parse(event.data);
          
          // Handle typing indicators
          if (message.type === 'typing_start') {
            setTypingUsers((prev) => {
              if (!prev.includes(message.username)) {
                return [...prev, message.username];
              }
              return prev;
            });
          } else if (message.type === 'typing_stop') {
            setTypingUsers((prev) => prev.filter((user) => user !== message.username));
          } else {
            // Regular message - add to messages list
            setMessages((prev) => [...prev, message]);
          }
        } catch (err) {
          console.error('Failed to parse message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('Bağlantı hatası oluştu');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Connection error:', err);
      setError('Sunucuya bağlanılamadı');
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setIsConnected(false);
      setMessages([]);
      setTypingUsers([]);
    }
  }, []);

  const sendMessage = useCallback((contentOrData: string | object) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const data = typeof contentOrData === 'string' 
        ? { content: contentOrData } 
        : contentOrData;
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  const loadHistory = useCallback((history: Message[]) => {
    setMessages(history);
  }, []);

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    messages,
    isConnected,
    error,
    sendMessage,
    connect,
    disconnect,
    loadHistory,
    typingUsers,
  };
};
