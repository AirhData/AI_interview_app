import React, { useEffect } from 'react';

const WelcomeAlert = ({ userName, onClose }) => {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, 2000);
        return () => clearTimeout(timer);
    }, [onClose]);
    return (
        <div className="welcome-alert">
            <div className="alert-icon">
                <i className="fas fa-info-circle"></i>
            </div>
            <div className="alert-content">
                <span>Heureux de vous revoir, {userName} !</span>
                <button className="alert-close" onClick={onClose}>
                    <i className="fas fa-times"></i>
                </button>
            </div>
        </div>
    );
};
export default WelcomeAlert;
