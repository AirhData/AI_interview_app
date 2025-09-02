// src/services/resumeService.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Note: Pour les actions authentifiées, vous devrez passer le token.
// Cette fonction est un exemple de comment le faire.
const getAuthHeaders = () => {
    // Supposons que votre token est stocké dans le localStorage après la connexion
    const user = JSON.parse(localStorage.getItem('user'));
    const token = user?.access_token; // Ajustez selon la structure de votre objet user
    if (!token) {
        throw new Error("Utilisateur non authentifié.");
    }
    return {
        'Authorization': `Bearer ${token}`
    };
};

export const resumeService = {
    // Récupérer les données du CV analysé
    getResumeData: async () => {
        const response = await fetch(`${API_BASE_URL}/resume/data`, { // Adaptez l'URL à votre route backend
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            if (response.status === 404) return null; // Pas de CV trouvé, ce n'est pas une erreur
            throw new Error('Erreur lors de la récupération des données du CV.');
        }
        return response.json();
    },

    // Télécharger et analyser un nouveau CV
    uploadResume: async (file) => {
        const formData = new FormData();
        formData.append('resume', file);

        const response = await fetch(`${API_BASE_URL}/resume/upload`, { // Adaptez l'URL à votre route backend
            method: 'POST',
            headers: getAuthHeaders(),
            body: formData,
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erreur lors du téléchargement du CV.');
        }
        return response.json();
    },

    deleteResume: async () => {
        const response = await fetch(`${API_BASE_URL}/resume/delete`, { // Adaptez l'URL à votre route backend
            method: 'POST', // ou 'DELETE' selon votre API
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error('La suppression du CV a échoué.');
        }
        return response.json();
    }
};