const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const getAuthHeaders = () => {
    const token = localStorage.getItem('authToken'); 
    
    if (!token) {
        throw new Error("Utilisateur non authentifié.");
    }
    
    return {
        'Authorization': `Bearer ${token}`
    };
};

export const jobsService = {
    getJobs: async () => {
        const response = await fetch(`${API_BASE_URL}/jobs/`, { 
            headers: getAuthHeaders() 
        });
        
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération des offres d'emploi.");
        }
        
        return response.json();
    },
};