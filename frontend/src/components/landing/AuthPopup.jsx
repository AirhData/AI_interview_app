import React, { useEffect } from 'react';
import '../../style/AuthPopup.css';

const AuthPopup = ({ isOpen, onClose, onGoogleLogin, onGoogleSignup }) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);
  if (!isOpen) return null;
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="auth-popup-overlay" onClick={handleOverlayClick}>
      <div className="auth-popup-container">
        <div className="auth-popup-header">
          <h2 className="auth-popup-title">Rejoignez AIrh</h2>
          <button className="auth-popup-close" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        </div>
        <div className="auth-popup-body">
          <p className="auth-popup-description">
            accéder à toutes nos fonctionnalités et a votre espace personnel
          </p>
          <button className="auth-google-btn login-btn" onClick={onGoogleLogin}>
            <div className="google-icon">
              <svg width="20" height="20" viewBox="0 0 18 18">
                <path fill="#4285F4" d="M16.51 8H8.98v3h4.3c-.18 1-.74 1.48-1.6 2.04v2.01h2.6a7.8 7.8 0 0 0 2.38-5.88c0-.57-.05-.66-.15-1.18Z"/>
                <path fill="#34A853" d="M8.98 16c2.16 0 3.97-.72 5.3-1.94l-2.6-2.04a4.8 4.8 0 0 1-7.18-2.53H1.83v2.07A8 8 0 0 0 8.98 16Z"/>
                <path fill="#FBBC05" d="M4.5 9.49a4.8 4.8 0 0 1 0-3.07V4.35H1.83a8 8 0 0 0 0 7.17L4.5 9.49Z"/>
                <path fill="#EA4335" d="M8.98 4.07c1.17 0 2.23.4 3.06 1.2l2.3-2.3A8 8 0 0 0 1.83 4.35L4.5 6.42a4.8 4.8 0 0 1 4.48-2.35Z"/>
              </svg>
            </div>
            Se connecter avec Google
          </button>
        </div>

      </div>
    </div>
  );
};

export default AuthPopup;