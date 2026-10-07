import React, { useState, useEffect, useRef } from 'react';
import {
  ChevronDown,
  ArrowRight,
  Shield,
  LogOut,
  LayoutDashboard,
  Menu,
  X,
  BookOpen,
  Users,
  Award,
  Calendar,
  Building,
  Bell,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function PublicNavbar({ onOpenLogin, onGoToDashboard }) {
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState(null);
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setActiveDropdown(null);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const navMenus = [
    {
      id: 'department',
      label: 'Department',
      items: [
        { label: 'Overview & Vision', href: '#overview', desc: 'Core academic identity & mission' },
        { label: 'About Department & HOD', href: '#about', desc: 'Address from Dr. M. A. Jabbar' },
        { label: 'Academic Programs & Degrees', href: '#programs', desc: 'B.Tech, M.Tech & Ph.D. pathways' },
        { label: 'Infrastructure & Labs', href: '#contact', desc: 'Specialized computing clusters' },
      ],
    },
    {
      id: 'faculty',
      label: 'Faculty',
      items: [
        { label: 'Faculty Directory', href: '#faculty', desc: 'Professors & research supervisors' },
        { label: 'Research Specializations', href: '#faculty', desc: 'AI, IoT, Cloud & Security mentors' },
        { label: 'Year Coordinators', href: '#contact', desc: '2nd, 3rd & 4th Year counselors' },
      ],
    },
    {
      id: 'activities',
      label: 'Activities',
      items: [
        { label: 'Conferences & Events', href: '#events', desc: 'National symposiums & FDPs' },
        { label: 'Student Achievements', href: '#achievements', desc: 'National hackathon awards & citations' },
        { label: 'Department Gallery', href: '#gallery', desc: 'Photographic archive of moments' },
      ],
    },
  ];

  const handleDropdownToggle = (id) => {
    setActiveDropdown((prev) => (prev === id ? null : id));
  };

  const handleLinkClick = () => {
    setActiveDropdown(null);
    setMobileMenuOpen(false);
  };

  return (
    <div className="navbar-wrapper">
      <header className="capsule-navbar" ref={dropdownRef}>
        {/* Brand Logo - Stylized 'cse.' matching 'st.' pill style */}
        <a href="#overview" className="capsule-brand" onClick={handleLinkClick}>
          <div className="brand-logo-mark">
            <span className="logo-main">cse</span>
            <span className="logo-dot">.</span>
          </div>
          <div className="brand-label-box">
            <span className="brand-dept-name">Department of CSE</span>
            <span className="brand-sub-tag">Academic Portal</span>
          </div>
        </a>

        {/* Center Navigation Links with Dropdown Chevrons */}
        <nav className="capsule-nav-items">
          {navMenus.map((menu) => {
            const isOpen = activeDropdown === menu.id;
            return (
              <div
                key={menu.id}
                className="capsule-nav-item"
                onMouseEnter={() => setActiveDropdown(menu.id)}
                onMouseLeave={() => setActiveDropdown(null)}
              >
                <button
                  type="button"
                  className={`capsule-nav-trigger ${isOpen ? 'active' : ''}`}
                  onClick={() => handleDropdownToggle(menu.id)}
                  aria-expanded={isOpen}
                >
                  <span>{menu.label}</span>
                  <ChevronDown size={14} className={`chevron-icon ${isOpen ? 'open' : ''}`} />
                </button>

                {/* Dropdown Menu Flyout */}
                {isOpen && (
                  <div className="capsule-dropdown-flyout">
                    <div className="flyout-inner">
                      {menu.items.map((item, idx) => (
                        <a
                          key={idx}
                          href={item.href}
                          className="flyout-link"
                          onClick={handleLinkClick}
                        >
                          <span className="flyout-link-title">{item.label}</span>
                          <span className="flyout-link-desc">{item.desc}</span>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}

          {/* Direct Nav Links */}
          <a href="#programs" className="capsule-nav-link" onClick={handleLinkClick}>
            <span>Programs</span>
          </a>
          <a href="#news" className="capsule-nav-link" onClick={handleLinkClick}>
            <span>News</span>
          </a>
          <a href="#gallery" className="capsule-nav-link" onClick={handleLinkClick}>
            <span>Gallery</span>
          </a>
          <a href="#announcements" className="capsule-nav-link" onClick={handleLinkClick}>
            <span>Circulars</span>
          </a>
          <a href="#contact" className="capsule-nav-link" onClick={handleLinkClick}>
            <span>Contact</span>
          </a>
        </nav>

        {/* Right Action Button - Matching Rounded Pill CTA */}
        <div className="capsule-cta-group">
          {isAuthenticated ? (
            <div className="logged-in-controls">
              <button
                onClick={onGoToDashboard}
                className="capsule-pill-btn"
                title="Enter HOD Academic Intelligence Workspace"
              >
                <span>HOD Workspace</span>
                <span className="cta-icon-circle">
                  <LayoutDashboard size={13} />
                </span>
              </button>
              <button
                onClick={logout}
                className="logout-mini-btn"
                title="Sign Out"
                aria-label="Sign Out"
              >
                <LogOut size={14} />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenLogin}
              className="capsule-pill-btn"
              title="Access HOD Management System"
            >
              <span>HOD Portal</span>
              <span className="cta-icon-circle">
                <ArrowRight size={13} />
              </span>
            </button>
          )}

          {/* Mobile Menu Toggle Button */}
          <button
            className="capsule-mobile-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </header>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="mobile-capsule-drawer">
          <div className="mobile-drawer-content">
            <div className="mobile-section-group">
              <span className="mobile-group-title">Navigation</span>
              <a href="#overview" className="mobile-item-link" onClick={handleLinkClick}>Overview</a>
              <a href="#about" className="mobile-item-link" onClick={handleLinkClick}>About Department & HOD</a>
              <a href="#faculty" className="mobile-item-link" onClick={handleLinkClick}>Faculty Directory</a>
              <a href="#events" className="mobile-item-link" onClick={handleLinkClick}>Conferences & Hackathons</a>
              <a href="#achievements" className="mobile-item-link" onClick={handleLinkClick}>Student Achievements</a>
              <a href="#announcements" className="mobile-item-link" onClick={handleLinkClick}>Official Circulars</a>
              <a href="#contact" className="mobile-item-link" onClick={handleLinkClick}>Contact & Secretariat</a>
            </div>

            <div className="mobile-cta-wrap">
              {isAuthenticated ? (
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onGoToDashboard();
                  }}
                  className="capsule-pill-btn w-full"
                >
                  <span>Enter HOD Workspace</span>
                  <span className="cta-icon-circle"><LayoutDashboard size={13} /></span>
                </button>
              ) : (
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onOpenLogin();
                  }}
                  className="capsule-pill-btn w-full"
                >
                  <span>HOD Portal Login</span>
                  <span className="cta-icon-circle"><ArrowRight size={13} /></span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      <style>{`
        .navbar-wrapper {
          position: sticky;
          top: 14px;
          z-index: 200;
          display: flex;
          justify-content: center;
          padding: 0 16px;
          pointer-events: none; /* Allows clicks around the pill */
        }

        .capsule-navbar {
          pointer-events: auto; /* Re-enables clicks inside pill */
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: rgba(15, 15, 17, 0.94);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid var(--color-border);
          border-radius: 9999px;
          padding: 6px 8px 6px 20px;
          width: 100%;
          max-width: 1140px;
          height: 60px;
          box-shadow: 0 12px 36px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(255, 255, 255, 0.04);
          transition: all var(--transition-base);
        }

        .capsule-navbar:hover {
          border-color: #2e2e34;
          box-shadow: 0 16px 42px rgba(0, 0, 0, 0.75), 0 0 0 1px rgba(50, 220, 92, 0.15);
        }

        /* Brand Logo: Stylized 'cse.' like the reference image 'st.' */
        .capsule-brand {
          display: flex;
          align-items: center;
          gap: 10px;
          text-decoration: none;
          flex-shrink: 0;
        }

        .brand-logo-mark {
          display: flex;
          align-items: baseline;
          line-height: 1;
        }

        .logo-main {
          font-family: var(--font-display);
          font-size: 1.55rem;
          font-weight: 800;
          color: #ffffff;
          letter-spacing: -0.04em;
        }

        .logo-dot {
          font-family: var(--font-display);
          font-size: 1.7rem;
          font-weight: 900;
          color: var(--color-primary); /* Primary #32DC5C accent dot */
          margin-left: 1px;
        }

        .brand-label-box {
          display: flex;
          flex-direction: column;
          line-height: 1.15;
          padding-left: 2px;
          border-left: 1px solid var(--color-border-subtle);
          margin-left: 2px;
        }

        .brand-dept-name {
          font-size: 0.785rem;
          font-weight: 700;
          color: var(--color-text-main);
          letter-spacing: -0.01em;
        }

        .brand-sub-tag {
          font-size: 0.65rem;
          color: var(--color-text-muted);
          font-weight: 500;
        }

        /* Center Nav Links with Dropdown Chevrons */
        .capsule-nav-items {
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .capsule-nav-item {
          position: relative;
        }

        .capsule-nav-trigger {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 8px 14px;
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--color-text-secondary);
          border-radius: 9999px;
          transition: all var(--transition-fast);
          background: transparent;
        }

        .capsule-nav-trigger:hover,
        .capsule-nav-trigger.active {
          color: #ffffff;
          background: var(--color-accent);
        }

        .capsule-nav-link {
          padding: 8px 14px;
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--color-text-secondary);
          border-radius: 9999px;
          transition: all var(--transition-fast);
        }

        .capsule-nav-link:hover {
          color: #ffffff;
          background: var(--color-accent);
        }

        .chevron-icon {
          color: var(--color-text-muted);
          transition: transform var(--transition-fast);
        }

        .chevron-icon.open {
          transform: rotate(180deg);
          color: var(--color-primary);
        }

        /* Dropdown Flyout */
        .capsule-dropdown-flyout {
          position: absolute;
          top: calc(100% + 12px);
          left: 50%;
          transform: translateX(-50%);
          width: 260px;
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          box-shadow: 0 16px 36px rgba(0, 0, 0, 0.7);
          padding: 8px;
          z-index: 210;
          animation: flyoutFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes flyoutFadeIn {
          from {
            opacity: 0;
            transform: translate(-50%, -6px);
          }
          to {
            opacity: 1;
            transform: translate(-50%, 0);
          }
        }

        .flyout-inner {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .flyout-link {
          display: flex;
          flex-direction: column;
          gap: 2px;
          padding: 8px 12px;
          border-radius: var(--radius-md);
          transition: background-color var(--transition-fast);
        }

        .flyout-link:hover {
          background-color: var(--color-accent);
        }

        .flyout-link-title {
          font-size: 0.845rem;
          font-weight: 600;
          color: var(--color-text-main);
        }

        .flyout-link-desc {
          font-size: 0.725rem;
          color: var(--color-text-muted);
        }

        /* Right Pill CTA - Matches the 'Contact Us >' button in the reference */
        .capsule-cta-group {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .capsule-pill-btn {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          background: var(--color-primary); /* #32DC5C primary green */
          color: #050506; /* Solid dark text for maximum contrast */
          font-family: var(--font-sans);
          font-size: 0.875rem;
          font-weight: 700;
          padding: 8px 10px 8px 18px;
          border-radius: 9999px;
          letter-spacing: -0.01em;
          transition: all var(--transition-base);
          box-shadow: 0 4px 14px rgba(50, 220, 92, 0.25);
          cursor: pointer;
        }

        .capsule-pill-btn:hover {
          background: var(--color-primary-hover);
          transform: translateY(-1px);
          box-shadow: 0 6px 18px rgba(50, 220, 92, 0.38);
        }

        .cta-icon-circle {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 26px;
          height: 26px;
          border-radius: 50%;
          background: rgba(5, 5, 6, 0.85);
          color: #ffffff;
          transition: transform var(--transition-fast);
        }

        .capsule-pill-btn:hover .cta-icon-circle {
          transform: translateX(2px);
          background: #050506;
          color: var(--color-primary);
        }

        .logged-in-controls {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .logout-mini-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          color: var(--color-text-secondary);
          transition: all var(--transition-fast);
        }

        .logout-mini-btn:hover {
          color: var(--color-destructive);
          border-color: var(--color-destructive-border);
          background: var(--color-destructive-subtle);
        }

        .capsule-mobile-toggle {
          display: none;
          align-items: center;
          justify-content: center;
          width: 38px;
          height: 38px;
          border-radius: 50%;
          background: var(--color-secondary);
          border: 1px solid var(--color-border);
          color: var(--color-text-main);
          margin-left: 6px;
        }

        /* Mobile Drawer */
        .mobile-capsule-drawer {
          pointer-events: auto;
          position: absolute;
          top: 76px;
          left: 16px;
          right: 16px;
          background: var(--color-card);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: 20px;
          box-shadow: var(--shadow-elevated);
          z-index: 190;
        }

        .mobile-drawer-content {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .mobile-section-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .mobile-group-title {
          font-size: 0.6875rem;
          font-weight: 700;
          color: var(--color-text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 4px;
        }

        .mobile-item-link {
          font-size: 0.9375rem;
          color: var(--color-text-secondary);
          padding: 6px 0;
          border-bottom: 1px solid var(--color-border-subtle);
        }

        .mobile-item-link:hover {
          color: var(--color-primary);
        }

        .mobile-cta-wrap {
          margin-top: 8px;
        }

        .w-full {
          width: 100%;
          justify-content: center;
        }

        /* Responsive Breakpoints */
        @media (max-width: 980px) {
          .capsule-nav-items {
            display: none;
          }
          .capsule-mobile-toggle {
            display: flex;
          }
        }

        @media (max-width: 600px) {
          .capsule-navbar {
            padding: 6px 8px 6px 14px;
            height: 54px;
          }
          .brand-label-box {
            display: none;
          }
          .capsule-pill-btn {
            font-size: 0.8125rem;
            padding: 6px 8px 6px 14px;
          }
          .cta-icon-circle {
            width: 22px;
            height: 22px;
          }
        }
      `}</style>
    </div>
  );
}
