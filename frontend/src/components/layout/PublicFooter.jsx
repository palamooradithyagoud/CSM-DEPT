import React from 'react';
import { GraduationCap, Mail, Phone, MapPin, ShieldCheck } from 'lucide-react';

export default function PublicFooter({ onOpenLogin }) {
  return (
    <footer className="footer-root">
      <div className="container footer-content">
        <div className="footer-grid">
          {/* Col 1: Identity & Accreditation */}
          <div className="footer-col">
            <div className="footer-brand">
              <div className="footer-brand-icon">
                <GraduationCap size={20} />
              </div>
              <span className="footer-brand-title">Department of CSE</span>
            </div>
            <p className="footer-desc">
              Dedicated to foundational computer science education, scalable systems research, and outcome-based academic excellence.
            </p>
            <div className="accreditation-badges">
              <span className="badge badge-success">NBA Accredited (Tier-I)</span>
              <span className="badge badge-neutral">NAAC A++ Grade</span>
            </div>
          </div>

          {/* Col 2: Navigation Links */}
          <div className="footer-col">
            <h4 className="footer-heading">Department Sections</h4>
            <ul className="footer-list">
              <li><a href="#overview">Overview & Highlights</a></li>
              <li><a href="#about">About & Leadership</a></li>
              <li><a href="#faculty">Faculty Directory</a></li>
              <li><a href="#events">Conferences & Hackathons</a></li>
              <li><a href="#achievements">Student Accolades</a></li>
              <li><a href="#announcements">Circulars & Notices</a></li>
            </ul>
          </div>

          {/* Col 3: Research & Facilities */}
          <div className="footer-col">
            <h4 className="footer-heading">Academic Facilities</h4>
            <ul className="footer-list">
              <li><span>AI & Deep Learning Computing Lab</span></li>
              <li><span>Network Security & CTF Sandbox</span></li>
              <li><span>Embedded Systems & IoT Laboratory</span></li>
              <li><span>Database Systems & Cloud Cluster</span></li>
              <li><span>Undergraduate Project Studio</span></li>
            </ul>
          </div>

          {/* Col 4: Official Contacts */}
          <div className="footer-col">
            <h4 className="footer-heading">Office of the HOD</h4>
            <div className="contact-details">
              <div className="contact-item">
                <MapPin size={16} className="contact-icon" />
                <span>Block-A, Room 302, Academic Enclave</span>
              </div>
              <div className="contact-item">
                <Mail size={16} className="contact-icon" />
                <a href="mailto:hod.cse@college.edu">hod.cse@college.edu</a>
              </div>
              <div className="contact-item">
                <Phone size={16} className="contact-icon" />
                <span>+91 40 2345 6789</span>
              </div>
            </div>
            <div className="auth-portal-link">
              <button onClick={onOpenLogin} className="portal-direct-btn">
                <ShieldCheck size={14} />
                <span>HOD / Administrator Access</span>
              </button>
            </div>
          </div>
        </div>

        {/* Disclaimer on Academic Privacy */}
        <div className="footer-disclaimer">
          <p>
            <strong>Academic Privacy Notice:</strong> This public portal provides departmental information, faculty profiles, and institutional activities. Individual student marks, SGPA/CGPA transcripts, subject-wise attendance logs, and academic analytics are confidential under institutional policy and restricted to authenticated academic leadership.
          </p>
        </div>

        {/* Bottom Bar */}
        <div className="footer-bottom">
          <p className="copyright-text">
            © {new Date().getFullYear()} Department of Computer Science & Engineering. All rights reserved.
          </p>
          <div className="system-pill">
            Academic Performance & Department Management System
          </div>
        </div>
      </div>

      <style>{`
        .footer-root {
          background-color: #030304;
          border-top: 1px solid var(--color-border);
          padding-top: var(--space-3xl);
          padding-bottom: var(--space-xl);
          margin-top: var(--space-3xl);
        }
        .footer-grid {
          display: grid;
          grid-template-columns: 1.5fr 1fr 1.2fr 1.3fr;
          gap: var(--space-2xl);
          margin-bottom: var(--space-2xl);
        }
        .footer-brand {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: var(--space-md);
        }
        .footer-brand-icon {
          width: 32px;
          height: 32px;
          border-radius: var(--radius-sm);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--color-primary);
        }
        .footer-brand-title {
          font-family: var(--font-display);
          font-weight: 700;
          font-size: 1.0625rem;
          color: var(--color-text-main);
        }
        .footer-desc {
          font-size: 0.875rem;
          color: var(--color-text-secondary);
          line-height: 1.6;
          margin-bottom: var(--space-md);
        }
        .accreditation-badges {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        .footer-heading {
          font-size: 0.9375rem;
          font-weight: 600;
          color: var(--color-text-main);
          margin-bottom: var(--space-md);
          letter-spacing: -0.01em;
        }
        .footer-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .footer-list li a, .footer-list li span {
          font-size: 0.875rem;
          color: var(--color-text-secondary);
          transition: color var(--transition-fast);
        }
        .footer-list li a:hover {
          color: var(--color-primary);
        }
        .contact-details {
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-bottom: var(--space-md);
        }
        .contact-item {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          font-size: 0.875rem;
          color: var(--color-text-secondary);
        }
        .contact-icon {
          color: var(--color-text-muted);
          flex-shrink: 0;
          margin-top: 3px;
        }
        .contact-item a:hover {
          color: var(--color-primary);
        }
        .portal-direct-btn {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          font-size: 0.8125rem;
          color: var(--color-text-secondary);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          padding: 6px 12px;
          border-radius: var(--radius-sm);
          transition: all var(--transition-fast);
        }
        .portal-direct-btn:hover {
          color: var(--color-primary);
          border-color: var(--color-primary-border);
        }
        .footer-disclaimer {
          padding: var(--space-md) var(--space-lg);
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          margin-bottom: var(--space-xl);
        }
        .footer-disclaimer p {
          font-size: 0.8125rem;
          color: var(--color-text-muted);
          line-height: 1.5;
          max-width: 100%;
        }
        .footer-disclaimer strong {
          color: var(--color-text-secondary);
        }
        .footer-bottom {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-top: var(--space-lg);
          border-top: 1px solid var(--color-border);
        }
        .copyright-text {
          font-size: 0.8125rem;
          color: var(--color-text-muted);
        }
        .system-pill {
          font-size: 0.75rem;
          color: var(--color-text-muted);
          background: var(--color-secondary);
          padding: 4px 10px;
          border-radius: var(--radius-full);
          border: 1px solid var(--color-border);
        }
        @media (max-width: 960px) {
          .footer-grid {
            grid-template-columns: 1fr 1fr;
          }
        }
        @media (max-width: 600px) {
          .footer-grid {
            grid-template-columns: 1fr;
          }
          .footer-bottom {
            flex-direction: column;
            gap: 12px;
            text-align: center;
          }
        }
      `}</style>
    </footer>
  );
}
