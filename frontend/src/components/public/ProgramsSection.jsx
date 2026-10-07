import React, { useState } from 'react';
import { GraduationCap, Clock, Users, ArrowUpRight, CheckCircle2, ChevronRight } from 'lucide-react';

export default function ProgramsSection({ programs = [] }) {
  const [activeProgramId, setActiveProgramId] = useState(programs[0]?.id || 'btech-cse');

  // Fallback demo programs if API hasn't loaded yet
  const defaultPrograms = [
    {
      id: 'btech-cse',
      name: 'B.Tech in Computer Science & Engineering',
      code: 'UG-CSE',
      degree: 'Bachelor of Technology',
      duration: '4 Years (8 Semesters)',
      intake: 180,
      overview: 'Comprehensive undergraduate program covering foundational computing theory, algorithm design, systems software, and modern application development.',
      coreTracks: [
        'Data Structures & Algorithms',
        'Operating Systems & Architecture',
        'Database Management Systems',
        'Computer Networks & Security',
        'Full-Stack Web & Cloud Systems'
      ],
      careerDirections: [
        'Software Development Engineer',
        'Systems Architect',
        'Cloud Solutions Engineer',
        'Research & Higher Studies'
      ]
    },
    {
      id: 'btech-cse-aiml',
      name: 'B.Tech in CSE (Artificial Intelligence & Machine Learning)',
      code: 'UG-AIML',
      degree: 'Bachelor of Technology',
      duration: '4 Years (8 Semesters)',
      intake: 60,
      overview: 'Specialized curriculum combining core computer science fundamentals with neural networks, deep learning, computer vision, and cognitive computing.',
      coreTracks: [
        'Mathematics for Machine Learning',
        'Deep Learning & Neural Architectures',
        'Natural Language Processing',
        'Computer Vision & Robotics',
        'MLOps & Scalable Inference'
      ],
      careerDirections: [
        'AI/ML Engineer',
        'Data Scientist',
        'Computer Vision Specialist',
        'Applied Research Scientist'
      ]
    },
    {
      id: 'mtech-cse',
      name: 'M.Tech in Computer Science & Engineering',
      code: 'PG-CSE',
      degree: 'Master of Technology',
      duration: '2 Years (4 Semesters)',
      intake: 24,
      overview: 'Postgraduate program focused on advanced research methodologies, distributed high-performance computing, and cybersecurity paradigms.',
      coreTracks: [
        'Advanced Distributed Systems',
        'Cryptographic Protocols & Blockchain',
        'Big Data Analytics & Streaming',
        'Doctoral Dissertation Research'
      ],
      careerDirections: [
        'Principal Research Engineer',
        'Technical Architect',
        'Doctoral Researcher',
        'Engineering Leadership'
      ]
    },
    {
      id: 'phd-cse',
      name: 'Ph.D. in Computer Science & Engineering',
      code: 'DOC-CSE',
      degree: 'Doctor of Philosophy',
      duration: '3 to 5 Years',
      intake: 10,
      overview: 'Rigorous doctoral research program under distinguished faculty guidance in AI, Network Security, Big Data, and Distributed Computing.',
      coreTracks: [
        'Machine Learning & Edge Intelligence',
        'Wireless Sensor Networks & IoT',
        'Cloud Security & Fault Tolerance',
        'Bioinformatics & Computational Biology'
      ],
      careerDirections: [
        'University Professor',
        'Industrial R&D Director',
        'Principal Scientist'
      ]
    }
  ];

  const displayPrograms = programs.length > 0 ? programs : defaultPrograms;
  const currentProgram = displayPrograms.find((p) => p.id === activeProgramId) || displayPrograms[0];

  return (
    <section id="programs" className="section-padding programs-root">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-subtitle">Academic Offerings & Curricula</span>
          <h2 className="section-title">Academic Programs & Degrees</h2>
          <p className="section-desc">
            Outcome-based undergraduate and postgraduate degree programs designed to blend theoretical rigor with real-world engineering mastery.
          </p>
        </div>

        {/* Programs Interactive Showcase */}
        <div className="programs-layout">
          {/* Left Column: Program Selectors */}
          <div className="programs-tabs-list">
            {displayPrograms.map((prog) => {
              const isSelected = prog.id === currentProgram?.id;
              return (
                <button
                  key={prog.id}
                  onClick={() => setActiveProgramId(prog.id)}
                  className={`prog-tab-card ${isSelected ? 'active' : ''}`}
                >
                  <div className="tab-left">
                    <span className="tab-code-badge">{prog.code}</span>
                    <div className="tab-text">
                      <h3 className="tab-prog-name">{prog.name}</h3>
                      <span className="tab-degree-level">{prog.degree} • {prog.duration}</span>
                    </div>
                  </div>
                  <ChevronRight size={18} className={`tab-chevron ${isSelected ? 'active' : ''}`} />
                </button>
              );
            })}
          </div>

          {/* Right Column: Detailed Program Profile */}
          {currentProgram && (
            <div className="program-detail-panel">
              <div className="panel-header">
                <div>
                  <div className="badge-row">
                    <span className="badge badge-success">{currentProgram.degree}</span>
                    <span className="badge badge-neutral">{currentProgram.code}</span>
                  </div>
                  <h3 className="panel-title">{currentProgram.name}</h3>
                </div>

                <div className="panel-meta-chips">
                  <div className="meta-chip">
                    <Clock size={15} />
                    <span>{currentProgram.duration}</span>
                  </div>
                  <div className="meta-chip">
                    <Users size={15} />
                    <span>Annual Intake: {currentProgram.intake}</span>
                  </div>
                </div>
              </div>

              <div className="panel-body">
                <div className="overview-block">
                  <h4 className="block-heading">Curriculum Overview</h4>
                  <p className="overview-text">{currentProgram.overview}</p>
                </div>

                <div className="tracks-grid">
                  <div className="track-col">
                    <h4 className="block-heading">Core Academic Tracks</h4>
                    <ul className="track-list">
                      {currentProgram.coreTracks.map((track, idx) => (
                        <li key={idx} className="track-item">
                          <CheckCircle2 size={15} className="track-icon" />
                          <span>{track}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="track-col">
                    <h4 className="block-heading">Graduate Career Directions</h4>
                    <ul className="track-list">
                      {currentProgram.careerDirections.map((career, idx) => (
                        <li key={idx} className="track-item">
                          <ArrowUpRight size={15} className="career-icon" />
                          <span>{career}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="panel-footer-note">
                  <span>Curriculum aligned with AICTE Model Guidelines & Washington Accord OBE Benchmarks.</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .programs-root {
          background-color: var(--color-background);
          border-bottom: 1px solid var(--color-border);
        }
        .programs-layout {
          display: grid;
          grid-template-columns: 380px 1fr;
          gap: var(--space-xl);
        }
        .programs-tabs-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .prog-tab-card {
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: 16px 18px;
          text-align: left;
          transition: all var(--transition-fast);
        }
        .prog-tab-card:hover {
          border-color: #383842;
          background: var(--color-card-hover);
        }
        .prog-tab-card.active {
          border-color: var(--color-primary-border);
          background: var(--color-secondary);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        }
        .tab-left {
          display: flex;
          align-items: center;
          gap: 14px;
        }
        .tab-code-badge {
          font-size: 0.6875rem;
          font-weight: 700;
          color: var(--color-primary);
          background: var(--color-primary-subtle);
          padding: 4px 8px;
          border-radius: var(--radius-sm);
          flex-shrink: 0;
        }
        .tab-text {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        .tab-prog-name {
          font-size: 0.9375rem;
          font-weight: 700;
          color: var(--color-text-main);
          line-height: 1.3;
        }
        .tab-degree-level {
          font-size: 0.75rem;
          color: var(--color-text-muted);
        }
        .tab-chevron {
          color: var(--color-text-muted);
          transition: transform var(--transition-fast);
        }
        .tab-chevron.active {
          color: var(--color-primary);
          transform: translateX(3px);
        }
        /* Right Detail Panel */
        .program-detail-panel {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-2xl);
          display: flex;
          flex-direction: column;
        }
        .panel-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          border-bottom: 1px solid var(--color-border);
          padding-bottom: var(--space-lg);
          margin-bottom: var(--space-lg);
          flex-wrap: wrap;
          gap: 16px;
        }
        .badge-row {
          display: flex;
          gap: 8px;
          margin-bottom: var(--space-xs);
        }
        .panel-title {
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--color-text-main);
          letter-spacing: -0.02em;
        }
        .panel-meta-chips {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
        }
        .meta-chip {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.8125rem;
          color: var(--color-text-secondary);
          background: var(--color-secondary);
          padding: 6px 12px;
          border-radius: var(--radius-md);
          border: 1px solid var(--color-border);
        }
        .overview-block {
          margin-bottom: var(--space-xl);
        }
        .block-heading {
          font-size: 0.9375rem;
          font-weight: 700;
          color: var(--color-text-main);
          margin-bottom: var(--space-sm);
          text-transform: uppercase;
          letter-spacing: 0.03em;
        }
        .overview-text {
          font-size: 0.9375rem;
          color: var(--color-text-secondary);
          line-height: 1.7;
          max-width: 100%;
        }
        .tracks-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: var(--space-xl);
          margin-bottom: var(--space-xl);
        }
        .track-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .track-item {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          font-size: 0.875rem;
          color: var(--color-text-secondary);
        }
        .track-icon {
          color: var(--color-primary);
          flex-shrink: 0;
          margin-top: 3px;
        }
        .career-icon {
          color: var(--color-text-muted);
          flex-shrink: 0;
          margin-top: 3px;
        }
        .panel-footer-note {
          padding-top: var(--space-md);
          border-top: 1px solid var(--color-border-subtle);
          font-size: 0.75rem;
          color: var(--color-text-muted);
          font-style: italic;
        }
        @media (max-width: 960px) {
          .programs-layout {
            grid-template-columns: 1fr;
          }
        }
        @media (max-width: 600px) {
          .tracks-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
