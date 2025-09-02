// src/services/googleAuth.js
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

export const initializeGoogleAuth = () => {
  return new Promise((resolve) => {
    if (window.google) {
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true,
      });
      resolve(true);
    } else {
      // Charger le script Google si pas encore chargé
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.onload = () => {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleCredentialResponse,
          auto_select: false,
          cancel_on_tap_outside: true,
        });
        resolve(true);
      };
      document.head.appendChild(script);
    }
  });
};

// Callback quand l'utilisateur se connecte
const handleCredentialResponse = (response) => {
  // Cette fonction sera remplacée dynamiquement
  console.log('Credential response:', response);
};

export const signInWithGoogle = () => { // On enlève le paramètre isSignup
  return new Promise((resolve, reject) => {
    const originalCallback = window.google.accounts.id.callback;
    
    window.google.accounts.id.callback = (response) => {
      window.google.accounts.id.callback = originalCallback;
      
      if (response.credential) {
        resolve(response); 
      } else {
        reject(new Error("La réponse de Google ne contient pas de credential."));
      }
    };
    window.google.accounts.id.prompt((notification) => {
      if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
        // Fallback : utiliser la méthode alternative
        window.google.accounts.id.renderButton(
          document.createElement('div'),
          { 
            theme: 'outline', 
            size: 'large',
            type: 'standard',
            text: isSignup ? 'signup_with' : 'signin_with'
          }
        );
        
        // Simuler un clic sur le bouton invisible
        const hiddenButton = document.querySelector('[role="button"]');
        if (hiddenButton) {
          hiddenButton.click();
        } else {
          reject(new Error('Impossible d\'ouvrir la popup Google'));
        }
      }
    });
  });
};

// Fonction utilitaire pour décoder le JWT
const parseJwt = (token) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    throw new Error('Token invalide');
  }
};