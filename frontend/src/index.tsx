import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';
import { useAuth, AuthProvider } from './context/AuthContext';
import { BrowserRouter } from "react-router-dom";
import Router from './router';

const App = () => {
  const { isAuthenticated, logIn, logOut, isLoading } = useAuth();
  const queryParams = new URLSearchParams(window.location.search);
  React.useEffect(() => {
    if (queryParams.get('code')) {
      logIn('GITHUB', queryParams.get('code') as string);
    }
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }
  return (
    <div className='App'>
      {isAuthenticated ? 
        <BrowserRouter>
          <Router />
        </BrowserRouter>
        :       
         <div className="login-page">
            <img src="logo-big.svg" alt="logo" />
            {import.meta.env.VITE_MS_CLIENT_ID && 
              <button type='button' onClick={() => logIn('MS')}>
                Continue with MS
              </button>
            }
            {import.meta.env.VITE_GOOGLE_CLIENT_ID && 
              <button type='button' onClick={() => logIn('GOOGLE')}>
                Continue with Google
              </button>
            }
            {import.meta.env.VITE_GITHUB_CLIENT_ID &&
              <button type='button' onClick={() => logIn('GITHUB')}>
                Continue with GitHub
              </button>
            }
         </div>
      }
    </div>
  );
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
