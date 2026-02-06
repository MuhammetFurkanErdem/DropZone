import { useState, useEffect, useRef, useCallback } from 'react';
import type { Message } from '../types/index';

const WS_URL = 'ws://localhost:8000';

interface UseWebSocketReturn {
  messages: Message[];
  isConnected: boolean;
  error: string | null;
  sendMessage: (content: string) => void;
  connect: (roomId: string, username: string) => void;
  disconnect: () => void;
}

export const useWebSocket = (): UseWebSocketReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
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
          setMessages((prev) => [...prev, message]);
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
    }
  }, []);

  const sendMessage = useCallback((content: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ content }));
    }
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
  };
};
