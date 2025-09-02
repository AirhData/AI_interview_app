import React, { useState } from 'react';
import ContactPopup from './ContactPopup';

const Support = ({ user }) => {
    const [isContactPopupOpen, setContactPopupOpen] = useState(false);

    return (
        <>
            <div className="support-section">
                <div className="support-card">
                    <h3 className="support-title">Contact</h3>
                    <p className="support-description">
                        Contactez-nous pour toute question ou feedback.
                    </p>
                    <button className="contact-btn" onClick={() => setContactPopupOpen(true)}>
                        Nous contacter
                    </button>
                </div>
            </div>

            <ContactPopup
                isOpen={isContactPopupOpen}
                onClose={() => setContactPopupOpen(false)}
                user={user} 
            />
        </>
    );
};

export default Support;