import { useState } from 'react';
import { Login } from './components/Login';
import { ChatRoom } from './components/ChatRoom';
import type { UserState } from './types/index';

function App() {
  const [userState, setUserState] = useState<UserState | null>(null);

  const handleLogin = (roomId: string, username: string) => {
    setUserState({
      username,
      room_id: roomId,
      isConnected: true,
    });
  };

  const handleLeave = () => {
    setUserState(null);
  };

  return (
    <>
      {!userState ? (
        <Login onLogin={handleLogin} />
      ) : (
        <ChatRoom
          roomId={userState.room_id}
          username={userState.username}
          onLeave={handleLeave}
        />
      )}
    </>
  );
}

export default App;
