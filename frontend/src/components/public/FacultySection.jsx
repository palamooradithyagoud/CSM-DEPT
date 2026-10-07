import React, { useState } from 'react';
import { Mail, Phone, BookOpen, Search, X, User } from 'lucide-react';

export default function FacultySection({ faculty = [] }) {
  const [selectedFilter, setSelectedFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeModalMember, setActiveModalMember] = useState(null);

  const filterOptions = [
    { label: 'All Faculty', value: 'ALL' },
    { label: 'Professors', value: 'Professor' },
    { label: 'Associate Professors', value: 'Associate' },
    { label: 'Assistant Professors', value: 'Assistant' },
  ];

  const filteredFaculty = faculty.filter((member) => {
    const matchesFilter =
      selectedFilter === 'ALL' ||
      member.designation.toLowerCase().includes(selectedFilter.toLowerCase());

    const matchesSearch =
      searchQuery === '' ||
      member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.specialization.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.qualification.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesFilter && matchesSearch;
  });

  return (
    <section id="faculty" className="section-padding faculty-root">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-subtitle">Academic Mentorship & Research</span>
          <h2 className="section-title">Faculty Directory</h2>
          <p className="section-desc">
            Distinguished academicians, doctoral supervisors, and industry practitioners dedicated to student academic progression.
          </p>
        </div>

        {/* Filter & Search Bar */}
        <div className="faculty-controls-bar">
          <div className="filter-pill-group">
            {filterOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setSelectedFilter(opt.value)}
                className={`filter-pill ${selectedFilter === opt.value ? 'active' : ''}`}
              >
                {opt.label}
              </button>
            ))}
          </div>

          <div className="faculty-search-box">
            <Search size={16} className="search-icon" />
            <input
              type="text"
              placeholder="Search by name, AI, IoT, Security..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="clear-search-btn">
                <X size={14} />
              </button>
            )}
          </div>
        </div>

        {/* Faculty Grid */}
        {filteredFaculty.length > 0 ? (
          <div className="faculty-grid">
            {filteredFaculty.map((member) => (
              <div
                key={member.id}
                className="faculty-card"
                onClick={() => setActiveModalMember(member)}
              >
                <div className="faculty-card-header">
                  <div className="faculty-avatar-circle">
                    {member.name.split(' ').map((n) => n[0]).slice(0, 2).join('')}
                  </div>
                  <div className="faculty-title-block">
                    <h3 className="faculty-name">{member.name}</h3>
                    <span className="faculty-designation">{member.designation}</span>
                  </div>
                </div>

                <div className="faculty-qual-badge">
                  <span>{member.qualification}</span>
                </div>

                <div className="faculty-spec-block">
                  <span className="spec-label">Specialization:</span>
                  <span className="spec-text">{member.specialization}</span>
                </div>

                <div className="faculty-card-footer">
                  <div className="faculty-contact-pill">
                    <Mail size={13} />
                    <span>{member.email}</span>
                  </div>
                  <span className="faculty-exp-tag">{member.experienceYears}y exp</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-results-box">
            <p>No faculty members match your filter criteria.</p>
          </div>
        )}
      </div>

      {/* Faculty Modal */}
      {activeModalMember && (
        <div className="modal-backdrop" onClick={() => setActiveModalMember(null)}>
          <div className="faculty-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-top">
              <div className="modal-header-info">
                <h3 className="modal-faculty-name">{activeModalMember.name}</h3>
                <span className="modal-faculty-role">{activeModalMember.designation}</span>
              </div>
              <button onClick={() => setActiveModalMember(null)} className="modal-close-btn">
                <X size={20} />
              </button>
            </div>

            <div className="modal-body-content">
              <div className="modal-detail-row">
                <span className="detail-label">Qualifications:</span>
                <span className="detail-value">{activeModalMember.qualification}</span>
              </div>
              <div className="modal-detail-row">
                <span className="detail-label">Academic Experience:</span>
                <span className="detail-value">{activeModalMember.experienceYears} Years</span>
              </div>
              <div className="modal-detail-row">
                <span className="detail-label">Research Specialization:</span>
                <span className="detail-value">{activeModalMember.specialization}</span>
              </div>
              <div className="modal-detail-row">
                <span className="detail-label">Official Email:</span>
                <a href={`mailto:${activeModalMember.email}`} className="modal-link">
                  {activeModalMember.email}
                </a>
              </div>
              {activeModalMember.phone && (
                <div className="modal-detail-row">
                  <span className="detail-label">Office Intercom:</span>
                  <span className="detail-value">{activeModalMember.phone}</span>
                </div>
              )}
              {activeModalMember.bio && (
                <div className="modal-bio-block">
                  <span className="detail-label">Academic Profile & Focus:</span>
                  <p className="bio-text">{activeModalMember.bio}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <style>{`
        .faculty-root {
          background-color: var(--color-background);
          border-bottom: 1px solid var(--color-border);
        }
        .faculty-controls-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: var(--space-md);
          margin-bottom: var(--space-2xl);
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: 12px 18px;
        }
        .filter-pill-group {
          display: flex;
          align-items: center;
          gap: 6px;
          flex-wrap: wrap;
        }
        .filter-pill {
          padding: 6px 14px;
          font-size: 0.8125rem;
          font-weight: 500;
          color: var(--color-text-secondary);
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          transition: all var(--transition-fast);
        }
        .filter-pill:hover {
          color: var(--color-text-main);
          border-color: #3b3b42;
        }
        .filter-pill.active {
          color: #050506;
          background: var(--color-primary);
          border-color: var(--color-primary);
          font-weight: 600;
        }
        .faculty-search-box {
          position: relative;
          display: flex;
          align-items: center;
          min-width: 280px;
        }
        .search-icon {
          position: absolute;
          left: 12px;
          color: var(--color-text-muted);
        }
        .search-input {
          width: 100%;
          padding-left: 36px;
          padding-right: 32px;
          padding-top: 8px;
          padding-bottom: 8px;
          font-size: 0.875rem;
        }
        .clear-search-btn {
          position: absolute;
          right: 10px;
          color: var(--color-text-muted);
          padding: 2px;
        }
        .faculty-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: var(--space-lg);
        }
        .faculty-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-lg);
          display: flex;
          flex-direction: column;
          cursor: pointer;
          transition: border-color var(--transition-base), transform var(--transition-base);
        }
        .faculty-card:hover {
          border-color: #383840;
          transform: translateY(-2px);
        }
        .faculty-card-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: var(--space-md);
        }
        .faculty-avatar-circle {
          width: 44px;
          height: 44px;
          border-radius: 50%;
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 0.875rem;
          color: var(--color-primary);
          flex-shrink: 0;
        }
        .faculty-title-block {
          overflow: hidden;
        }
        .faculty-name {
          font-size: 0.9375rem;
          font-weight: 700;
          color: var(--color-text-main);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .faculty-designation {
          display: block;
          font-size: 0.75rem;
          color: var(--color-primary);
          font-weight: 500;
        }
        .faculty-qual-badge {
          margin-bottom: var(--space-sm);
        }
        .faculty-qual-badge span {
          display: inline-block;
          font-size: 0.75rem;
          color: var(--color-text-muted);
          background: var(--color-secondary);
          padding: 2px 8px;
          border-radius: var(--radius-sm);
          border: 1px solid var(--color-border-subtle);
        }
        .faculty-spec-block {
          margin-bottom: var(--space-md);
          flex-grow: 1;
        }
        .spec-label {
          display: block;
          font-size: 0.6875rem;
          color: var(--color-text-muted);
          text-transform: uppercase;
          letter-spacing: 0.04em;
          margin-bottom: 2px;
        }
        .spec-text {
          font-size: 0.8125rem;
          color: var(--color-text-secondary);
          line-height: 1.4;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        .faculty-card-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-top: var(--space-sm);
          border-top: 1px solid var(--color-border-subtle);
        }
        .faculty-contact-pill {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.75rem;
          color: var(--color-text-muted);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .faculty-exp-tag {
          font-size: 0.6875rem;
          font-weight: 600;
          color: var(--color-text-secondary);
          background: var(--color-secondary);
          padding: 2px 6px;
          border-radius: var(--radius-sm);
        }
        .no-results-box {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          padding: var(--space-2xl);
          text-align: center;
          color: var(--color-text-muted);
        }
        /* Modal Styles */
        .modal-backdrop {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.75);
          backdrop-filter: blur(8px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 200;
          padding: var(--space-md);
        }
        .faculty-modal {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          max-width: 520px;
          width: 100%;
          padding: var(--space-xl);
          box-shadow: var(--shadow-elevated);
        }
        .modal-top {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          border-bottom: 1px solid var(--color-border);
          padding-bottom: var(--space-md);
          margin-bottom: var(--space-md);
        }
        .modal-faculty-name {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--color-text-main);
        }
        .modal-faculty-role {
          font-size: 0.8125rem;
          color: var(--color-primary);
          font-weight: 600;
        }
        .modal-close-btn {
          color: var(--color-text-muted);
          padding: 4px;
        }
        .modal-close-btn:hover {
          color: var(--color-text-main);
        }
        .modal-body-content {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .modal-detail-row {
          display: flex;
          justify-content: space-between;
          font-size: 0.875rem;
          border-bottom: 1px solid var(--color-border-subtle);
          padding-bottom: 8px;
        }
        .detail-label {
          color: var(--color-text-muted);
          font-weight: 500;
        }
        .detail-value {
          color: var(--color-text-main);
          font-weight: 500;
          text-align: right;
        }
        .modal-link {
          color: var(--color-primary);
        }
        .modal-bio-block {
          margin-top: 8px;
        }
        .bio-text {
          font-size: 0.875rem;
          color: var(--color-text-secondary);
          line-height: 1.6;
          margin-top: 6px;
        }
        @media (max-width: 1100px) {
          .faculty-grid {
            grid-template-columns: repeat(3, 1fr);
          }
        }
        @media (max-width: 780px) {
          .faculty-grid {
            grid-template-columns: repeat(2, 1fr);
          }
          .faculty-controls-bar {
            flex-direction: column;
            align-items: stretch;
          }
          .faculty-search-box {
            width: 100%;
          }
        }
        @media (max-width: 500px) {
          .faculty-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
