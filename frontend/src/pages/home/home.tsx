import * as React from 'react';
import './home.css'
import InfoCard from '@/components/info-card/info-card';
import data from '@/mockData.json';
import Project from '@/components/project/project';
import { sendRequest } from '@/api';
import SettingsModal from '@/components/settings-model';
import { useAuth } from '@/context/AuthContext';
const APIHOST = import.meta.env.VITE_SERVER_HOST;

interface props {

}

export const Home:React.FunctionComponent = (props:props) => {
    const { getToken, getAuthMethodType, getUser } = useAuth();
    const [token, setToken] = React.useState('');
    const [refreshBots, incrementrefreshBots] = React.useState(0);
    const [projects, setProjects] = React.useState([]);
    const [loading, setLoading] = React.useState(false);
    const [isSettingsModelOpen, showModel] = React.useState(false);
    const [modelData, setDataForModel] = React.useState<any>();
    const [jb_secret, setJBSecret] = React.useState('');
    React.useEffect(() => {
       getToken().then((token:string) => {
            setToken(token);
        });
    },[])
    
    React.useEffect(() => {
        if (!token) return;
        setLoading(true);
        sendRequest({
            url: `${APIHOST}/bots`,
            accessToken: token,
            loginMethod: getAuthMethodType()
         }).then((response:any) => {
            setProjects(response);
            setLoading(false);
        });
    },[refreshBots, token])

    const closeModal = () => {
        showModel(false);
        incrementrefreshBots(refreshBots + 1);
    }

    const installBot = () => {
        showModel(true);
        setDataForModel({
            inputs: {
                name: {
                    value: '',
                    type: 'string',
                    required: true
                },
                dsl: {
                    value: '',
                    type: 'text'
                },
                code: {
                    value: '',
                    type: 'text',
                    required: true
                },
                requirements: {
                    value: '',
                    type: 'text'
                },
                index_urls: {
                    value: '',
                    type: 'list',
                    placeholder: "Use comma to separate multiple URLs"

                },
                version: {
                    value: '',
                    type: 'string'
                },
                required_credentials: {
                    value: '',
                    type: 'list',
                    placeholder: 'Use comma to seperate for multiple credentials'
                }

            },
            modelType: 'install'
        });
    }
  const getJBSecret = async () => {
    const user = await getUser();
    if (user?.jb_secret) {
        navigator.clipboard.writeText(user?.jb_secret);
        alert("Secret Copied")
    } else {
        alert("No JB Secret Found")
    }
  }
    
  return (
    <div className='home'>
        <SettingsModal isOpen={isSettingsModelOpen} inputs={modelData?.inputs} onClose={closeModal} modelType={modelData?.modelType} botId={modelData?.botId} />
        <div className='top-section'>
            <div className='cards-container'>
                <InfoCard title='Guide' className="guide" />
                <InfoCard title='Blogs' className="blogs" />
                <InfoCard title='Community' className="community" />
                <InfoCard title='FAQ' className="faq" />
            </div>
            <div className='user-info'>
                <div className='type'>
                    <div>
                        Installation URL:
                        <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 17 17" fill="none">
                            <path d="M7.65 4.25H9.35V5.95H7.65V4.25ZM7.65 7.65H9.35V12.75H7.65V7.65ZM8.5 0C3.808 0 0 3.808 0 8.5C0 13.192 3.808 17 8.5 17C13.192 17 17 13.192 17 8.5C17 3.808 13.192 0 8.5 0ZM8.5 15.3C4.7515 15.3 1.7 12.2485 1.7 8.5C1.7 4.7515 4.7515 1.7 8.5 1.7C12.2485 1.7 15.3 4.7515 15.3 8.5C15.3 12.2485 12.2485 15.3 8.5 15.3Z" fill="black"/>
                        </svg>
                    </div>
                    <div>
                        JB Manager Secret:
                        <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 17 17" fill="none">
                            <path d="M7.65 4.25H9.35V5.95H7.65V4.25ZM7.65 7.65H9.35V12.75H7.65V7.65ZM8.5 0C3.808 0 0 3.808 0 8.5C0 13.192 3.808 17 8.5 17C13.192 17 17 13.192 17 8.5C17 3.808 13.192 0 8.5 0ZM8.5 15.3C4.7515 15.3 1.7 12.2485 1.7 8.5C1.7 4.7515 4.7515 1.7 8.5 1.7C12.2485 1.7 15.3 4.7515 15.3 8.5C15.3 12.2485 12.2485 15.3 8.5 15.3Z" fill="black"/>
                        </svg>
                    </div>
                </div>
                <div className='value'>
                    <div onClick={() => { navigator.clipboard.writeText("https://bandhujbstorage.z29.web.core.windows.net/"); alert("Installation URL copied") }}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
                            <path d="M11.75 2C9.95507 2 8.5 3.45508 8.5 5.25V23.25C8.5 25.0449 9.95507 26.5 11.75 26.5H23.75C25.5449 26.5 27 25.0449 27 23.25V5.25C27 3.45507 25.5449 2 23.75 2H11.75ZM10.5 5.25C10.5 4.55964 11.0596 4 11.75 4H23.75C24.4404 4 25 4.55964 25 5.25V23.25C25 23.9404 24.4404 24.5 23.75 24.5H11.75C11.0596 24.5 10.5 23.9404 10.5 23.25V5.25ZM7 5.74902C5.82552 6.2388 5 7.39797 5 8.74994V23.4999C5 27.0898 7.91015 29.9999 11.5 29.9999H20.25C21.6021 29.9999 22.7613 29.1743 23.2511 27.9996H20.2786C20.2691 27.9998 20.2596 27.9999 20.25 27.9999H11.5C9.01472 27.9999 7 25.9852 7 23.4999V5.74902Z" fill="#8B8B8B"/>
                        </svg>
                        {import.meta.env.VITE_SERVER_HOST+"/install"}
                    </div>
                    <div>
                        <svg onClick={getJBSecret} xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none">
                            <path d="M11.75 2C9.95507 2 8.5 3.45508 8.5 5.25V23.25C8.5 25.0449 9.95507 26.5 11.75 26.5H23.75C25.5449 26.5 27 25.0449 27 23.25V5.25C27 3.45507 25.5449 2 23.75 2H11.75ZM10.5 5.25C10.5 4.55964 11.0596 4 11.75 4H23.75C24.4404 4 25 4.55964 25 5.25V23.25C25 23.9404 24.4404 24.5 23.75 24.5H11.75C11.0596 24.5 10.5 23.9404 10.5 23.25V5.25ZM7 5.74902C5.82552 6.2388 5 7.39797 5 8.74994V23.4999C5 27.0898 7.91015 29.9999 11.5 29.9999H20.25C21.6021 29.9999 22.7613 29.1743 23.2511 27.9996H20.2786C20.2691 27.9998 20.2596 27.9999 20.25 27.9999H11.5C9.01472 27.9999 7 25.9852 7 23.4999V5.74902Z" fill="#8B8B8B"/>
                        </svg>
                        ***************************
                    </div>
                </div>
            </div>
        </div>
        <div className='separator'></div>
        <div className='projects-container'>
            <div className="title-container">
                <div className='title'>Connected Projects:</div>
                <button onClick={installBot}>Install New Bot</button>
            </div>
            <div className='columns'>
                <div className='credits'>Credits</div>
                <div className='status'>Status</div>
                <div className='added'>Added</div>
                <div className='modified'>Modifed</div>
            </div>
            {projects && projects.map((project:object, index) => <Project refreshBots={() => { incrementrefreshBots(refreshBots+1)  }} setDataForModel={setDataForModel} showModel={showModel} {...project} key={index} />)}
        </div>
    </div>
    );
}

export default Home;