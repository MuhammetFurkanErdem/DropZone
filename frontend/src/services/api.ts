const API_URL = 'http://localhost:8000';

export const api = {
  // Get active rooms
  getRooms: async () => {
    const response = await fetch(`${API_URL}/rooms`);
    if (!response.ok) throw new Error('Failed to fetch rooms');
    return response.json();
  },

  // Upload file
  uploadFile: async (file: File, roomId: string, username: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('room_id', roomId);
    formData.append('username', username);

    const response = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  },

  // Get upload info
  getUploadInfo: async () => {
    const response = await fetch(`${API_URL}/upload/info`);
    if (!response.ok) throw new Error('Failed to fetch upload info');
    return response.json();
  },

  // Get chat history
  getChatHistory: async (roomId: string, limit: number = 50) => {
    const response = await fetch(`${API_URL}/chat/${roomId}/history?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch chat history');
    return response.json();
  },

  // Create new room
  createRoom: async (roomName: string) => {
    const response = await fetch(`${API_URL}/rooms/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ room_name: roomName }),
    });
    if (!response.ok) throw new Error('Failed to create room');
    return response.json();
  },

  // Check if room exists
  checkRoom: async (code: string) => {
    const response = await fetch(`${API_URL}/rooms/${code}/check`);
    if (!response.ok) throw new Error('Failed to check room');
    return response.json();
  },

  // Get room details by code
  getRoomDetails: async (code: string) => {
    const response = await fetch(`${API_URL}/rooms/${code}/check`);
    if (!response.ok) throw new Error('Failed to get room details');
    return response.json();
  },
};
