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
};
