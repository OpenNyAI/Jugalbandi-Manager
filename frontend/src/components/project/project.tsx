import { Link } from "react-router-dom";
import './project.css'
import moment from 'moment';
import { sendRequest } from '@/api';
import { useState, useEffect } from "react";

interface IProjectProps {
    id: string;
    name: string;
    credits: string;
    status: string;
    channel: string;
    created_at: string;
    modified: string;
    required_credentials: string[];
    showModel: Function;
    project: any;
    credentials: any;
    setDataForModel: Function;
    setModelType: Function;
    refreshBots: Function;
}

function Project(props: IProjectProps) {
    const { refreshBots, id, name, credits, status, channel, created_at, modified, showModel, setDataForModel, required_credentials, credentials } = props;
    const APIHOST = import.meta.env.VITE_SERVER_HOST;
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [channelTypes, setChannelTypes] = useState<string[]>([]);
    const [selectedChannelType, setSelectedChannelType] = useState<string>("");
    const [channelName, setChannelName] = useState('');
    const [url, setUrl] = useState('');
    const [appId, setAppId] = useState('');
    const [key, setKey] = useState('');

    const statusColor = status.toLowerCase() === 'active' ? '#009B39' :
                        status.toLowerCase() === 'configuration pending' ? '#F2BB4F' : '#000';

    const editConfig = () => {
        let config: any = {};
        for (let key of required_credentials || []) {
            const value = credentials && credentials[key] ? credentials[key] : '';
            config[key] = {
                value,
                is_secret: true
            };
        }
        setDataForModel({
            title: `Edit ${name} Settings`,
            inputs: config,
            botId: id,
            modelType: "credentials"
        });
        showModel(true);
    }

    const activateProject = () => {
        let config: any = {
            "phone_number": {
                "value": "",
                "is_secret": false,
                "required": true
            },
            "whatsapp": {
                "value": "",
                "is_secret": true,
                "required": true
            }
        }
        setDataForModel({
            title: `Activate ${name}`,
            inputs: config,
            botId: id,
            modelType: "activate"
        });
        showModel(true);
    }

    const pauseBot = () => {
        if (confirm(`Are you sure want to pause this ${name}?`)) {
            sendRequest({
                url: `${APIHOST}/v1/bot/${id}/deactivate`,
                method: "GET"
            }).then((response: any) => {
                console.log(response);
                refreshBots();
            });
        }
    }

    const deleteBot = () => {
        if (confirm(`Are you sure want to delete this ${name}?`)) {
            sendRequest({
                url: `${APIHOST}/v1/bot/${id}`,
                method: "DELETE"
            }).then((response: any) => {
                console.log(response);
                refreshBots();
            });
        }
    }

    useEffect(() => {
        console.log("useEffect triggered");
        // Fetch channel types on component mount
        sendRequest({
            url: `${APIHOST}/v2/channel/`,
            method: "GET"
        }).then((response: any) => {
            console.log("Response received");
            console.log(response);
            if (response) {
                setChannelTypes(response); // Adjust this according to your API response structure
                console.log("Channel types:", response);
            } else {
                console.log("Response is empty or does not contain data");
            }
        }).catch((error: any) => {
            console.error("Error fetching channel types:", error);
        });
    }, [APIHOST]);

    const handleOpenModal = () => {
        setIsModalOpen(true);

    }

    const handleCloseModal = () => {
        setIsModalOpen(false);
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const body = {
            name: channelName,
            type: selectedChannelType,
            url: url,
            app_id: appId,
            key: key,
            status: "inactive"
        };
        console.log(body);
        // console.log(JSON.stringify(body));


        sendRequest({
            url: `${APIHOST}/v2/bot/${id}/channel`,
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        }).then((response: any) => {
            console.log(response);
            handleCloseModal();
            refreshBots();
        });
    }

    return (
        <div className='project-container'>
            <div className='project'>
                <div className='name'>{name}</div>
                <Link to="/chat" state={{ from: name, bot_id: id }}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M21.6 0H2.4C1.08 0 0.012 1.08 0.012 2.4L0 24L4.8 19.2H21.6C22.92 19.2 24 18.12 24 16.8V2.4C24 1.08 22.92 0 21.6 0ZM18 14.4H6C5.34 14.4 4.8 13.86 4.8 13.2C4.8 12.54 5.34 12 6 12H18C18.66 12 19.2 12.54 19.2 13.2C19.2 13.86 18.66 14.4 18 14.4ZM18 10.8H6C5.34 10.8 4.8 10.26 4.8 9.6C4.8 8.94 5.34 8.4 6 8.4H18C18.66 8.4 19.2 8.94 19.2 9.6C19.2 10.26 18.66 10.8 18 10.8ZM18 7.2H6C5.34 7.2 4.8 6.66 4.8 6C4.8 5.34 5.34 4.8 6 4.8H18C18.66 4.8 19.2 5.34 19.2 6C19.2 6.66 18.66 7.2 18 7.2Z" fill="#B3B3B3" />
                    </svg>
                </Link>
                {/* <Link to="/analytics" state={{ from: name }}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path fillRule="evenodd" clipRule="evenodd" d="M0 4C0 2.93913 0.421427 1.92172 1.17157 1.17157C1.92172 0.421427 2.93913 0 4 0H20C21.0609 0 22.0783 0.421427 22.8284 1.17157C23.5786 1.92172 24 2.93913 24 4V20C24 21.0609 23.5786 22.0783 22.8284 22.8284C22.0783 23.5786 21.0609 24 20 24H4C2.93913 24 1.92172 23.5786 1.17157 22.8284C0.421427 22.0783 0 21.0609 0 20V4ZM13.3333 6.66667C13.3333 6.31305 13.1929 5.97391 12.9428 5.72386C12.6928 5.47381 12.3536 5.33333 12 5.33333C11.6464 5.33333 11.3072 5.47381 11.0572 5.72386C10.8071 5.97391 10.6667 6.31305 10.6667 6.66667V17.3333C10.6667 17.687 10.8071 18.0261 11.0572 18.2761C11.3072 18.5262 11.6464 18.6667 12 18.6667C12.3536 18.6667 12.6928 18.5262 12.9428 18.2761C13.1929 18.0261 13.3333 17.687 13.3333 17.3333V6.66667ZM8 10.6667C8 10.313 7.85952 9.97391 7.60948 9.72386C7.35943 9.47381 7.02029 9.33333 6.66667 9.33333C6.31305 9.33333 5.97391 9.47381 5.72386 9.72386C5.47381 9.97391 5.33333 10.313 5.33333 10.6667V17.3333C5.33333 17.687 5.47381 18.0261 5.72386 18.2761C5.97391 18.5262 6.31305 18.6667 6.66667 18.6667C7.02029 18.6667 7.35943 18.5262 7.60948 18.2761C7.85952 18.0261 8 17.687 8 17.3333V10.6667ZM18.6667 14.6667C18.6667 14.313 18.5262 13.9739 18.2761 13.7239C18.0261 13.4738 17.687 13.3333 17.3333 13.3333C16.9797 13.3333 16.6406 13.4738 16.3905 13.7239C16.1405 13.9739 16 14.313 16 14.6667V17.3333C16 17.687 16.1405 18.0261 16.3905 18.2761C16.6406 18.5262 16.9797 18.6667 17.3333 18.6667C17.687 18.6667 18.0261 18.5262 18.2761 18.2761C18.5262 18.0261 18.6667 17.687 18.6667 17.3333V14.6667Z" fill="#B3B3B3"/>
                    </svg>
                </Link> */}
                <svg onClick={editConfig} className='settings-icon' xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 26 26" fill="none">
                    <path d="M13 8.5C10.4067 8.5 8.30435 10.5147 8.30435 13C8.30435 15.4853 10.4067 17.5 13 17.5C14.4075 17.5 15.6703 16.9066 16.5309 15.9666C17.2561 15.1745 17.6957 14.1365 17.6957 13C17.6957 12.5401 17.6236 12.0962 17.4899 11.6783C16.9007 9.838 15.1134 8.5 13 8.5ZM9.86957 13C9.86957 11.3431 11.2711 10 13 10C14.7289 10 16.1304 11.3431 16.1304 13C16.1304 14.6569 14.7289 16 13 16C11.2711 16 9.86957 14.6569 9.86957 13ZM21.0445 21.3947L19.2419 20.6364C18.7262 20.4197 18.1204 20.4514 17.633 20.7219C17.1457 20.9923 16.8348 21.4692 16.7729 22.0065L16.5561 23.8855C16.5115 24.2729 16.2181 24.5917 15.8231 24.6819C13.9665 25.106 12.0322 25.106 10.1756 24.6819C9.78062 24.5917 9.48727 24.2729 9.44258 23.8855L9.22618 22.0093C9.16262 21.473 8.83778 20.9976 8.3508 20.728C7.86383 20.4585 7.27253 20.4269 6.75853 20.6424L4.95552 21.4009C4.58207 21.558 4.14602 21.4718 3.86754 21.1858C2.57017 19.8536 1.60442 18.2561 1.04301 16.5136C0.922085 16.1383 1.0618 15.7307 1.3912 15.4976L2.9849 14.3703C3.43883 14.05 3.70693 13.5415 3.70693 13.0006C3.70693 12.4597 3.43883 11.9512 2.9843 11.6305L1.3916 10.5051C1.06172 10.272 0.921872 9.86375 1.04322 9.48812C1.60561 7.74728 2.57186 6.15157 3.86927 4.82108C4.14801 4.53522 4.58427 4.44935 4.95766 4.60685L6.75266 5.36398C7.26914 5.58162 7.86292 5.54875 8.35253 5.27409C8.84002 5.00258 9.16456 4.52521 9.22722 3.98787L9.44522 2.11011C9.49075 1.71797 9.79082 1.39697 10.1919 1.31131C11.1113 1.11498 12.0495 1.01065 13.0136 1C13.9545 1.01041 14.8916 1.11478 15.8099 1.31143C16.2108 1.39728 16.5106 1.71817 16.5561 2.11011L16.7742 3.98931C16.873 4.85214 17.6317 5.50566 18.5362 5.50657C18.7793 5.50694 19.0198 5.45832 19.2445 5.36288L21.0398 4.60562C21.4132 4.44812 21.8494 4.53399 22.1282 4.81984C23.4256 6.15034 24.3918 7.74605 24.9542 9.48689C25.0755 9.86227 24.9359 10.2702 24.6064 10.5034L23.0151 11.6297C22.5612 11.9499 22.287 12.4585 22.287 12.9994C22.287 13.5402 22.5612 14.0488 23.0161 14.3697L24.6088 15.4964C24.9384 15.7296 25.0781 16.1376 24.9568 16.513C24.3946 18.2536 23.4289 19.8491 22.1323 21.1799C21.8538 21.4657 21.4178 21.5518 21.0445 21.3947ZM15.3614 21.1965C15.6068 20.4684 16.1189 19.8288 16.8487 19.4238C17.7689 18.9132 18.8994 18.8546 19.8704 19.2626L21.2728 19.8526C22.1732 18.8537 22.8706 17.7013 23.3285 16.4551L22.0882 15.5777L22.0872 15.577C21.2414 14.9799 20.7217 14.0276 20.7217 12.9994C20.7217 11.9718 21.2408 11.0195 22.0858 10.4227L22.0872 10.4217L23.3259 9.54496C22.8679 8.29874 22.1702 7.1463 21.2694 6.14764L19.8788 6.73419L19.8764 6.73521C19.4533 6.91457 18.9971 7.00716 18.5345 7.00657C16.8311 7.00447 15.4048 5.77425 15.2185 4.15459L15.2183 4.15285L15.0489 2.69298C14.3776 2.57322 13.6967 2.50866 13.0136 2.50011C12.3102 2.50885 11.6248 2.57361 10.9524 2.69322L10.7828 4.15446C10.6652 5.16266 10.0567 6.05902 9.14112 6.5698C8.22022 7.08554 7.09864 7.14837 6.12211 6.73688L4.72806 6.14887C3.82729 7.14745 3.12965 8.29977 2.67161 9.54587L3.91319 10.4232C4.76816 11.0268 5.27214 11.9836 5.27214 13.0006C5.27214 14.0172 4.76844 14.9742 3.91378 15.5776L2.67125 16.4565C3.12872 17.7044 3.82626 18.8584 4.72736 19.8587L6.13122 19.2681C7.10168 18.8613 8.21641 18.9214 9.13361 19.4291C10.0511 19.9369 10.6619 20.8319 10.7814 21.84L10.7819 21.8445L10.9508 23.3087C12.3036 23.5638 13.6951 23.5638 15.0479 23.3087L15.2171 21.8417C15.2425 21.6217 15.291 21.4054 15.3614 21.1965Z" fill="#B3B3B3" stroke="#666666"/>
                </svg>
                <div className='credits'>{credits}</div>
                <div className='status' style={{color: statusColor}}>
                    <div>{status}</div>
                    {status.toLowerCase() === 'active' ? 
                        <svg onClick={pauseBot} xmlns="http://www.w3.org/2000/svg" width="19" height="20" viewBox="0 0 19 20" fill="none">
                            <path d="M16.101 0H12.1739C11.6532 0 11.1537 0.210714 10.7855 0.585786C10.4173 0.960859 10.2104 1.46957 10.2104 2V18C10.2104 18.5304 10.4173 19.0391 10.7855 19.4142C11.1537 19.7893 11.6532 20 12.1739 20H16.101C16.6217 20 17.1212 19.7893 17.4894 19.4142C17.8576 19.0391 18.0645 18.5304 18.0645 18V2C18.0645 1.46957 17.8576 0.960859 17.4894 0.585786C17.1212 0.210714 16.6217 0 16.101 0ZM15.7083 17.6H12.5666V2.4H15.7083V17.6ZM5.8906 0H1.96353C1.44277 0 0.94334 0.210714 0.575106 0.585786C0.206872 0.960859 0 1.46957 0 2V18C0 18.5304 0.206872 19.0391 0.575106 19.4142C0.94334 19.7893 1.44277 20 1.96353 20H5.8906C6.41136 20 6.9108 19.7893 7.27903 19.4142C7.64727 19.0391 7.85414 18.5304 7.85414 18V2C7.85414 1.46957 7.64727 0.960859 7.27903 0.585786C6.9108 0.210714 6.41136 0 5.8906 0ZM5.4979 17.6H2.35624V2.4H5.4979V17.6Z" fill="#666666"/>
                        </svg> 
                        : 
                        <svg onClick={activateProject} xmlns="http://www.w3.org/2000/svg" width="23" height="24" viewBox="0 0 23 24" fill="none">
                            <path d="M19.4085 9.35309C19.8888 9.60849 20.2905 9.98976 20.5707 10.456C20.8508 10.9223 20.9988 11.456 20.9988 12C20.9988 12.544 20.8508 13.0777 20.5707 13.544C20.2905 14.0103 19.8888 14.3915 19.4085 14.6469L6.59686 21.6137C4.53392 22.7367 2 21.2767 2 18.9678V5.03322C2 2.72329 4.53392 1.26433 6.59686 2.3853L19.4085 9.35309Z" stroke="#666666" strokeWidth="3"/>
                        </svg>
                    }
                </div>
                <div className='channel'>
                    <button onClick={handleOpenModal}>Add Channel</button>
                </div>
                <div className='added'>{moment(created_at).format("Do MMM YY")}</div>
                <div className='modified'>{modified && moment(modified).format("Do MMM YY")}</div>
                <svg onClick={deleteBot} xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M5 2C5 1.46957 5.21071 0.960859 5.58579 0.585786C5.96086 0.210714 6.46957 0 7 0H13C13.5304 0 14.0391 0.210714 14.4142 0.585786C14.7893 0.960859 15 1.46957 15 2V4H19C19.2652 4 19.5196 4.10536 19.7071 4.29289C19.8946 4.48043 20 4.73478 20 5C20 5.26522 19.8946 5.51957 19.7071 5.70711C19.5196 5.89464 19.2652 6 19 6H17.931L17.064 18.142C17.0281 18.6466 16.8023 19.1188 16.4321 19.4636C16.0619 19.8083 15.5749 20 15.069 20H4.93C4.42414 20 3.93707 19.8083 3.56688 19.4636C3.1967 19.1188 2.97092 18.6466 2.935 18.142L2.07 6H1C0.734784 6 0.48043 5.89464 0.292893 5.70711C0.105357 5.51957 0 5.26522 0 5C0 4.73478 0.105357 4.48043 0.292893 4.29289C0.48043 4.10536 0.734784 4 1 4H5V2ZM7 4H13V2H7V4ZM4.074 6L4.931 18H15.07L15.927 6H4.074ZM8 8C8.26522 8 8.51957 8.10536 8.70711 8.29289C8.89464 8.48043 9 8.73478 9 9V15C9 15.2652 8.89464 15.5196 8.70711 15.7071C8.51957 15.8946 8.26522 16 8 16C7.73478 16 7.48043 15.8946 7.29289 15.7071C7.10536 15.5196 7 15.2652 7 15V9C7 8.73478 7.10536 8.48043 7.29289 8.29289C7.48043 8.10536 7.73478 8 8 8ZM12 8C12.2652 8 12.5196 8.10536 12.7071 8.29289C12.8946 8.48043 13 8.73478 13 9V15C13 15.2652 12.8946 15.5196 12.7071 15.7071C12.5196 15.8946 12.2652 16 12 16C11.7348 16 11.4804 15.8946 11.2929 15.7071C11.1054 15.5196 11 15.2652 11 15V9C11 8.73478 11.1054 8.48043 11.2929 8.29289C11.4804 8.10536 11.7348 8 12 8Z" fill="#666666"/>
                </svg>
            </div>

            {isModalOpen && (
                <div className="modal">
                    <div className="modal-content">
                        <span className="close" onClick={handleCloseModal}>&times;</span>
                        <form onSubmit={handleSubmit}>
                            <label>
                                Channel Name:
                                <input type="text" value={channelName} onChange={(e) => setChannelName(e.target.value)} />
                            </label>
                            <label>
                                Channel Type:
                                <select value={selectedChannelType} onChange={(e) => setSelectedChannelType(e.target.value)}>
                                    <option value="">Select a channel type</option>
                                    {channelTypes.map((type: string) => (
                                        <option key={type} value={type}>{type}</option>
                                    ))}
                                </select>
                            </label>
                            <label>
                                URL:
                                <input type="text" value={url} onChange={(e) => setUrl(e.target.value)} />
                            </label>
                            <label>
                                App ID:
                                <input type="text" value={appId} onChange={(e) => setAppId(e.target.value)} />
                            </label>
                            <label>
                                Key:
                                <input type="text" value={key} onChange={(e) => setKey(e.target.value)} />
                            </label>
                            <button type="submit">Submit</button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Project;
