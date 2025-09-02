import React, { useState } from 'react';

import Layout from '../components/tabs/Layout';
import ResumeTab from '../components/tabs/ResumeTab';
import JobsTab from '../components/tabs/JobsTab';
import InterviewTab from '../components/tabs/InterviewTab';
import FeedbacksTab from '../components/tabs/FeedbacksTab';

import WelcomeAlert from '../components/dashboard/WelcomeAlert';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import GettingStarted from '../components/dashboard/GettingStarted';
import Support from '../components/dashboard/Support';

import '../style/HomePage.css';

const HomePage = ({ user }) => {
    const [activeSection, setActiveSection] = useState('home');
    const [isAlertVisible, setAlertVisible] = useState(true);
    const userName = user?.name || 'Utilisateur';

    const HomeContent = () => (
        <div className="home-dashboard">
            <DashboardHeader userName={userName} />
            <GettingStarted onStepClick={setActiveSection} />
            <Support user={user} />
                        {isAlertVisible && (
            <WelcomeAlert userName={userName} onClose={() => setAlertVisible(false)} />
            )}
        </div>
    );

    const renderContent = () => {
        switch (activeSection) {
            case 'home':
                return <HomeContent />;
            case 'resume':
                return <ResumeTab />;
            case 'jobs':
                return <JobsTab />;
            case 'interview':
                return <InterviewTab />;
            case 'feedbacks':
                return <FeedbacksTab />;
            case 'settings':
                return (
                    <div className="settings-content">
                        <h1>Paramètres</h1>
                        <p>Page des paramètres à implémenter</p>
                    </div>
                );
            default:
                return <HomeContent />;
        }
    };

    return (
        <Layout
            activeSection={activeSection}
            onSectionChange={setActiveSection}
            user={user}
        >
            {renderContent()}
        </Layout>
    );
};

export default HomePage;