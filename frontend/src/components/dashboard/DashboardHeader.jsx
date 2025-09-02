import React from 'react';

const DashboardHeader = ({ userName }) => (
    <div className="dashboard-header">
        <p className="dashboard-title">Bonjour, {userName}</p>
        <p className="dashboard-subtitle">Bienvenue sur AIrh</p>
    </div>
);

export default DashboardHeader;