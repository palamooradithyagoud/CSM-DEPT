import React, { useState } from 'react';
import {
  MapPin,
  Mail,
  Phone,
  Clock,
  Building,
  Globe,
  Send,
  CheckCircle2,
  ExternalLink,
  MessageSquare
} from 'lucide-react';

export default function ContactSection({ department }) {
  const contact = department?.contact || {};
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: 'General Academic Enquiry',
    message: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.message) return;
    setFormSubmitted(true);
    setTimeout(() => {
      setFormData({ name: '', email: '', subject: 'General Academic Enquiry', message: '' });
      setFormSubmitted(false);
    }, 4000);
  };

  return (
    <section id="contact" className="section-padding contact-root">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-subtitle">Department Headquarters & Enquiries</span>
          <h2 className="section-title">Contact & Campus Location</h2>
          <p className="section-desc">
            Direct communication channels to the administrative office of the Head of the Department and academic coordinators.
          </p>
        </div>

        {/* 2-Column Main Contact Grid */}
        <div className="contact-main-grid">
          {/* Left Column: Department Coordinates & Office Info */}
          <div className="contact-details-col">
            {/* Card 1: Secretariat & Digital Links */}
            <div className="contact-card">
              <div className="card-icon-wrap">
                <Building size={20} />
              </div>
              <h3 className="card-title">HOD Administrative Secretariat</h3>

              <div className="info-list">
                <div className="info-item">
                  <MapPin size={16} className="info-icon" />
                  <div>
                    <span className="info-heading">Campus Address</span>
                    <p className="info-text">{contact.officeLocation || "Block-A, Room 302, Academic Enclave, Main Campus"}</p>
                  </div>
                </div>

                <div className="info-item">
                  <Mail size={16} className="info-icon" />
                  <div>
                    <span className="info-heading">Official Communication</span>
                    <a href={`mailto:${contact.email || "hod.cse@college.edu"}`} className="info-link">
                      {contact.email || "hod.cse@college.edu"}
                    </a>
                  </div>
                </div>

                <div className="info-item">
                  <Phone size={16} className="info-icon" />
                  <div>
                    <span className="info-heading">Telephone Intercom</span>
                    <span className="info-text">{contact.phone || "+91 40 2345 6789"}</span>
                  </div>
                </div>

                <div className="info-item">
                  <Globe size={16} className="info-icon" />
                  <div>
                    <span className="info-heading">Institutional Portal</span>
                    <a href="https://www.college.edu" target="_blank" rel="noreferrer" className="info-link">
                      www.college.edu <ExternalLink size={12} style={{ display: 'inline' }} />
                    </a>
                  </div>
                </div>
              </div>
            </div>

            {/* Card 2: Consultation Timings */}
            <div className="contact-card">
              <div className="card-icon-wrap">
                <Clock size={20} />
              </div>
              <h3 className="card-title">Academic Consultation Hours</h3>

              <div className="timing-stack">
                <div className="timing-row">
                  <span className="timing-day">Monday – Friday:</span>
                  <span className="timing-time">09:00 AM – 04:30 PM</span>
                </div>
                <div className="timing-row">
                  <span className="timing-day">HOD Student Hours:</span>
                  <span className="timing-time">02:30 PM – 04:00 PM (Daily)</span>
                </div>
                <div className="timing-row">
                  <span className="timing-day">Saturday (Remedial & Labs):</span>
                  <span className="timing-time">09:30 AM – 01:00 PM</span>
                </div>
              </div>

              {/* Social Channels Placeholders */}
              <div className="social-channels-row">
                <span className="social-label">Departmental Media:</span>
                <div className="social-tags">
                  <span className="social-pill">LinkedIn</span>
                  <span className="social-pill">GitHub</span>
                  <span className="social-pill">YouTube</span>
                  <span className="social-pill">Twitter/X</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Interactive Query Form & Campus Locator */}
          <div className="contact-form-col">
            <div className="query-card">
              <div className="query-card-header">
                <div className="query-icon-wrap">
                  <MessageSquare size={18} />
                </div>
                <div>
                  <h3 className="card-title" style={{ marginBottom: 2 }}>Department Query Dispatch</h3>
                  <span className="form-subtext">Submit academic inquiries to departmental coordinators</span>
                </div>
              </div>

              {formSubmitted ? (
                <div className="form-success-banner">
                  <CheckCircle2 size={24} className="success-icon" />
                  <div>
                    <h4 className="success-title">Enquiry Transmitted</h4>
                    <p className="success-msg">Your enquiry has been logged with the Department Secretariat. A coordinator will respond via your provided institutional email.</p>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="query-form">
                  <div className="form-row-2">
                    <div className="form-field">
                      <label htmlFor="contact-name" className="field-label">Full Name</label>
                      <input
                        id="contact-name"
                        type="text"
                        placeholder="e.g. Aditya Sharma"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                        className="form-input"
                      />
                    </div>
                    <div className="form-field">
                      <label htmlFor="contact-email" className="field-label">Email Address</label>
                      <input
                        id="contact-email"
                        type="email"
                        placeholder="scholar@college.edu"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        required
                        className="form-input"
                      />
                    </div>
                  </div>

                  <div className="form-field">
                    <label htmlFor="contact-subject" className="field-label">Enquiry Category</label>
                    <select
                      id="contact-subject"
                      value={formData.subject}
                      onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                      className="form-select"
                    >
                      <option value="General Academic Enquiry">General Academic Enquiry</option>
                      <option value="2nd Year Academic Coordination">2nd Year Academic Coordination</option>
                      <option value="End-Term Lab Observation Query">End-Term Lab Observation Query</option>
                      <option value="Research & Hackathon Mentorship">Research & Hackathon Mentorship</option>
                    </select>
                  </div>

                  <div className="form-field">
                    <label htmlFor="contact-message" className="field-label">Message Details</label>
                    <textarea
                      id="contact-message"
                      rows={4}
                      placeholder="Please articulate your departmental query..."
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      required
                      className="form-textarea"
                    ></textarea>
                  </div>

                  <button type="submit" className="btn btn-primary form-submit-btn">
                    <Send size={15} />
                    <span>Submit Academic Enquiry</span>
                  </button>
                </form>
              )}
            </div>

            {/* Stylized Campus Map Placeholder */}
            <div className="campus-map-card">
              <div className="map-placeholder-header">
                <MapPin size={14} className="map-pin-icon" />
                <span>Academic Enclave • Department of Computer Science & Engineering</span>
              </div>
              <div className="map-visual-frame">
                <div className="map-grid-pattern"></div>
                <div className="campus-building-node">
                  <span className="node-beacon"></span>
                  <span className="node-label">CSE Department (Block A, 3rd Floor)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .contact-root {
          background-color: var(--color-background);
          border-bottom: 1px solid var(--color-border);
        }
        .contact-main-grid {
          display: grid;
          grid-template-columns: 1fr 1.15fr;
          gap: var(--space-2xl);
        }
        .contact-details-col {
          display: flex;
          flex-direction: column;
          gap: var(--space-xl);
        }
        .contact-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-xl);
        }
        .card-icon-wrap {
          width: 40px;
          height: 40px;
          border-radius: var(--radius-md);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--color-primary);
          margin-bottom: var(--space-md);
        }
        .card-title {
          font-size: 1.0625rem;
          font-weight: 700;
          color: var(--color-text-main);
          margin-bottom: var(--space-md);
        }
        .info-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .info-item {
          display: flex;
          align-items: flex-start;
          gap: 12px;
        }
        .info-icon {
          color: var(--color-primary);
          flex-shrink: 0;
          margin-top: 3px;
        }
        .info-heading {
          display: block;
          font-size: 0.6875rem;
          color: var(--color-text-muted);
          text-transform: uppercase;
          letter-spacing: 0.04em;
          margin-bottom: 2px;
        }
        .info-text {
          font-size: 0.875rem;
          color: var(--color-text-secondary);
          line-height: 1.5;
        }
        .info-link {
          font-size: 0.875rem;
          color: var(--color-primary);
          display: inline-flex;
          align-items: center;
          gap: 4px;
        }
        .timing-stack {
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-bottom: var(--space-lg);
        }
        .timing-row {
          display: flex;
          justify-content: space-between;
          font-size: 0.8125rem;
          padding-bottom: 8px;
          border-bottom: 1px solid var(--color-border-subtle);
        }
        .timing-day {
          color: var(--color-text-muted);
        }
        .timing-time {
          color: var(--color-text-main);
          font-weight: 600;
        }
        .social-channels-row {
          padding-top: var(--space-sm);
        }
        .social-label {
          display: block;
          font-size: 0.75rem;
          color: var(--color-text-muted);
          margin-bottom: 8px;
        }
        .social-tags {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        .social-pill {
          font-size: 0.75rem;
          color: var(--color-text-secondary);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          padding: 4px 10px;
          border-radius: var(--radius-sm);
        }
        /* Right Query Card */
        .query-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-xl);
          margin-bottom: var(--space-xl);
        }
        .query-card-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: var(--space-lg);
        }
        .query-icon-wrap {
          width: 36px;
          height: 36px;
          border-radius: var(--radius-md);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--color-primary);
        }
        .form-subtext {
          font-size: 0.75rem;
          color: var(--color-text-muted);
        }
        .query-form {
          display: flex;
          flex-direction: column;
          gap: var(--space-md);
        }
        .form-row-2 {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: var(--space-md);
        }
        .form-field {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .field-label {
          font-size: 0.8125rem;
          font-weight: 600;
          color: var(--color-text-secondary);
        }
        .form-input, .form-select, .form-textarea {
          width: 100%;
        }
        .form-submit-btn {
          margin-top: 4px;
          padding: 12px;
        }
        .form-success-banner {
          display: flex;
          align-items: flex-start;
          gap: 14px;
          background: var(--color-primary-subtle);
          border: 1px solid var(--color-primary-border);
          border-radius: var(--radius-md);
          padding: 16px;
          color: var(--color-primary);
        }
        .success-icon {
          flex-shrink: 0;
          margin-top: 2px;
        }
        .success-title {
          font-size: 0.9375rem;
          font-weight: 700;
          margin-bottom: 4px;
        }
        .success-msg {
          font-size: 0.8125rem;
          color: var(--color-text-secondary);
          line-height: 1.5;
        }
        /* Campus Map Card */
        .campus-map-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          overflow: hidden;
        }
        .map-placeholder-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 0.75rem;
          color: var(--color-text-muted);
          padding: 10px 16px;
          border-bottom: 1px solid var(--color-border-subtle);
          background: var(--color-secondary);
        }
        .map-pin-icon {
          color: var(--color-primary);
        }
        .map-visual-frame {
          position: relative;
          height: 140px;
          background: #09090c;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .map-grid-pattern {
          position: absolute;
          inset: 0;
          background-image: linear-gradient(to right, #18181c 1px, transparent 1px),
                            linear-gradient(to bottom, #18181c 1px, transparent 1px);
          background-size: 20px 20px;
          opacity: 0.5;
        }
        .campus-building-node {
          position: relative;
          z-index: 2;
          display: flex;
          align-items: center;
          gap: 8px;
          background: var(--color-card);
          border: 1px solid var(--color-primary-border);
          padding: 8px 14px;
          border-radius: var(--radius-full);
          box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6);
        }
        .node-beacon {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--color-primary);
          box-shadow: 0 0 8px var(--color-primary);
        }
        .node-label {
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--color-text-main);
        }
        @media (max-width: 900px) {
          .contact-main-grid {
            grid-template-columns: 1fr;
          }
          .form-row-2 {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
