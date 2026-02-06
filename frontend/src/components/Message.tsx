import type { Message as MessageType } from '../types/index';
import { FileText, Download, Image as ImageIcon } from 'lucide-react';

interface MessageProps {
  message: MessageType;
  currentUsername: string;
}

// Helper function to determine file type
const getFileType = (filename: string | undefined): 'image' | 'pdf' | 'other' => {
  if (!filename) return 'other';
  
  const ext = filename.split('.').pop()?.toLowerCase();
  
  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext || '')) {
    return 'image';
  }
  if (ext === 'pdf') {
    return 'pdf';
  }
  return 'other';
};

export const Message = ({ message, currentUsername }: MessageProps) => {
  const isOwnMessage = message.username === currentUsername;
  const isSystemMessage = ['join', 'leave', 'system'].includes(message.type);

  if (isSystemMessage) {
    return (
      <div className="flex justify-center my-2">
        <div className="bg-gray-200 text-gray-600 text-sm px-4 py-2 rounded-full">
          {message.message || message.content}
        </div>
      </div>
    );
  }

  if (message.type === 'file') {
    const fileType = getFileType(message.file_name);
    const fileUrl = `http://localhost:8000${message.file_url}`;

    return (
      <div
        className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-4`}
      >
        <div
          className={`max-w-md ${
            isOwnMessage
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-800'
          } rounded-lg px-4 py-3 shadow-lg`}
        >
          <div className="font-semibold text-sm mb-2">{message.username}</div>

          {/* Image Preview */}
          {fileType === 'image' && (
            <div className="mb-2">
              <a
                href={fileUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="block"
              >
                <img
                  src={fileUrl}
                  alt={message.file_name || 'Image'}
                  className="max-h-[200px] w-auto rounded-lg hover:opacity-90 transition-opacity cursor-pointer border-2 border-white/20"
                  loading="lazy"
                />
              </a>
              <div className="mt-2 text-xs opacity-75">
                {message.file_name}
              </div>
            </div>
          )}

          {/* PDF Preview */}
          {fileType === 'pdf' && (
            <a
              href={fileUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="block mb-2"
            >
              <div className="bg-white bg-opacity-10 hover:bg-opacity-20 transition-all rounded-lg p-3 border-2 border-white/20 cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="bg-red-500 p-2 rounded-lg">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate text-sm">
                      {message.file_name}
                    </div>
                    <div className="text-xs opacity-75 flex items-center gap-2">
                      <span>PDF Doküman</span>
                      {message.file_size && (
                        <span>• {(message.file_size / 1024).toFixed(1)} KB</span>
                      )}
                    </div>
                  </div>
                  <Download className="w-4 h-4 opacity-75" />
                </div>
              </div>
            </a>
          )}

          {/* Other Files */}
          {fileType === 'other' && (
            <a
              href={fileUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="block mb-2"
            >
              <div className="bg-white bg-opacity-10 hover:bg-opacity-20 transition-all rounded-lg p-3 border-2 border-white/20 cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="bg-gray-500 p-2 rounded-lg">
                    <Download className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate text-sm">
                      {message.file_name}
                    </div>
                    <div className="text-xs opacity-75">
                      {message.file_size &&
                        `${(message.file_size / 1024).toFixed(1)} KB`}
                    </div>
                  </div>
                </div>
              </div>
            </a>
          )}

          <div className="text-xs opacity-75">
            {new Date(message.timestamp).toLocaleTimeString('tr-TR', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-xs lg:max-w-md ${
          isOwnMessage
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 text-gray-800'
        } rounded-lg px-4 py-2 shadow`}
      >
        <div className="font-semibold text-sm mb-1">{message.username}</div>
        <div className="break-words">{message.content}</div>
        <div className="text-xs opacity-75 mt-1">
          {new Date(message.timestamp).toLocaleTimeString('tr-TR', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
};
