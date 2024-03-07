import React, { useState, useEffect } from 'react';
import './settings-model.css';
import { sendRequest } from '@/api';
import { useAuth } from '@/context/AuthContext';

interface InputConfig {
  value: string | number | boolean;
  is_secret?: boolean;
  type: 'string' | 'number' | 'boolean' | 'list' | 'text';
  placeholder?: string;
  required: boolean;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  inputs: Record<string, InputConfig>;
  bot_id: string;
  onSave: (inputs: Record<string, InputConfig>) => void;
  modelType: string;
  botId?: string;
}

const SettingsModal: React.FC<Props> = ({ botId, isOpen, onClose, inputs, modelType }) => {
  const [inputElements, setInputElements] = useState<Record<string, InputConfig>>({});
  const { getToken, getAuthMethodType, logOut } = useAuth();
  const [token, setToken] = useState('');
  const APIHOST = import.meta.env.VITE_SERVER_HOST;

  useEffect(() => {
    setInputElements(inputs || {});
  }, [inputs]);

  useEffect(() => {
    getToken().then((token: string) => {
      setToken(token);
    });
  }, []);

  const updateValue = (key: string, newValue: string | number | boolean) => {
    setInputElements(prevState => ({
      ...prevState,
      [key]: {
        ...prevState[key],
        value: newValue,
      },
    }));
  };

  const getInputType = (inputConfig: InputConfig): string => {
    if (inputConfig.is_secret) return 'password';
    return inputConfig.type === 'number' ? 'number' : 'text'; // Expand as needed
  };

  const handleSubmit = async () => {
    let data:any = {};
    let apiEndpoint = '';
    if (modelType === 'credentials') {
        apiEndpoint = `${APIHOST}/bot/${botId}/configure`;
        let credentials:any = {};
        for (let key in inputElements) {
          if (inputElements[key].required === true && !inputElements[key].value.toString().trim()) {
            alert(`${key} is required`);
            return;
          }
          credentials[key] = inputElements[key].value;
        }
        data['credentials'] = { ...credentials };
    } else if (modelType === 'activate') {
        apiEndpoint = `${APIHOST}/bot/${botId}/activate`;
        data['phone_number'] = inputElements['phone_number'].value;
    } else if (modelType === 'install') {
        apiEndpoint = `${APIHOST}/bot/install`;
        for (let key in inputElements) {
          if (inputElements[key].required === true && !inputElements[key].value.toString().trim()) {
            alert(`${key} is required`);
            return;
          }
          if (inputElements[key].type === 'list') {
            data[key] = inputElements[key].value.toString().split(',').map((item: string) => item.trim());
            continue;
          }
          data[key] = inputElements[key].value;
        }
    }
    try {
      await sendRequest({
        url: apiEndpoint,
        method: 'POST',
        body: JSON.stringify(data),
        accessToken: token,
        loginMethod: getAuthMethodType(),
        onUnauthorized: logOut,
        headers: {
            'Content-Type': 'application/json',
        }
      })
        onClose();
    } catch (error) {
        alert("Error from server. Please try again.")
        console.error('Error saving settings:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={onClose} />
      <div className="modal-container">
        <div className="modal-header">
          <h2>Settings</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {Object.keys(inputElements).map((key) => (
            <div className="input-wrapper" key={key}>
              <label>{key}{inputElements[key]?.required === true? ' *' : ''}</label>
              {inputElements[key].type === 'text' ?
                <textarea
                    className='text-area'
                    value={inputElements[key].value.toString()}
                    placeholder={inputElements[key].placeholder || ''}
                    onChange={e => updateValue(key, e.target.value)}
                    rows={5}
                />
              :
              <input
              type={getInputType(inputElements[key])}
                value={inputElements[key].value.toString()}
                placeholder={inputElements[key].placeholder || ''}
                onChange={e => updateValue(key, e.target.type === 'number' ? Number(e.target.value) : e.target.value)}
              />}
            </div>
          ))}
        </div>
        <div className="modal-footer">
          <button className="save-button" onClick={handleSubmit}>Save</button>
          <button className="cancel-button" onClick={onClose}>Cancel</button>
        </div>
      </div>
    </>
  );
};

export default SettingsModal;
