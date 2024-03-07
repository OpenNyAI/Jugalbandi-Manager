import React from "react";
import { useLocation } from "react-router-dom";
import { sendRequest } from "@/api";
import AudioPlayer from '@/components/audio-player';
import { useAuth } from "@/context/AuthContext";
import moment from 'moment';
import './chat.css';
const APIHOST = import.meta.env.VITE_SERVER_HOST;

interface props {

}
export const Chat:React.FunctionComponent = (props: props) => {
  const [chatSessions, setChatSessions] = React.useState([]);
  const [selectedSession, setSelectedSession] = React.useState<any>(null);
  const [playingId, setPlayingId] = React.useState<string | null>(null);
  const [sessionMessages, setSessionMessages] = React.useState<any>([]);
  const { getToken, getAuthMethodTypem, logOut } = useAuth();
  const [token, setToken] = React.useState('');
  const location = useLocation();

  const { from, bot_id } = location.state;
  React.useEffect(() => {
    if (bot_id) {
      sendRequest({
        url: `${APIHOST}/chats/${bot_id}`,
        accessToken: token,
        loginMethod: getAuthMethodType(),
        onUnauthorized: logOut
      }).then((response:any) => {
        setChatSessions(response);
        loadMessages(response[0]);
      });
    }
  }, [bot_id]);

  React.useEffect(() => {
    getToken().then((token:string) => {
      setToken(token);
    });
  },[]);

  const loadMessages = (session:any) => {
    setSelectedSession(session.id);
    sendRequest({
      url: `${APIHOST}/chats/${bot_id}/sessions/${session.id}`,
      accessToken: token,
      loginMethod: getAuthMethodType(),
      onUnauthorized: logOut
    }).then((response:any) => {
      if (response && response.length) {
        setSessionMessages(response[0]);
      }
      
    });
  }

  const handleTogglePlay = (id:string) => {
    setPlayingId(playingId === id ? null : id);
  };


  const loadMessage = (message:any, index: number) => {
    if (message.message_type === 'text' || message.message_type === 'image') {
      return (
      <div className={message.is_user_sent ? 'message sender': 'message receiver'} key={index}>
        <div className="chat-message-info">
          <p>{message.message_text}</p>
        </div>  
      </div>)
    } else if (message.message_type === 'interactive') {
      return (<div className={message.is_user_sent ? 'message sender': 'message receiver'} key={index}>
        <div className="chat-message-info">
          <p>{message.message_text || "User selected from the menu (Interactive Msg)"}</p>
        </div>  
      </div>)
    }
     else if (message.message_type === 'audio') {
      //return <></>;
      return (<div className={message.is_user_sent ? 'message sender': 'message receiver'} key={index}>
      <div className="chat-message-info">
        <AudioPlayer
          key={message.id}
          src={message.media_url}
          isPlaying={playingId === message.id}
          onTogglePlay={() => handleTogglePlay(message.id)}
        />
      </div>  
    </div>)
    }
    return <></>;
  }

  return (
    <div className="chats">
      <div className="chat-container">
          <div className="chat-sidebar">
            {chatSessions && chatSessions.map((session:any, index) => {
                return (
                  <div onClick={() => loadMessages(session)} key={index} className="chat-session">
                    <div className={session.id === selectedSession ? 'chat-session-info selected' : 'chat-session-info'}>
                      <div className="user-info">
                        <div>{session.user.phone_number}</div>
                      </div>
                      <div className={'channel-info'}>
                        <div>
                          <img className="channel-icon" src="whatsapp.svg" />
                        </div>
                        <div>{moment(session.created_at).format('DD/MM/YYYY')}</div>
                      </div>
                    </div>
                  </div>
                );
              })
            }
          </div>
          <div className="chat-messages">
            {sessionMessages && sessionMessages?.turns && sessionMessages.turns.map((turn:any, index:number) => {
              return(
              <>
              {turn?.messages && turn.messages.map((message:any, index:number) => {
                return (
                  loadMessage(message, index)
                );
              })}
              </>)
            })
            }
          </div>
      </div>
    </div>
  );
}

export default Chat;