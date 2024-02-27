import './App.css';
import { BrowserRouter } from "react-router-dom";
import Router from './router';
import React from 'react';

function App() {
  return (
    <div className='App'>
      <BrowserRouter>
        <Router />
      </BrowserRouter>
    </div>
  );
}

export default App;