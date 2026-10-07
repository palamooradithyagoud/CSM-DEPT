import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  UploadCloud,
  Users,
  BookOpen,
  History,
  ShieldCheck,
  UserCheck,
  LogOut,
  ArrowLeft,
  Layers,
  CheckCircle2,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import DataAvailabilityMatrix from './DataAvailabilityMatrix';
import AcademicUpload from './AcademicUpload';
import StudentDirectory from './StudentDirectory';
import SubjectManager from './SubjectManager';
import UploadHistoryView from './UploadHistoryView';

export default function HodDashboard({ onBackToPublic }) {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [batches, setBatches] = useState([]);
  const [uploadContext, setUploadContext] = useState(null);

  // Fetch batches
  useEffect(() => {
    api.getBatches().then(setBatches).catch(console.error);
  }, []);

  const handleNavigateToUpload = (context) => {
    setUploadContext(context);
    setActiveTab('upload');
  };

  return (
    <div className="hod-dashboard-root">
      {/* Top Header */}
      <header className="hod-header">
        <div className="container hod-header-inner">
          <div className="hod-brand-group">
            <button onClick={onBackToPublic} className="back-btn" title="Return to Public Website">
              <ArrowLeft size={16} />
              <span>Public Portal</span>
            </button>
            <div className="divider-vert" />
            <div className="hod-title-wrap">
              <span className="badge badge-success">Phase 2 Production</span>
              <h1 className="hod-main-title">HOD Academic Data Management Suite</h1>
            </div>
          </div>

          <div className="hod-user-profile">
            <div className="user-icon-circle">
              <UserCheck size={18} />
            </div>
            <div className="user-text">
              <span className="user-name">{user?.fullName || 'Dr. M. A. Jabbar'}</span>
              <span className="user-role-dept">{user?.role} • {user?.department || 'CSE'}</span>
            </div>
            <button onClick={logout} className="btn btn-secondary btn-sm" title="Log Out">
              <LogOut size={14} />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Secondary Navigation Bar */}
      <nav className="hod-nav-bar">
        <div className="container hod-nav-inner">
          <button
            className={`nav-tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <LayoutDashboard size={16} />
            <span>Overview & Availability</span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            <UploadCloud size={16} />
            <span>Upload Academic Data</span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'students' ? 'active' : ''}`}
            onClick={() => setActiveTab('students')}
          >
            <Users size={16} />
            <span>Students Directory</span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'subjects' ? 'active' : ''}`}
            onClick={() => setActiveTab('subjects')}
          >
            <BookOpen size={16} />
            <span>Curriculum Subjects</span>
          </button>

          <button
            className={`nav-tab-btn ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <History size={16} />
            <span>Upload Audit History</span>
          </button>
        </div>
      </nav>

      {/* Main Workspace Body */}
      <main className="container hod-workspace-body">
        {activeTab === 'overview' && (
          <div className="overview-tab-content">
            {/* Quick Context Summary Banner */}
            <div className="hierarchy-banner card">
              <div className="hierarchy-header">
                <Layers size={20} className="text-primary" />
                <div>
                  <h3 className="banner-title">Active Academic Hierarchy: Batch 2025–2029</h3>
                  <p className="text-muted text-sm">
                    Current Focus: 2nd Year (Semester 3) • Configurable Sections A, B & C • Dynamic 4-Year Hierarchy
                  </p>
                </div>
              </div>

              <div className="hierarchy-steps">
                <div className="step-box">
                  <span className="step-label">Batch</span>
                  <span className="step-value font-mono">2025–2029</span>
                </div>
                <span className="step-arrow">→</span>
                <div className="step-box">
                  <span className="step-label">Academic Year</span>
                  <span className="step-value">2nd Year</span>
                </div>
                <span className="step-arrow">→</span>
                <div className="step-box">
                  <span className="step-label">Semester</span>
                  <span className="step-value">Semester 3</span>
                </div>
                <span className="step-arrow">→</span>
                <div className="step-box">
                  <span className="step-label">Sections</span>
                  <span className="step-value">A, B, C</span>
                </div>
                <span className="step-arrow">→</span>
                <div className="step-box">
                  <span className="step-label">Roster</span>
                  <span className="step-value text-primary">193 Enrolled</span>
                </div>
              </div>
            </div>

            {/* Availability Matrix */}
            <DataAvailabilityMatrix
              batches={batches}
              onNavigateToUpload={handleNavigateToUpload}
            />
          </div>
        )}

        {activeTab === 'upload' && (
          <AcademicUpload
            initialContext={uploadContext}
            onUploadSuccess={() => {}}
          />
        )}

        {activeTab === 'students' && (
          <StudentDirectory batches={batches} />
        )}

        {activeTab === 'subjects' && (
          <SubjectManager batches={batches} />
        )}

        {activeTab === 'history' && (
          <UploadHistoryView />
        )}
      </main>
    </div>
  );
}
