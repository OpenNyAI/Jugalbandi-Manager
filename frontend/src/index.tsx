import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';
import { useAuth, AuthProvider } from './context/AuthContext';
import { BrowserRouter } from "react-router-dom";
import Router from './router';

const App = () => {
  const { isAuthenticated, logIn, logOut } = useAuth();
  return (
    <div className='App'>
      {isAuthenticated ? 
        <BrowserRouter>
          <Router />
        </BrowserRouter>
        :       
         <div className="login-page">
            <img src="logo-big.svg" alt="logo" />
            <button type='button' onClick={() => logIn('MS')}>
              Continue with MS
            </button>
            <button type='button' onClick={() => logIn('GOOGLE')}>
              Continue with Google
            </button>
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
