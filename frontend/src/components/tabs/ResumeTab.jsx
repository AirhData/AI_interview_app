import React, { useState, useEffect, useCallback, useRef } from 'react';
import { resumeService } from '../../services/resumeService';
import '../../style/ResumeTab.css'; // Importez le nouveau CSS

const CvDataDisplay = ({ cvData }) => (
    <div>
        {/* Informations Personnelles */}
        <div className="cv-section">
            <div className="cv-section-header">Informations Personnelles</div>
            <div className="cv-section-body">
                <p><strong>Nom:</strong> {cvData.informations_personnelles?.nom || 'N/A'}</p>
                <p><strong>Email:</strong> {cvData.informations_personnelles?.email || 'N/A'}</p>
                <p><strong>Téléphone:</strong> {cvData.informations_personnelles?.numero_de_telephone || 'N/A'}</p>
                <p><strong>Localisation:</strong> {cvData.informations_personnelles?.localisation || 'N/A'}</p>
            </div>
        </div>

        {/* Compétences */}
        <div className="cv-section">
            <div className="cv-section-header">Compétences</div>
            <div className="cv-section-body">
                <h6>Compétences Techniques</h6>
                <div className="skills-container">
                    {cvData.compétences?.hard_skills?.map(skill => <span key={skill} className="skill-badge hard">{skill}</span>) || <small>Aucune</small>}
                </div>
                <h6 style={{marginTop: '1rem'}}>Compétences Comportementales</h6>
                <div className="skills-container">
                    {cvData.compétences?.soft_skills?.map(skill => <span key={skill} className="skill-badge soft">{skill}</span>) || <small>Aucune</small>}
                </div>
            </div>
        </div>
        {/* Ajoutez d'autres sections comme l'expérience et la formation sur le même modèle */}
    </div>
);


const ResumeTab = () => {
    const [cvData, setCvData] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isUploading, setIsUploading] = useState(false);
    const [statusMessage, setStatusMessage] = useState({ text: '', type: '' });
    const [isDragOver, setIsDragOver] = useState(false);
    const fileInputRef = useRef(null);

    const fetchCvData = useCallback(async () => {
        setIsLoading(true);
        try {
            const data = await resumeService.getResumeData();
            setCvData(data);
        } catch (error) {
            setStatusMessage({ text: 'Erreur de chargement du CV.', type: 'error' });
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchCvData();
    }, [fetchCvData]);

    const handleFileSelect = (file) => {
        if (file && file.type === 'application/pdf') {
            setSelectedFile(file);
            setStatusMessage({ text: `Fichier prêt : ${file.name}`, type: 'success' });
        } else {
            setSelectedFile(null);
            setStatusMessage({ text: 'Erreur : Veuillez sélectionner un fichier PDF.', type: 'error' });
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) return;
        setIsUploading(true);
        setStatusMessage({ text: 'Analyse de votre CV en cours...', type: 'info' });
        try {
            await resumeService.uploadResume(selectedFile);
            setStatusMessage({ text: 'Analyse terminée avec succès !', type: 'success' });
            setSelectedFile(null);
            fetchCvData(); // Recharger les données
        } catch (error) {
            setStatusMessage({ text: error.message, type: 'error' });
        } finally {
            setIsUploading(false);
        }
    };
    
    const handleDelete = async () => {
        if (!window.confirm('Êtes-vous sûr de vouloir supprimer votre CV ?')) return;
        setIsLoading(true);
        try {
            await resumeService.deleteResume();
            setCvData(null);
            setStatusMessage({ text: 'CV supprimé avec succès.', type: 'success' });
        } catch (error) {
            setStatusMessage({ text: error.message, type: 'error' });
        } finally {
            setIsLoading(false);
        }
    };

    // Fonctions pour le Drag & Drop
    const handleDragEvents = (e, over) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragOver(over);
    };
    
    const handleDrop = (e) => {
        handleDragEvents(e, false);
        const file = e.dataTransfer.files[0];
        handleFileSelect(file);
    };

    return (
        <div className="tab-content">
            <div className="content-header">
            </div>
            <div className="resume-grid">
                {/* Colonne de gauche : Upload */}
                <div className="upload-card">
                    <h3>Gérer mon CV</h3>
                    <div 
                        className={`upload-area ${isDragOver ? 'drag-over' : ''}`}
                        onClick={() => fileInputRef.current.click()}
                        onDragEnter={(e) => handleDragEvents(e, true)}
                        onDragLeave={(e) => handleDragEvents(e, false)}
                        onDragOver={(e) => handleDragEvents(e, true)}
                        onDrop={handleDrop}
                    >
                        <div className="upload-icon"><i className="fas fa-cloud-upload-alt"></i></div>
                        <p className="upload-text">Glissez-déposez ou cliquez ici</p>
                        <p className="upload-hint">Format PDF uniquement</p>
                        <input 
                            type="file" 
                            accept=".pdf" 
                            ref={fileInputRef}
                            onChange={(e) => handleFileSelect(e.target.files[0])}
                            style={{ display: 'none' }}
                        />
                    </div>
                    {statusMessage.text && <p className={`status-message ${statusMessage.type}`}>{statusMessage.text}</p>}
                    <button onClick={handleUpload} disabled={!selectedFile || isUploading} className="btn-primary" style={{width: '100%', marginTop: '1rem'}}>
                        {isUploading ? 'Analyse en cours...' : 'Analyser mon CV'}
                    </button>
                    {cvData && (
                        <button onClick={handleDelete} className="btn-danger" style={{width: '100%', marginTop: '1rem'}}>
                            Supprimer le CV actuel
                        </button>
                    )}
                </div>

                {/* Colonne de droite : Analyse */}
                <div className="analysis-card">
                    <div className="analysis-header cv-section-header">Profil Analysé</div>
                    {(isLoading || isUploading) && (
                        <div className="analysis-loading-overlay">
                            <div className="spinner"></div>
                            <p style={{marginTop: '1rem', color: '#6b7280'}}>{isUploading ? 'Analyse en cours...' : 'Chargement...'}</p>
                        </div>
                    )}
                    <div className="cv-section-body">
                        {!isLoading && cvData ? (
                            <CvDataDisplay cvData={cvData} />
                        ) : !isLoading && (
                            <div style={{ textAlign: 'center', padding: '3rem' }}>
                                <i className="fas fa-eye-slash fa-2x" style={{color: '#9ca3af'}}></i>
                                <h4 style={{ marginTop: '1rem' }}>Aucune donnée à afficher</h4>
                                <p>Veuillez télécharger un CV pour que notre IA l'analyse.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResumeTab;