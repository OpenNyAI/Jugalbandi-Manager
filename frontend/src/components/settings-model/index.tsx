import React, { useState, useEffect } from 'react';
import './settings-model.css';
import { sendRequest } from '@/api';
import { fetchSecret } from '@/pages/home/home';
import { channel } from 'diagnostics_channel';

interface InputConfig {
  value: string | number | boolean;
  is_secret?: boolean;
  type: 'string' | 'number' | 'boolean' | 'list' | 'text'; 
  placeholder?: string;
  required: boolean;
  options?: string[]; 
}

interface Props {
  title?: string;
  isOpen: boolean;
  onClose: () => void;
  inputs: Record<string, InputConfig>;
  bot_id: string;
  onSave: (inputs: Record<string, InputConfig>) => void;
  modelType: string;
  botId?: string;
  channelID?: string;
}

const SettingsModal: React.FC<Props> = ({ botId, isOpen, onClose, inputs, modelType, title, channelID=null }) => {
  const [inputElements, setInputElements] = useState<Record<string, InputConfig>>({});
  const APIHOST = import.meta.env.VITE_SERVER_HOST;

  useEffect(() => {
    const initialInputs = { ...inputs }; // Create a copy to avoid modifying props directly

    // Auto-populate url based on initial type value
    if (initialInputs.type && initialInputs.url) { // Check if both fields exist
      if (initialInputs.type.value === "telegram") {
        initialInputs.url.value = "https://api.telegram.org/";
      }
      // else { ... handle other cases or reset url } //  (Optional)
    }

    setInputElements(initialInputs);
  }, [inputs]);

  const updateValue = (key: string, newValue: string | number | boolean) => {
    const updatedInputs = {
      ...inputElements,
      [key]: {
        ...inputElements[key],
        value: newValue,
      },
    };

    if (key === "type") {
      if (newValue === "telegram") {
        updatedInputs["url"] = {
          ...updatedInputs["url"], 
          value: "https://api.telegram.org/",
        };
      } else {
        updatedInputs["url"] = {
          ...updatedInputs["url"], 
          value: "",
        };
      }
    }


    setInputElements(updatedInputs);
  };


  const getInputType = (inputConfig: InputConfig): string => {
    if (inputConfig.is_secret) return 'password';
    return inputConfig.type === 'number' ? 'number' : 'text'; // Expand as needed
  };

  const handleSubmit = async () => {
    let data:any = {};
    let apiEndpoint = '';
    let accessToken = null;
    if (modelType === 'credentials') {
        apiEndpoint = `${APIHOST}/v1/bot/${botId}/configure`;
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
        apiEndpoint = `${APIHOST}/v1/bot/${botId}/activate`;
        if (inputElements['phone_number'].required === true && !inputElements['phone_number'].value.toString().trim()) {
            alert('Phone number is required');
            return;
        }
        if (inputElements['whatsapp'].required === true && !inputElements['whatsapp'].value.toString().trim()) {
            alert('Whatsapp Key is required');
            return;
        }
        data['phone_number'] = inputElements['phone_number'].value;
        data['channels'] = {};
        data['channels']['whatsapp'] = inputElements['whatsapp'].value;
    } else if (modelType === 'install') {
        apiEndpoint = `${APIHOST}/v1/bot/install`;
        try {
          accessToken = await fetchSecret();
      } catch (error) {
          console.error("Failed to fetch the access token:", error);
          alert("Failed to fetch the access token");
          return;
      }
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
    else if(modelType === 'channelInstall'){
      apiEndpoint = `${APIHOST}/v2/bot/${botId}/channel`;
        try {
          accessToken = await fetchSecret();
      } catch (error) {
          console.error("Failed to fetch the access token:", error);
          alert("Failed to fetch the access token");
          return;
      }
        for (let key in inputElements) {
          if (inputElements[key].required === true && !inputElements[key].value.toString().trim()) {
            alert(`${key} is required`);
            return;
          }
          if (inputElements[key].type === 'list') {
            data[key] = inputElements[key].value.toString();
            continue;
          }
          data[key] = inputElements[key].value;
        }
    }
    else if(modelType === 'channelUpdate'){
      apiEndpoint = `${APIHOST}/v2/channel/${channelID}`;
        try {
          accessToken = await fetchSecret();
      } catch (error) {
          console.error("Failed to fetch the access token:", error);
          alert("Failed to fetch the access token");
          return;
      }
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
        accessToken: accessToken,
        body: JSON.stringify(data ),
        headers: {
            'Content-Type': 'application/json',
        }
      })
        onClose();
    } catch (error: any) {
        alert(`Error from server "${error?.body?.detail}". Please try again.`)
        console.error('Error saving settings:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={onClose} />
      <div className="modal-container">
        <div className="modal-header">
          <h2>{title || 'Settings'}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {Object.keys(inputElements).map((key) => (
            <div className="input-wrapper" key={key}>
              <label>{key}{inputElements[key]?.required ? ' *' : ''}</label>
              {inputElements[key].type === 'list' && inputElements[key].options ? (
                <select
                  value={inputElements[key].value.toString()}
                  onChange={e => updateValue(key, e.target.value)}
                >
                  {inputElements[key].options.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              ) : inputElements[key].type === 'text' ? (
                <textarea
                  className="text-area"
                  value={inputElements[key].value.toString()}
                  placeholder={inputElements[key].placeholder || ''}
                  onChange={e => updateValue(key, e.target.value)}
                  rows={5}
                />
              ) : (
                <input
                  type={getInputType(inputElements[key])}
                  value={inputElements[key].value.toString()}
                  placeholder={inputElements[key].placeholder || ''}
                  onChange={e => updateValue(key, e.target.type === 'number' ? Number(e.target.value) : e.target.value)}
                />
              )}
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
