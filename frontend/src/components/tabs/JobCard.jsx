// src/components/tabs/JobCard.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';

const JobCard = ({ job }) => {
    const navigate = useNavigate();

    const handleStartInterview = () => {
        // Redirige vers l'onglet interview en passant l'ID de l'offre
        // Vous devrez adapter cette logique si vous utilisez un autre système de navigation
        navigate(`/home?section=interview&jobId=${job.id}`);
    };

    return (
        <div className="job-card">
            <h3 className="job-title">{job.poste}</h3>
            <div className="job-info">
                <div className="job-info-item">
                    <i className="fas fa-building"></i>
                    <span>{job.entreprise}</span>
                </div>
                <div className="job-info-item">
                    <i className="fas fa-map-marker-alt"></i>
                    <span>{job.ville}</span>
                </div>
                <div className="job-info-item">
                    <i className="fas fa-file-contract"></i>
                    <span>{job.contrat}</span>
                </div>
                <div className="job-info-item">
                    <i className="fas fa-calendar-alt"></i>
                    <span>Publié le {job.publication}</span>
                </div>
            </div>
            <div className="job-actions">
                <a href={job.lien} target="_blank" rel="noopener noreferrer" className="job-btn view-offer">
                    Voir l'offre
                </a>
                <button onClick={handleStartInterview} className="job-btn start-interview">
                    Entretien
                </button>
            </div>
        </div>
    );
};

export default JobCard;