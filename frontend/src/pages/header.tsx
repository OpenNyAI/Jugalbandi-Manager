import React from 'react';
import { useLocation } from 'react-router-dom';
import './header.css'

export const Header = () => {
    const location = useLocation();
    return (
        <div className='header'>
            <img src="logo.svg" style={ { width: '200px' } } alt="JB Manager" />
            <h3>{location?.state?.from && location.state.from}</h3>
            <div>&nbsp;</div>
        </div>
    )
}

export default Header;