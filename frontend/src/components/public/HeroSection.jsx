import React from 'react';
import { ArrowRight, Shield, Award, Users, Cpu, FileText } from 'lucide-react';

export default function HeroSection({ department, stats, onOpenLogin }) {
  return (
    <section id="overview" className="hero-root">
      <div className="container hero-container">
        {/* Accreditation Pill */}
        <div className="hero-eyebrow">
          <span className="eyebrow-dot"></span>
          <span>Approved by AICTE • NBA Accredited (Tier-I) • Autonomous Institution</span>
        </div>

        {/* Main Headline */}
        <h1 className="hero-title">
          Department of <br />
          <span className="hero-title-accent">Computer Science & Engineering</span>
        </h1>

        {/* Subtitle / Tagline */}
        <p className="hero-tagline">
          {department?.tagline || "Fostering Academic Rigor, Advanced Systems Research & Technological Innovation"}
        </p>

        {/* Action Group */}
        <div className="hero-actions">
          <a href="#faculty" className="btn btn-primary">
            <span>Explore Faculty</span>
            <ArrowRight size={16} />
          </a>
          <a href="#announcements" className="btn btn-secondary">
            <FileText size={16} />
            <span>Academic Circulars</span>
          </a>
          <button onClick={onOpenLogin} className="btn btn-secondary hero-hod-btn">
            <Shield size={16} className="shield-icon" />
            <span>HOD Academic Portal</span>
          </button>
        </div>

        {/* Quantitative Highlights Strip (Zero student private marks) */}
        <div className="hero-stats-grid">
          <div className="stat-card">
            <div className="stat-header">
              <Users size={18} className="stat-icon" />
              <span className="stat-num">{stats?.facultyCount || 8}+</span>
            </div>
            <span className="stat-label">Distinguished Faculty</span>
            <span className="stat-sub">Ph.D. & Industry Specialists</span>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <Cpu size={18} className="stat-icon" />
              <span className="stat-num">{stats?.specializedLabs || 8}</span>
            </div>
            <span className="stat-label">Specialized Labs</span>
            <span className="stat-sub">AI, IoT, Cloud & Security Clusters</span>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <Award size={18} className="stat-icon" />
              <span className="stat-num">A++</span>
            </div>
            <span className="stat-label">NAAC Grade</span>
            <span className="stat-sub">Highest Collegiate Rating</span>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <Users size={18} className="stat-icon" />
              <span className="stat-num">{stats?.studentIntake || 180}</span>
            </div>
            <span className="stat-label">UG Cohort Intake</span>
            <span className="stat-sub">Outcome-based Curriculum</span>
          </div>
        </div>
      </div>

      <style>{`
        .hero-root {
          padding-top: var(--space-3xl);
          padding-bottom: var(--space-3xl);
          position: relative;
          border-bottom: 1px solid var(--color-border);
          background: radial-gradient(circle at 50% 0%, rgba(24, 24, 28, 0.4) 0%, rgba(5, 5, 6, 0.95) 70%);
        }
        .hero-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
        }
        .hero-eyebrow {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 6px 14px;
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-full);
          font-size: 0.8125rem;
          color: var(--color-text-secondary);
          margin-bottom: var(--space-lg);
        }
        .eyebrow-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--color-primary);
        }
        .hero-title {
          font-size: 3.25rem;
          font-weight: 800;
          color: var(--color-text-main);
          letter-spacing: -0.03em;
          line-height: 1.15;
          margin-bottom: var(--space-lg);
        }
        .hero-title-accent {
          color: #ffffff;
          position: relative;
        }
        .hero-tagline {
          font-size: 1.1875rem;
          color: var(--color-text-secondary);
          max-width: 65ch;
          line-height: 1.6;
          margin-bottom: var(--space-2xl);
        }
        .hero-actions {
          display: flex;
          align-items: center;
          gap: 14px;
          flex-wrap: wrap;
          justify-content: center;
          margin-bottom: var(--space-3xl);
        }
        .hero-hod-btn {
          border-color: #2b2b32;
        }
        .hero-hod-btn:hover {
          border-color: var(--color-primary-border);
        }
        .shield-icon {
          color: var(--color-primary);
        }
        .hero-stats-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: var(--space-lg);
          width: 100%;
        }
        .stat-card {
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: var(--space-lg) var(--space-md);
          text-align: left;
          transition: border-color var(--transition-base), transform var(--transition-base);
        }
        .stat-card:hover {
          border-color: #33333a;
          transform: translateY(-2px);
        }
        .stat-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: var(--space-xs);
        }
        .stat-icon {
          color: var(--color-text-muted);
        }
        .stat-num {
          font-family: var(--font-display);
          font-size: 1.75rem;
          font-weight: 700;
          color: var(--color-text-main);
          letter-spacing: -0.02em;
        }
        .stat-label {
          display: block;
          font-size: 0.9375rem;
          font-weight: 600;
          color: var(--color-text-main);
        }
        .stat-sub {
          display: block;
          font-size: 0.75rem;
          color: var(--color-text-muted);
          margin-top: 2px;
        }
        @media (max-width: 900px) {
          .hero-title {
            font-size: 2.25rem;
          }
          .hero-stats-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
        @media (max-width: 540px) {
          .hero-stats-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </section>
  );
}
