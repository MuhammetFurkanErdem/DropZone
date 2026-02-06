// Message types
export interface Message {
  type: 'join' | 'leave' | 'message' | 'file' | 'error' | 'system';
  username: string;
  timestamp: string;
  content?: string;
  message?: string;
  room_users?: string[];
  file_url?: string;
  file_name?: string;
  file_size?: number;
  file_type?: string;
  error_code?: string;
  severity?: 'info' | 'warning' | 'success';
}

// Room info
export interface RoomInfo {
  room_id: string;
  user_count: number;
  users: string[];
}

// Upload response
export interface UploadResponse {
  success: boolean;
  file_url: string;
  file_name: string;
  file_size: number;
  file_type: string;
  uploaded_at: string;
}

// User state
export interface UserState {
  username: string;
  room_id: string;
  isConnected: boolean;
}
