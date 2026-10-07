import React from 'react';
import { Target, Compass, Award, Quote } from 'lucide-react';

export default function AboutSection({ department }) {
  const hod = department?.hod || {};

  return (
    <section id="about" className="section-padding about-root">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-subtitle">Department Leadership & Vision</span>
          <h2 className="section-title">Academic Philosophy & Purpose</h2>
          <p className="section-desc">
            Equipping students with foundational computing principles, algorithmic rigor, and systematic performance mentorship.
          </p>
        </div>

        {/* HOD Welcome Card */}
        <div className="hod-message-card">
          <div className="hod-profile-pane">
            <div className="hod-avatar-frame">
              <img
                src={hod.photoUrl || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80"}
                alt={hod.name || "Head of Department"}
                className="hod-img"
              />
            </div>
            <div className="hod-meta">
              <h3 className="hod-name">{hod.name || "Dr. M. A. Jabbar"}</h3>
              <span className="hod-role">{hod.designation || "Professor & Head of Department"}</span>
              <span className="hod-deg">{hod.qualification || "Ph.D. (CSE), M.Tech, SMIEEE, FIETE"}</span>
            </div>
          </div>

          <div className="hod-text-pane">
            <div className="quote-mark">
              <Quote size={28} />
            </div>
            <h4 className="hod-message-heading">Message from the Head of the Department</h4>
            <p className="hod-paragraph">
              {hod.message || (
                "Welcome to the Department of Computer Science & Engineering. Our primary objective is to build " +
                "an intellectually vibrant environment that bridges rigorous academic theory with real-world technical execution. " +
                "Through continuous assessment, subject-wise attendance analytics, and outcome-oriented mentorship, we monitor " +
                "every student's trajectory to ensure no learner is left behind while top performers are propelled toward research " +
                "and industry leadership."
              )}
            </p>
            <div className="hod-sign-off">
              <span>Department of Computer Science & Engineering</span>
              <span className="established-tag">Established 2008</span>
            </div>
          </div>
        </div>

        {/* Vision & Mission Grid */}
        <div className="vm-grid">
          <div className="vm-card">
            <div className="vm-icon-row">
              <div className="vm-icon-wrap">
                <Target size={20} />
              </div>
              <h3 className="vm-title">Department Vision</h3>
            </div>
            <p className="vm-text">
              {department?.vision ||
                "To be a premier center of academic excellence and pioneering research in Computer Science and Engineering, producing globally competent professionals who innovate with social responsibility."}
            </p>
          </div>

          <div className="vm-card">
            <div className="vm-icon-row">
              <div className="vm-icon-wrap">
                <Compass size={20} />
              </div>
              <h3 className="vm-title">Department Mission</h3>
            </div>
            <div className="vm-text mission-list">
              {department?.mission?.split('\n').map((m, idx) => (
                <div key={idx} className="mission-item">
                  <span>{m}</span>
                </div>
              )) || (
                <p>Provide foundational computing education, cultivate research inquiry, and foster ethical leadership.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .about-root {
          background-color: var(--color-background);
          border-bottom: 1px solid var(--color-border);
        }
        .hod-message-card {
          display: grid;
          grid-template-columns: 320px 1fr;
          gap: var(--space-2xl);
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-2xl);
          margin-bottom: var(--space-2xl);
        }
        .hod-profile-pane {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          border-right: 1px solid var(--color-border);
          padding-right: var(--space-2xl);
        }
        .hod-avatar-frame {
          width: 140px;
          height: 140px;
          border-radius: 50%;
          overflow: hidden;
          border: 2px solid var(--color-border);
          margin-bottom: var(--space-md);
          background: var(--color-secondary);
        }
        .hod-img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .hod-name {
          font-size: 1.1875rem;
          font-weight: 700;
          color: var(--color-text-main);
          margin-bottom: 2px;
        }
        .hod-role {
          display: block;
          font-size: 0.8125rem;
          color: var(--color-primary);
          font-weight: 600;
          margin-bottom: 4px;
        }
        .hod-deg {
          display: block;
          font-size: 0.75rem;
          color: var(--color-text-muted);
        }
        .hod-text-pane {
          position: relative;
          display: flex;
          flex-direction: column;
          justify-content: center;
        }
        .quote-mark {
          color: var(--color-border);
          margin-bottom: var(--space-sm);
        }
        .hod-message-heading {
          font-size: 1.25rem;
          color: var(--color-text-main);
          margin-bottom: var(--space-md);
        }
        .hod-paragraph {
          font-size: 0.9375rem;
          color: var(--color-text-secondary);
          line-height: 1.7;
          margin-bottom: var(--space-lg);
          max-width: 100%;
        }
        .hod-sign-off {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-top: var(--space-md);
          border-top: 1px solid var(--color-border-subtle);
          font-size: 0.8125rem;
          color: var(--color-text-muted);
        }
        .established-tag {
          padding: 2px 8px;
          background: var(--color-secondary);
          border-radius: var(--radius-sm);
          border: 1px solid var(--color-border);
        }
        .vm-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: var(--space-xl);
        }
        .vm-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-xl);
        }
        .vm-icon-row {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: var(--space-md);
        }
        .vm-icon-wrap {
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
        .vm-title {
          font-size: 1.125rem;
          color: var(--color-text-main);
        }
        .vm-text {
          font-size: 0.9375rem;
          color: var(--color-text-secondary);
          line-height: 1.7;
        }
        .mission-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .mission-item {
          display: flex;
          align-items: flex-start;
          gap: 6px;
        }
        @media (max-width: 900px) {
          .hod-message-card {
            grid-template-columns: 1fr;
          }
          .hod-profile-pane {
            border-right: none;
            border-bottom: 1px solid var(--color-border);
            padding-right: 0;
            padding-bottom: var(--space-xl);
          }
          .vm-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
