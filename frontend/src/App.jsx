import React, { useState, useEffect } from 'react';
import { useAuth } from './context/AuthContext';
import { api } from './services/api';
import PublicNavbar from './components/layout/PublicNavbar';
import PublicFooter from './components/layout/PublicFooter';
import HeroSection from './components/public/HeroSection';
import AboutSection from './components/public/AboutSection';
import ProgramsSection from './components/public/ProgramsSection';
import FacultySection from './components/public/FacultySection';
import EventsSection from './components/public/EventsSection';
import AchievementsSection from './components/public/AchievementsSection';
import NewsSection from './components/public/NewsSection';
import GallerySection from './components/public/GallerySection';
import AnnouncementsSection from './components/public/AnnouncementsSection';
import ContactSection from './components/public/ContactSection';
import LoginModal from './components/auth/LoginModal';
import HodDashboard from './components/admin/HodDashboard';
import { Loader2 } from 'lucide-react';


export default function App() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [currentView, setCurrentView] = useState('public'); // 'public' | 'admin'
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  // Department public state
  const [department, setDepartment] = useState(null);
  const [faculty, setFaculty] = useState([]);
  const [events, setEvents] = useState([]);
  const [achievements, setAchievements] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [gallery, setGallery] = useState([]);
  const [news, setNews] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load public data on mount
  useEffect(() => {
    async function loadPublicData() {
      try {
        setLoading(true);
        const [deptData, facData, evData, achData, annData, progData, galData, newsData, stData] = await Promise.all([
          api.getDepartmentInfo().catch(() => null),
          api.getFaculty().catch(() => []),
          api.getEvents().catch(() => []),
          api.getAchievements().catch(() => []),
          api.getAnnouncements().catch(() => []),
          api.getPrograms().catch(() => []),
          api.getGallery().catch(() => []),
          api.getNews().catch(() => []),
          api.getPublicStats().catch(() => ({})),
        ]);

        setDepartment(deptData);
        setFaculty(facData);
        setEvents(evData);
        setAchievements(achData);
        setAnnouncements(annData);
        setPrograms(progData);
        setGallery(galData);
        setNews(newsData);
        setStats(stData);
      } catch (err) {
        setError('Failed to fetch public department information.');
      } finally {
        setLoading(false);
      }
    }

    loadPublicData();
  }, []);

  // Listen for hash changes (e.g. #hod/login or #hod/dashboard)
  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash;
      if (hash === '#hod/login' || hash === '#login') {
        setIsLoginModalOpen(true);
      } else if (hash === '#hod/dashboard') {
        if (isAuthenticated) {
          setCurrentView('admin');
        } else {
          setIsLoginModalOpen(true);
        }
      }
    };
    handleHash();
    window.addEventListener('hashchange', handleHash);
    return () => window.removeEventListener('hashchange', handleHash);
  }, [isAuthenticated]);

  // Handle successful login
  const handleLoginSuccess = () => {
    setCurrentView('admin');
    window.location.hash = '#hod/dashboard';
  };

  // If viewing admin workspace and authenticated
  if (currentView === 'admin' && isAuthenticated) {
    return (
      <HodDashboard
        onBackToPublic={() => {
          setCurrentView('public');
          window.location.hash = '#overview';
        }}
      />
    );
  }


  return (
    <div className="app-root">
      {/* Public Navbar (Floating Capsule) */}
      <PublicNavbar
        onOpenLogin={() => setIsLoginModalOpen(true)}
        onGoToDashboard={() => {
          setCurrentView('admin');
          window.location.hash = '#hod/dashboard';
        }}
      />

      {loading ? (
        <div className="page-loader-screen">
          <Loader2 size={32} className="spin-loader" />
          <span>Loading Department Portal...</span>
        </div>
      ) : (
        <main>
          {/* 1. Hero Section */}
          <HeroSection
            department={department}
            stats={stats}
            onOpenLogin={() => setIsLoginModalOpen(true)}
          />

          {/* 2. About & HOD Address */}
          <AboutSection department={department} />

          {/* 3. Academic Programs & Courses */}
          <ProgramsSection programs={programs} />

          {/* 4. Faculty Showcase */}
          <FacultySection faculty={faculty} />

          {/* 5. Conferences & Events */}
          <EventsSection events={events} />

          {/* 6. Student Achievements */}
          <AchievementsSection achievements={achievements} />

          {/* 7. Department Press & News */}
          <NewsSection news={news} />

          {/* 8. Department Gallery */}
          <GallerySection gallery={gallery} />

          {/* 9. Official Circulars & Notices */}
          <AnnouncementsSection announcements={announcements} />

          {/* 10. Contact, Location & Query Dispatch */}
          <ContactSection department={department} />
        </main>
      )}

      {/* Public Footer */}
      <PublicFooter onOpenLogin={() => setIsLoginModalOpen(true)} />

      {/* HOD Login Modal */}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        onSuccess={handleLoginSuccess}
      />

      <style>{`
        .app-root {
          min-height: 100vh;
          background-color: var(--color-background);
          color: var(--color-text-main);
          display: flex;
          flex-direction: column;
        }
        .page-loader-screen {
          min-height: 70vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 16px;
          color: var(--color-text-muted);
          font-size: 0.9375rem;
        }
        .spin-loader {
          color: var(--color-primary);
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
