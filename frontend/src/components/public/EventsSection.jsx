import React, { useState } from 'react';
import { Calendar, MapPin, Tag } from 'lucide-react';

export default function EventsSection({ events = [] }) {
  const [activeCategory, setActiveCategory] = useState('ALL');

  const categories = ['ALL', 'Conference', 'Hackathon', 'Workshop', 'Guest Lecture'];

  const filteredEvents = events.filter((ev) => {
    if (activeCategory === 'ALL') return true;
    return ev.category.toLowerCase() === activeCategory.toLowerCase();
  });

  return (
    <section id="events" className="section-padding events-root">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-subtitle">Conferences & Technical Activities</span>
          <h2 className="section-title">Department Events</h2>
          <p className="section-desc">
            National conferences, industry hackathons, faculty development initiatives, and technical symposiums.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="category-pills-row">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`cat-pill ${activeCategory === cat ? 'active' : ''}`}
            >
              {cat === 'ALL' ? 'All Activities' : cat}
            </button>
          ))}
        </div>

        {/* Events Grid */}
        <div className="events-grid">
          {filteredEvents.map((item) => (
            <div key={item.id} className="event-card">
              <div className="event-card-top">
                <div className="event-date-badge">
                  <Calendar size={14} className="date-icon" />
                  <span>{item.eventDate ? new Date(item.eventDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'TBA'}</span>
                </div>
                <div className="event-status-tags">
                  {item.isUpcoming && (
                    <span className="badge badge-success">Upcoming</span>
                  )}
                  <span className="category-tag">{item.category}</span>
                </div>
              </div>

              <h3 className="event-title">{item.title}</h3>
              <p className="event-desc">{item.description}</p>

              <div className="event-footer">
                <div className="location-pill">
                  <MapPin size={14} />
                  <span>{item.location}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        .events-root {
          background-color: var(--color-background);
          border-bottom: 1px solid var(--color-border);
        }
        .category-pills-row {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
          margin-bottom: var(--space-2xl);
        }
        .cat-pill {
          padding: 6px 14px;
          font-size: 0.8125rem;
          color: var(--color-text-secondary);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          transition: all var(--transition-fast);
        }
        .cat-pill:hover {
          color: var(--color-text-main);
          border-color: #3b3b42;
        }
        .cat-pill.active {
          color: #050506;
          background: var(--color-primary);
          border-color: var(--color-primary);
          font-weight: 600;
        }
        .events-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: var(--space-xl);
        }
        .event-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-xl);
          display: flex;
          flex-direction: column;
          transition: border-color var(--transition-base), transform var(--transition-base);
        }
        .event-card:hover {
          border-color: #383842;
          transform: translateY(-2px);
        }
        .event-card-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: var(--space-md);
        }
        .event-date-badge {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.8125rem;
          color: var(--color-primary);
          font-weight: 600;
        }
        .date-icon {
          color: var(--color-primary);
        }
        .event-status-tags {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .category-tag {
          font-size: 0.75rem;
          color: var(--color-text-muted);
          background: var(--color-secondary);
          padding: 3px 8px;
          border-radius: var(--radius-sm);
          border: 1px solid var(--color-border-subtle);
        }
        .event-title {
          font-size: 1.1875rem;
          font-weight: 700;
          color: var(--color-text-main);
          margin-bottom: var(--space-sm);
          line-height: 1.35;
        }
        .event-desc {
          font-size: 0.9375rem;
          color: var(--color-text-secondary);
          line-height: 1.6;
          margin-bottom: var(--space-lg);
          flex-grow: 1;
        }
        .event-footer {
          display: flex;
          align-items: center;
          padding-top: var(--space-md);
          border-top: 1px solid var(--color-border-subtle);
        }
        .location-pill {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.8125rem;
          color: var(--color-text-muted);
        }
        @media (max-width: 800px) {
          .events-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
