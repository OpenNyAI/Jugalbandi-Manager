//This Page helps creating and modifying the Channel details as well as the bot credentials.
import React, { useState, useEffect } from 'react';
import { sendRequest } from '../../api';
import './BotSettings.css'; // Import the CSS file
import { Console, log } from 'console';
import SettingsModal from '../../components/settings-model';
import { channel } from 'diagnostics_channel';
import ConfirmationModal from '../../components/confirmation-model/Confirmation-Model';

const APIHOST = import.meta.env.VITE_SERVER_HOST;

interface Bot {
  id: string;
  name: string;
  required_credentials: string[];
  credentials: { [key: string]: string };
  channels: Channel[];
}

interface Channel {
  id: string;
  name: string;
  type: string;
  url: string;
  status: string;
  app_id: string;
  key: string;
}

interface BotSettingsProps {
  botID?: string;
}

export const BotSettings: React.FunctionComponent<BotSettingsProps> = ({botID}) => {
  const [bots, setBots] = useState<Bot[]>([]);
  const [selectedBot, setSelectedBot] = useState<Bot | null>(null);
  const [isSettingsModelOpen, showModel] = React.useState(false);
  const [modelData, setDataForModel] = React.useState<any>();
  const [selectedChannelID, setSelectedChannelID] = React.useState<string>("");
  const [isConfirmationOpen, setIsConfirmationOpen] = useState(false); 
  const [channelToDelete, setChannelToDelete] = useState<string | null>(null); 
  const [availableChannelTypes,setAvailableChannelTyps] = useState<string[]|null> (null);

  // RefreshData function refreshes the bots and available channel types
  // If selectedBot is not null then that particular bot is selected after refresh data.

  const RefreshData = async ()=>{
    try {
      sendRequest({
        url: `${APIHOST}/v2/bot/`
      }).then((response: any) => {
        setBots(response);
        console.log("URL Bot ID: ",botID);
        if(botID!=null){
          const bot = response.find((b) => b.id === botID) || null;
          setSelectedBot(bot);
        }
        else if(selectedBot!=null){
          const bot = response.find((b) => b.id === selectedBot.id) || null;
          setSelectedBot(bot);
        }
        else{
          setSelectedBot(response[0]);
        }
      });
    } catch (error) {
      console.error('Error fetching bots:', error);
    }
    try {
      sendRequest({
        url: `${APIHOST}/v2/channel/`
      }).then((response: any) => {
        setAvailableChannelTyps(response);
      });
    } catch (error) {
      console.error('Error fetching channel types:', error);
    }
  }
  
  useEffect(() => {
    RefreshData();
  }, []);


  //Utility functions for various functionality.

  const closeModal = () => {
    showModel(false);
    RefreshData();
  }

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedBotId = event.target.value;
    const bot = bots.find(b => b.id === selectedBotId) || null;
    console.log(bot);
    setSelectedBot(bot);
  };

  const handleChannelToggle = (channelId: string, currentStatus: boolean) => {
    const newStatus = !currentStatus;
    const action = newStatus ? "activate" : "deactivate";
    console.log(`Toggling channel ${channelId} to ${newStatus ? 'active' : 'inactive'}`);
    console.log(selectedBot);
    console.Console;
    sendRequest({
      url: `${APIHOST}/v2/channel/${channelId}/${action}`,
    })
      .then((response: any) => {
        if (response.status === "success") {
          const updatedBots = bots.map((bot) =>
            bot.id === selectedBot?.id
              ? {
                  ...bot,
                  channels: bot.channels.map((channel) =>
                    channel.id === channelId
                      ? { ...channel, status: newStatus?"active":"inactive"  }
                      : channel
                  ),
                }
              : bot
          );
          const updatedSelectedBot = updatedBots.find(bot => bot.id === selectedBot?.id) || null;

          setBots(updatedBots);

          setSelectedBot(updatedSelectedBot);
          console.log('Channel status toggled successfully!');
        } else {
          console.error('Failed to toggle channel status:', response);
        }
      })
      .catch((error) => {
        console.error('Error updating status:', error);
      });
  };
  
  const handleDeleteClick = (channelId: string) => {
    setChannelToDelete(channelId);
    setIsConfirmationOpen(true);
  };

  const confirmDelete = () => {
    if (channelToDelete) {
      sendRequest({
        url: `${APIHOST}/v2/channel/${channelToDelete}/`,
        method: 'DELETE'
      }).then((response: any) => {
        if (response.status === 'success') {
          console.log("Channel deleted");
          RefreshData();
        }
      }).catch(error => {
        console.error('Error deleting channel:', error);
      });
      setIsConfirmationOpen(false);
    }
  };

  const cancelDelete = () => {
    setIsConfirmationOpen(false);
    setChannelToDelete(null);
  };

  const editConfig = () => {
    let config:any = {};
    for (let key of selectedBot?.required_credentials || []) {
        const value = selectedBot?.credentials && selectedBot.credentials[key] ? selectedBot.credentials[key] : '';
        config[key] = {
            value,
            is_secret: true
        };
    }
    setDataForModel({
        title: `Edit ${name} Settings`,
        inputs: config,
        botId: selectedBot?.id,
        modelType: "credentials"
    });
    showModel(true);
  }
  
  const handleModifyChannel = (channel: Channel) => {
    console.log(`Modified channel ${channel.id}`);
    setSelectedChannelID(channel.id);
    showModel(true);
    setDataForModel({
        title: 'Add New Channel',
        inputs: {
            name: {
                value: channel.name,
                type: 'string',
                required: true
            },
            type: {
                value: channel.type,
                type: 'text',
                required: true
            },
            url: {
                value: channel.url,
                type: 'text',
                required: true
            },
            app_id: {
                value: channel.app_id,
                type: 'text',
                required: true
            },
            key: {
                value: channel.key,
                type: 'text',
                required: true
            },

        },
        modelType: 'channelUpdate'
    });
  };

  const handleAddChannel = () => {
    showModel(true);
    setDataForModel({
        title: 'Add New Channel',
        inputs: {
            name: {
                value: '',
                type: 'string',
                required: true
            },
            type: {
              value: availableChannelTypes!=null?availableChannelTypes[0]:"",
              type: 'list',
              required: true,
              options: availableChannelTypes, 
              placeholder: 'Select Channel Type'
            },
            url: {
                value: '',
                type: 'text',
                required: true
            },
            app_id: {
                value: '',
                type: 'text',
                required: true
            },
            key: {
                value: '',
                type: 'text',
                required: true
            },

        },
        modelType: 'channelInstall'
    });
  };

  return (
    <div className="container">
      <SettingsModal title={modelData?.title} isOpen={isSettingsModelOpen} inputs={modelData?.inputs} onClose={closeModal} modelType={modelData?.modelType} botId={selectedBot?.id} bot_id='' onSave={()=>{}} channelID={selectedChannelID} />
      <ConfirmationModal 
        isOpen={isConfirmationOpen} 
        onClose={cancelDelete} 
        onConfirm={confirmDelete} 
        message="Are you sure you want to delete this channel?"
      />
      <div className='Bot-Section'>
        <h3>Select a Bot:</h3>
          <div className='Bot-Config'>
            <div className='Bot-Selector'>
              <select id="bot-select" value={selectedBot?.id || ''} onChange={handleChange}>
                {bots.map((bot) => (
                  <option key={bot.id} value={bot.id}>
                    {bot.name}
                  </option>
                ))}
              </select>
            </div>
            <div className='Bot-Editor'>
            <svg onClick={()=>{editConfig()}} xmlns="http://www.w3.org/2000/svg" className="bot-edit-icon" fill="none" height="30" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="24">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            </div>
        </div>
      </div>

      {selectedBot && (
        <div className="bot-details">
          <h3>Bot Details</h3>
          <p><strong>Channels:</strong></p>
          <ul>
            {selectedBot.channels
              .filter(channel => channel.status !== "deleted") 
              .map((channel) => (
                <li className='Channel-Item' key={channel.id}>
                  <div className='ChannelInfo'>
                    <div className='ChannelInfoLeft'>
                      {channel.name} ({channel.type})
                    </div>
                    <div className='ChannelInfoRight'>
                      <svg onClick={() => handleModifyChannel(channel)} className='settings-icon' xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 26 26" fill="none">
                        <path d="M13 8.5C10.4067 8.5 8.30435 10.5147 8.30435 13C8.30435 15.4853 10.4067 17.5 13 17.5C14.4075 17.5 15.6703 16.9066 16.5309 15.9666C17.2561 15.1745 17.6957 14.1365 17.6957 13C17.6957 12.5401 17.6236 12.0962 17.4899 11.6783C16.9007 9.838 15.1134 8.5 13 8.5ZM9.86957 13C9.86957 11.3431 11.2711 10 13 10C14.7289 10 16.1304 11.3431 16.1304 13C16.1304 14.6569 14.7289 16 13 16C11.2711 16 9.86957 14.6569 9.86957 13ZM21.0445 21.3947L19.2419 20.6364C18.7262 20.4197 18.1204 20.4514 17.633 20.7219C17.1457 20.9923 16.8348 21.4692 16.7729 22.0065L16.5561 23.8855C16.5115 24.2729 16.2181 24.5917 15.8231 24.6819C13.9665 25.106 12.0322 25.106 10.1756 24.6819C9.78062 24.5917 9.48727 24.2729 9.44258 23.8855L9.22618 22.0093C9.16262 21.473 8.83778 20.9976 8.3508 20.728C7.86383 20.4585 7.27253 20.4269 6.75853 20.6424L4.95552 21.4009C4.58207 21.558 4.14602 21.4718 3.86754 21.1858C2.57017 19.8536 1.60442 18.2561 1.04301 16.5136C0.922085 16.1383 1.0618 15.7307 1.3912 15.4976L2.9849 14.3703C3.43883 14.05 3.70693 13.5415 3.70693 13.0006C3.70693 12.4597 3.43883 11.9512 2.9843 11.6305L1.3916 10.5051C1.06172 10.272 0.921872 9.86375 1.04322 9.48812C1.60561 7.74728 2.57186 6.15157 3.86927 4.82108C4.14801 4.53522 4.58427 4.44935 4.95766 4.60685L6.75266 5.36398C7.26914 5.58162 7.86292 5.54875 8.35253 5.27409C8.84002 5.00258 9.16456 4.52521 9.22722 3.98787L9.44522 2.11011C9.49075 1.71797 9.79082 1.39697 10.1919 1.31131C11.1113 1.11498 12.0495 1.01065 13.0136 1C13.9545 1.01041 14.8916 1.11478 15.8099 1.31143C16.2108 1.39728 16.5106 1.71817 16.5561 2.11011L16.7742 3.98931C16.873 4.85214 17.6317 5.50566 18.5362 5.50657C18.7793 5.50694 19.0198 5.45832 19.2445 5.36288L21.0398 4.60562C21.4132 4.44812 21.8494 4.53399 22.1282 4.81984C23.4256 6.15034 24.3918 7.74605 24.9542 9.48689C25.0755 9.86227 24.9359 10.2702 24.6064 10.5034L23.0151 11.6297C22.5612 11.9499 22.287 12.4585 22.287 12.9994C22.287 13.5402 22.5612 14.0488 23.0161 14.3697L24.6088 15.4964C24.9384 15.7296 25.0781 16.1376 24.9568 16.513C24.3946 18.2536 23.4289 19.8491 22.1323 21.1799C21.8538 21.4657 21.4178 21.5518 21.0445 21.3947ZM15.3614 21.1965C15.6068 20.4684 16.1189 19.8288 16.8487 19.4238C17.7689 18.9132 18.8994 18.8546 19.8704 19.2626L21.2728 19.8526C22.1732 18.8537 22.8706 17.7013 23.3285 16.4551L22.0882 15.5777L22.0872 15.577C21.2414 14.9799 20.7217 14.0276 20.7217 12.9994C20.7217 11.9718 21.2408 11.0195 22.0858 10.4227L22.0872 10.4217L23.3259 9.54496C22.8679 8.29874 22.1702 7.1463 21.2694 6.14764L19.8788 6.73419L19.8764 6.73521C19.4533 6.91457 18.9971 7.00716 18.5345 7.00657C16.8311 7.00447 15.4048 5.77425 15.2185 4.15459L15.2183 4.15285L15.0489 2.69298C14.3776 2.57322 13.6967 2.50866 13.0136 2.50011C12.3102 2.50885 11.6248 2.57361 10.9524 2.69322L10.7828 4.15446C10.6652 5.16266 10.0567 6.05902 9.14112 6.5698C8.22022 7.08554 7.09864 7.14837 6.12211 6.73688L4.72806 6.14887C3.82729 7.14745 3.12965 8.29977 2.67161 9.54587L3.91319 10.4232C4.76816 11.0268 5.27214 11.9836 5.27214 13.0006C5.27214 14.0172 4.76844 14.9742 3.91378 15.5776L2.67125 16.4565C3.12872 17.7044 3.82626 18.8584 4.72736 19.8587L6.13122 19.2681C7.10168 18.8613 8.21641 18.9214 9.13361 19.4291C10.0511 19.9369 10.6619 20.8319 10.7814 21.84L10.7819 21.8445L10.9508 23.3087C12.3036 23.5638 13.6951 23.5638 15.0479 23.3087L15.2171 21.8417C15.2425 21.6217 15.291 21.4054 15.3614 21.1965Z" fill="#B3B3B3" stroke="#666666"/>
                      </svg>
                      <svg onClick={() => handleDeleteClick(channel.id)} className='delete-icon' xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 20 20" fill="none">
                          <path d="M5 2C5 1.46957 5.21071 0.960859 5.58579 0.585786C5.96086 0.210714 6.46957 0 7 0H13C13.5304 0 14.0391 0.210714 14.4142 0.585786C14.7893 0.960859 15 1.46957 15 2V4H19C19.2652 4 19.5196 4.10536 19.7071 4.29289C19.8946 4.48043 20 4.73478 20 5C20 5.26522 19.8946 5.51957 19.7071 5.70711C19.5196 5.89464 19.2652 6 19 6H17.931L17.064 18.142C17.0281 18.6466 16.8023 19.1188 16.4321 19.4636C16.0619 19.8083 15.5749 20 15.069 20H4.93C4.42414 20 3.93707 19.8083 3.56688 19.4636C3.1967 19.1188 2.97092 18.6466 2.935 18.142L2.07 6H1C0.734784 6 0.48043 5.89464 0.292893 5.70711C0.105357 5.51957 0 5.26522 0 5C0 4.73478 0.105357 4.48043 0.292893 4.29289C0.48043 4.10536 0.734784 4 1 4H5V2ZM7 4H13V2H7V4ZM4.074 6L4.931 18H15.07L15.927 6H4.074ZM8 8C8.26522 8 8.51957 8.10536 8.70711 8.29289C8.89464 8.48043 9 8.73478 9 9V15C9 15.2652 8.89464 15.5196 8.70711 15.7071C8.51957 15.8946 8.26522 16 8 16C7.73478 16 7.48043 15.8946 7.29289 15.7071C7.10536 15.5196 7 15.2652 7 15V9C7 8.73478 7.10536 8.48043 7.29289 8.29289C7.48043 8.10536 7.73478 8 8 8ZM12 8C12.2652 8 12.5196 8.10536 12.7071 8.29289C12.8946 8.48043 13 8.73478 13 9V15C13 15.2652 12.8946 15.5196 12.7071 15.7071C12.5196 15.8946 12.2652 16 12 16C11.7348 16 11.4804 15.8946 11.2929 15.7071C11.1054 15.5196 11 15.2652 11 15V9C11 8.73478 11.1054 8.48043 11.2929 8.29289C11.4804 8.10536 11.7348 8 12 8Z" fill="#666666"/>
                      </svg>
                      <label className="switch">
                        <input
                          type="checkbox"
                          checked={channel.status === "active"}
                          onChange={() => handleChannelToggle(channel.id, channel.status === "active")}
                        />                      
                        <span className="slider round"></span>
                      </label>
                    </div>
                  </div>
                  <div className='bottom-line'></div>
                </li>
              ))}
          </ul>
          <div className="btn-add-project">
              <button onClick={() => handleAddChannel()}>Add Channel</button>
          </div>
        </div>
      )}
    </div>
  );
};
