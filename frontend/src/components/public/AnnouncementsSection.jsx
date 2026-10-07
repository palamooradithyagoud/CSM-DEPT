import React, { useState } from 'react';
import { Pin, Calendar, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';

export default function AnnouncementsSection({ announcements = [] }) {
  const [expandedId, setExpandedId] = useState(null);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <section id="announcements" className="section-padding announcements-root">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-subtitle">Official Circulars & Notices</span>
          <h2 className="section-title">Department Announcements</h2>
          <p className="section-desc">
            Official departmental notifications, end-term examination timetables, and academic attendance regulations.
          </p>
        </div>

        {/* Notices Stack */}
        <div className="notices-stack">
          {announcements.map((item) => {
            const isExpanded = expandedId === item.id;
            return (
              <div
                key={item.id}
                className={`notice-card ${item.isPinned ? 'pinned-card' : ''}`}
                onClick={() => toggleExpand(item.id)}
              >
                <div className="notice-summary-row">
                  <div className="notice-left">
                    {item.isPinned && (
                      <div className="pinned-badge" title="Pinned Announcement">
                        <Pin size={13} />
                        <span>Pinned</span>
                      </div>
                    )}
                    <span className="category-pill">{item.category}</span>
                    <h3 className="notice-title">{item.title}</h3>
                  </div>

                  <div className="notice-right">
                    <div className="notice-date">
                      <Calendar size={13} />
                      <span>{item.publishDate ? new Date(item.publishDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'Recent'}</span>
                    </div>
                    <button className="expand-chevron" aria-label="Toggle details">
                      {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div className="notice-expanded-body">
                    <p className="notice-content-text">{item.content}</p>
                    <div className="notice-stamp">
                      <span>Official Circular • Department Office of Computer Science & Engineering</span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <style>{`
        .announcements-root {
          background-color: var(--color-background);
          border-bottom: 1px solid var(--color-border);
        }
        .notices-stack {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .notice-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          padding: 16px 20px;
          cursor: pointer;
          transition: border-color var(--transition-fast), background-color var(--transition-fast);
        }
        .notice-card:hover {
          border-color: #383842;
          background: var(--color-card-hover);
        }
        .pinned-card {
          border-left: 3px solid var(--color-primary);
        }
        .notice-summary-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
        }
        .notice-left {
          display: flex;
          align-items: center;
          gap: 12px;
          flex-wrap: wrap;
          flex-grow: 1;
        }
        .pinned-badge {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          font-size: 0.6875rem;
          font-weight: 700;
          color: var(--color-primary);
          background: var(--color-primary-subtle);
          padding: 3px 8px;
          border-radius: var(--radius-sm);
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }
        .category-pill {
          font-size: 0.75rem;
          color: var(--color-text-muted);
          background: var(--color-secondary);
          padding: 3px 8px;
          border-radius: var(--radius-sm);
          border: 1px solid var(--color-border);
        }
        .notice-title {
          font-size: 0.9375rem;
          font-weight: 600;
          color: var(--color-text-main);
          letter-spacing: -0.01em;
        }
        .notice-right {
          display: flex;
          align-items: center;
          gap: 16px;
          flex-shrink: 0;
        }
        .notice-date {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.8125rem;
          color: var(--color-text-muted);
        }
        .expand-chevron {
          color: var(--color-text-muted);
          display: flex;
          align-items: center;
        }
        .notice-expanded-body {
          margin-top: 14px;
          padding-top: 14px;
          border-top: 1px solid var(--color-border-subtle);
        }
        .notice-content-text {
          font-size: 0.875rem;
          color: var(--color-text-secondary);
          line-height: 1.7;
          max-width: 100%;
          margin-bottom: 10px;
        }
        .notice-stamp {
          font-size: 0.75rem;
          color: var(--color-text-muted);
          font-style: italic;
        }
        @media (max-width: 768px) {
          .notice-summary-row {
            flex-direction: column;
            align-items: flex-start;
          }
          .notice-right {
            width: 100%;
            justify-content: space-between;
          }
        }
      `}</style>
    </section>
  );
}
