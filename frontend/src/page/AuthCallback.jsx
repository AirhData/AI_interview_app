// src/page/AuthCallback.jsx
import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../style/AuthCallback.css';

const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('Finalisation de votre connexion...');

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Récupérer les paramètres de l'URL
        const urlParams = new URLSearchParams(location.search);
        const token = urlParams.get('token');
        const userParam = urlParams.get('user');
        const error = urlParams.get('error');

        console.log('Auth callback params:', { token: !!token, user: !!userParam, error });

        if (error) {
          throw new Error(`Erreur d'authentification: ${error}`);
        }

        if (token && userParam) {
          try {
            const user = JSON.parse(decodeURIComponent(userParam));
            
            // Stocker les données dans localStorage
            localStorage.setItem('authToken', token);
            localStorage.setItem('user', JSON.stringify(user));
            
            setStatus('success');
            setMessage('Connexion réussie ! Redirection...');
            
            // Redirection après un court délai
            setTimeout(() => {
              navigate('/home', { replace: true });
            }, 1500);
            
          } catch (parseError) {
            console.error('Erreur parsing user data:', parseError);
            throw new Error('Données utilisateur invalides');
          }
        } else {
          throw new Error('Token ou données utilisateur manquants');
        }
      } catch (error) {
        console.error('Erreur dans AuthCallback:', error);
        setStatus('error');
        setMessage(`Erreur lors de la connexion: ${error.message}`);
        
        // Redirection vers la page d'accueil après erreur
        setTimeout(() => {
          navigate('/?error=auth_failed', { replace: true });
        }, 3000);
      }
    };

    // Petit délai pour l'UX
    const timer = setTimeout(handleAuthCallback, 800);
    return () => clearTimeout(timer);
  }, [navigate, location]);

  const getIcon = () => {
    switch (status) {
      case 'success':
        return <i className="fas fa-check-circle"></i>;
      case 'error':
        return <i className="fas fa-times-circle"></i>;
      default:
        return <i className="fas fa-spinner fa-spin"></i>;
    }
  };

  return (
    <div className="auth-callback-container">
      <div className="auth-callback-card">
        <div className={`auth-callback-icon ${status}`}>
          {getIcon()}
        </div>
        
        <h2 className="auth-callback-title">
          {status === 'success' ? 'Connexion réussie !' : 
           status === 'error' ? 'Erreur de connexion' : 
           'Connexion en cours...'}
        </h2>
        
        <p className="auth-callback-message">
          {message}
        </p>

        {status === 'error' && (
          <button
            className="auth-callback-button"
            onClick={() => navigate('/', { replace: true })}
          >
            Retour à l'accueil
          </button>
        )}
      </div>
    </div>
  );
};

export default AuthCallback;