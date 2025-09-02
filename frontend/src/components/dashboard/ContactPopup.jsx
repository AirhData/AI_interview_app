import React, { useState, useEffect } from 'react';
import { contactService } from '../../services/contactService';
import '../../style/ContactPopup.css';

const ContactPopup = ({ isOpen, onClose, user }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });
  const [status, setStatus] = useState({ sending: false, success: false, error: null });

  useEffect(() => {
    if (user) {
      setFormData(prev => ({ ...prev, name: user.name || '', email: user.email || '' }));
    }
  }, [user]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ sending: true, success: false, error: null });
    try {
      await contactService.sendContactEmail(formData);
      setStatus({ sending: false, success: true, error: null });
      setTimeout(() => {
        onClose();
        setStatus({ sending: false, success: false, error: null });
      }, 2000);
    } catch (error) {
      setStatus({ sending: false, success: false, error: 'Erreur lors de l\'envoi du message.' });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="contact-popup-overlay" onClick={onClose}>
      <div className="contact-popup-container" onClick={e => e.stopPropagation()}>
        <div className="contact-popup-header">
          <h2 className="contact-popup-title">Contactez-nous</h2>
          <button className="contact-popup-close" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        </div>
        <div className="contact-popup-body">
          {status.success && <div className="contact-success-message">Message envoyé avec succès !</div>}
          {status.error && <div className="contact-error-message">{status.error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name" className="form-label">Nom</label>
              <input type="text" id="name" name="name" className="form-control" value={formData.name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="email" className="form-label">Email</label>
              <input type="email" id="email" name="email" className="form-control" value={formData.email} onChange={handleChange} required readOnly={!!user?.email} />
            </div>
            <div className="form-group">
              <label htmlFor="subject" className="form-label">Sujet</label>
              <select id="subject" name="subject" className="form-control" value={formData.subject} onChange={handleChange} required>
                <option value="">Sélectionnez un sujet</option>
                <option value="feedback">Feedback</option>
                <option value="feature">Demande de feature</option>
                <option value="problem">Problème</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="message" className="form-label">Message</label>
              <textarea id="message" name="message" rows="5" className="form-control" value={formData.message} onChange={handleChange} required></textarea>
            </div>
            <button type="submit" className="btn-contact" disabled={status.sending}>
              {status.sending ? 'Envoi en cours...' : 'Envoyer'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ContactPopup;