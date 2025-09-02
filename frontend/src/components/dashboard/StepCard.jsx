import React from 'react';

const StepCard = ({ number, icon, title, description, onClick }) => (
    <div className="step-card" onClick={onClick}>
        <div className="step-header">
            <span className="step-number">Étape {number}</span>
        </div>
        <div className="step-icon">
            <i className={`fas ${icon}`}></i>
        </div>
        <h3 className="step-title">{title}</h3>
        <p className="step-description">{description}</p>
        <button className="step-arrow">
            <i className="fas fa-arrow-right"></i>
        </button>
    </div>
);

export default StepCard;