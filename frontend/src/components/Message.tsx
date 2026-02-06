import type { Message as MessageType } from '../types/index';

interface MessageProps {
  message: MessageType;
  currentUsername: string;
}

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
          <div className="bg-white bg-opacity-20 rounded p-2 mb-2">
            <div className="flex items-center gap-2">
              <span className="text-2xl">📄</span>
              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">{message.file_name}</div>
                <div className="text-xs opacity-75">
                  {message.file_size &&
                    `${(message.file_size / 1024).toFixed(1)} KB`}
                </div>
              </div>
            </div>
          </div>
          <a
            href={`http://localhost:8000${message.file_url}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs underline opacity-75 hover:opacity-100"
          >
            İndir ⬇️
          </a>
          <div className="text-xs opacity-75 mt-1">
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
