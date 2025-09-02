import React from 'react';
import StepCard from './StepCard';

const GettingStarted = ({ onStepClick }) => {
    const steps = [
        {
            id: 'resume',
            number: 1,
            icon: 'fa-file-alt',
            title: 'Téléchargez votre CV',
            description: 'Téléchargez votre CV pour aider AIrh à mieux vous connaître',
        },
        {
            id: 'jobs',
            number: 2,
            icon: 'fa-briefcase',
            title: 'Parcourez nos offres d\'emplois',
            description: 'parcourez et filtrez nos offres disponibles selon vos critéres',
        },
        {
            id: 'interview',
            number: 3,
            icon: 'fa-users',
            title: 'Démarrez un entretien',
            description: 'Lancez votre entretien avec Roni notre agent IA',
        },
    ];

    return (
        <div className="getting-started-section">
            <h2 className="section-heading">Demarrer en 3 étapes :</h2>
            <div className="steps-grid">
                {steps.map((step) => (
                    <StepCard
                        key={step.id}
                        number={step.number}
                        icon={step.icon}
                        title={step.title}
                        description={step.description}
                        onClick={() => onStepClick(step.id)}
                    />
                ))}
            </div>
        </div>
    );
};

export default GettingStarted;