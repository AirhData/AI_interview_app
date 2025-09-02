// src/services/authService.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const authService = {
  // Initialisation
  initialize: async () => {
    console.log('Auth service initialisé');
  },

  // Connexion avec Google - Redirige vers le backend
  loginWithGoogle: () => {
    const authUrl = `${API_BASE_URL}/auth/oauth/google`;
    console.log('🔄 Redirection vers:', authUrl);
    window.location.href = authUrl;
  },

  // Inscription avec Google - Même processus
  signupWithGoogle: () => {
    const authUrl = `${API_BASE_URL}/auth/oauth/google`;
    console.log('🔄 Redirection vers:', authUrl);
    window.location.href = authUrl;
  },

  // Méthode unifiée pour connexion/inscription automatique
  authenticateWithGoogle: () => {
    const authUrl = `${API_BASE_URL}/auth/oauth/google`;
    console.log('🔄 Redirection vers:', authUrl);
    window.location.href = authUrl;
  },

  // Vérifier si l'utilisateur est connecté
  isAuthenticated: () => {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('user');
    return !!(token && user);
  },

  // Récupérer le token
  getToken: () => {
    return localStorage.getItem('authToken');
  },

  // Récupérer les informations de l'utilisateur actuel
  getCurrentUser: async () => {
    try {
      const localUser = localStorage.getItem('user');
      if (localUser) {
        return JSON.parse(localUser);
      }
      return null;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'utilisateur:', error);
      return null;
    }
  },

  // Déconnexion
  logout: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    window.location.href = '/';
  },

  // Valider un token avec le backend
  validateToken: async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });
      
      if (!response.ok) {
        throw new Error('Token validation failed');
      }
      
      const data = await response.json();
      return data.valid ? data.user : null;
    } catch (error) {
      console.error('Erreur validation token:', error);
      return null;
    }
  },

  // Gestion du callback d'authentification
  handleAuthCallback: (urlParams) => {
    const token = urlParams.get('token');
    const userData = urlParams.get('user');
    
    if (token && userData) {
      try {
        const user = JSON.parse(decodeURIComponent(userData));
        localStorage.setItem('authToken', token);
        localStorage.setItem('user', JSON.stringify(user));
        return true;
      } catch (error) {
        console.error('Erreur parsing user data:', error);
        return false;
      }
    }
    return false;
  }
};