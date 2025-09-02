// src/components/tabs/JobsTab.jsx
import React, { useState, useEffect } from 'react';
import { jobsService } from '../../services/jobService';
import JobCard from './JobCard'; // Importez le nouveau composant de carte
import '../../style/JobsTab.css'; // Importez le nouveau CSS

const JobsTab = () => {
    const [jobs, setJobs] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadJobs = async () => {
            try {
                const jobsData = await jobsService.getJobs();
                setJobs(jobsData);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        loadJobs();
    }, []);

    const renderContent = () => {
        if (isLoading) {
            return <div className="jobs-loading">Chargement des offres...</div>;
        }

        if (error) {
            return <div className="jobs-error">Erreur : {error}</div>;
        }

        if (jobs.length === 0) {
            return <div className="jobs-loading">Aucune offre d'emploi trouvée pour le moment.</div>;
        }

        return (
            <div className="jobs-grid">
                {jobs.map(job => (
                    <JobCard key={job.id} job={job} />
                ))}
            </div>
        );
    };

    return (
        <div className="tab-content">
            <div className="content-header">
                <h2 className="section-title">Les offres d'emploi</h2>
                <p className="section-subtitle">Découvrez les opportunités et lancez votre entretien.</p>
            </div>
            {renderContent()}
        </div>
    );
};

export default JobsTab;