import React from 'react';
import { Trophy, Award, Users, CheckCircle2 } from 'lucide-react';

export default function AchievementsSection({ achievements = [] }) {
  return (
    <section id="achievements" className="section-padding achievements-root">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-subtitle">Student Accolades & Competitions</span>
          <h2 className="section-title">Department Achievements</h2>
          <p className="section-desc">
            National hackathon prizes, IEEE research papers, and competitive programming excellence by our undergraduate scholars.
          </p>
        </div>

        {/* Achievements Grid */}
        <div className="achievements-grid">
          {achievements.map((item) => (
            <div key={item.id} className="achievement-card">
              <div className="card-top">
                <div className="trophy-wrap">
                  <Trophy size={20} />
                </div>
                <div className="award-pill">
                  <span>{item.award}</span>
                </div>
              </div>

              <h3 className="achieve-title">{item.title}</h3>
              <div className="event-meta-pill">
                <span className="event-label">Competition:</span>
                <span className="event-name">{item.eventName}</span>
              </div>

              <p className="achieve-desc">{item.description}</p>

              <div className="achieve-footer">
                <div className="scholars-block">
                  <div className="scholars-header">
                    <Users size={14} className="scholars-icon" />
                    <span>Scholars:</span>
                  </div>
                  <span className="scholars-names">{item.studentNames}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        .achievements-root {
          background-color: var(--color-background);
          border-bottom: 1px solid var(--color-border);
        }
        .achievements-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: var(--space-xl);
        }
        .achievement-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-xl);
          display: flex;
          flex-direction: column;
          transition: border-color var(--transition-base), transform var(--transition-base);
        }
        .achievement-card:hover {
          border-color: #383842;
          transform: translateY(-2px);
        }
        .card-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: var(--space-md);
        }
        .trophy-wrap {
          width: 38px;
          height: 38px;
          border-radius: var(--radius-md);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--color-primary);
        }
        .award-pill {
          padding: 4px 10px;
          border-radius: var(--radius-full);
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--color-primary);
          background: var(--color-primary-subtle);
          border: 1px solid var(--color-primary-border);
        }
        .achieve-title {
          font-size: 1.125rem;
          font-weight: 700;
          color: var(--color-text-main);
          margin-bottom: var(--space-xs);
          line-height: 1.35;
        }
        .event-meta-pill {
          display: flex;
          gap: 6px;
          font-size: 0.8125rem;
          margin-bottom: var(--space-sm);
        }
        .event-label {
          color: var(--color-text-muted);
        }
        .event-name {
          color: var(--color-text-secondary);
          font-weight: 500;
        }
        .achieve-desc {
          font-size: 0.875rem;
          color: var(--color-text-secondary);
          line-height: 1.6;
          margin-bottom: var(--space-lg);
          flex-grow: 1;
        }
        .achieve-footer {
          padding-top: var(--space-md);
          border-top: 1px solid var(--color-border-subtle);
        }
        .scholars-block {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .scholars-header {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.75rem;
          color: var(--color-text-muted);
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }
        .scholars-icon {
          color: var(--color-text-muted);
        }
        .scholars-names {
          font-size: 0.8125rem;
          font-weight: 600;
          color: var(--color-text-main);
          line-height: 1.4;
        }
        @media (max-width: 960px) {
          .achievements-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
        @media (max-width: 600px) {
          .achievements-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
