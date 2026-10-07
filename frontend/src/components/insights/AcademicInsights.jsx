import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  AlertOctagon,
  Users,
  BookOpen,
  Layers,
  Sparkles,
  Sliders,
  ShieldAlert,
  ArrowRight,
  Download,
} from 'lucide-react';
import { api } from '../../services/api';
import InsightsFilters from './InsightsFilters';
import StudentWatchlist from './StudentWatchlist';
import SubjectInsights from './SubjectInsights';
import SectionInsights from './SectionInsights';
import ThresholdConfigModal from './ThresholdConfigModal';

export default function AcademicInsights({ batches }) {
  const [activeSubTab, setActiveSubTab] = useState('watchlist'); // 'watchlist' | 'subjects' | 'sections'
  const [filters, setFilters] = useState({
    batchId: '',
    academicYearId: '',
    semesterId: '',
    sectionId: '',
    severity: 'ALL',
    category: 'ALL',
  });

  const [overviewData, setOverviewData] = useState(null);
  const [loadingOverview, setLoadingOverview] = useState(false);

  // Watchlist pagination state
  const [watchlistStudents, setWatchlistStudents] = useState([]);
  const [watchlistTotal, setWatchlistTotal] = useState(0);
  const [watchlistPage, setWatchlistPage] = useState(1);
  const [loadingWatchlist, setLoadingWatchlist] = useState(false);

  // Config modal
  const [isConfigOpen, setIsConfigOpen] = useState(false);

  // Auto-select preferred batch
  useEffect(() => {
    if (batches && batches.length > 0 && !filters.batchId) {
      const pref = batches.find((b) => b.name === '2025-2029') || batches[0];
      setFilters((prev) => ({ ...prev, batchId: pref.id }));
    }
  }, [batches]);

  // Load Overview Data
  const loadOverview = () => {
    if (!filters.semesterId) return;
    setLoadingOverview(true);
    api.getInsightsOverview({
      batch_id: filters.batchId || undefined,
      academic_year_id: filters.academicYearId || undefined,
      semester_id: filters.semesterId || undefined,
      section_id: filters.sectionId || undefined,
    })
      .then((data) => {
        setOverviewData(data);
        setLoadingOverview(false);
      })
      .catch((err) => {
        console.error(err);
        setLoadingOverview(false);
      });
  };

  // Load Watchlist Data
  const loadWatchlist = () => {
    if (!filters.semesterId) return;
    setLoadingWatchlist(true);
    api.getStudentWatchlist({
      batch_id: filters.batchId || undefined,
      academic_year_id: filters.academicYearId || undefined,
      semester_id: filters.semesterId || undefined,
      section_id: filters.sectionId || undefined,
      severity: filters.severity !== 'ALL' ? filters.severity : undefined,
      category: filters.category !== 'ALL' ? filters.category : undefined,
      page: watchlistPage,
      limit: 20,
    })
      .then((res) => {
        setWatchlistStudents(res.data || []);
        setWatchlistTotal(res.total || 0);
        setLoadingWatchlist(false);
      })
      .catch((err) => {
        console.error(err);
        setLoadingWatchlist(false);
      });
  };

  useEffect(() => {
    loadOverview();
    loadWatchlist();
  }, [filters.batchId, filters.academicYearId, filters.semesterId, filters.sectionId, filters.severity, filters.category, watchlistPage]);

  const handleFilterChange = (newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
    setWatchlistPage(1);
  };

  const summary = overviewData?.summary || {
    studentsRequiringAttention: 0,
    criticalIssuesCount: 0,
    highPriorityCount: 0,
    mediumPriorityCount: 0,
    lowPriorityCount: 0,
    subjectsRequiringAttention: 0,
    sectionsRequiringAttention: 0,
  };

  return (
    <div className="academic-insights-workspace">
      {/* 1. Global Cascading Filters */}
      <InsightsFilters
        batches={batches}
        filters={filters}
        onChange={handleFilterChange}
        onRefresh={() => {
          loadOverview();
          loadWatchlist();
        }}
        loading={loadingOverview || loadingWatchlist}
        onOpenConfig={() => setIsConfigOpen(true)}
      />

      {/* 2. Top Summary KPI Grid */}
      <div className="insights-summary-grid">
        <div className="insight-kpi-card border-critical">
          <div className="kpi-header-row">
            <span className="kpi-title">Critical Attention</span>
            <AlertOctagon size={18} className="text-danger" />
          </div>
          <span className="kpi-big-number text-danger">{summary.criticalIssuesCount}</span>
          <span className="kpi-footer-note">Multiple backlogs or steep drops</span>
        </div>

        <div className="insight-kpi-card border-high">
          <div className="kpi-header-row">
            <span className="kpi-title">High Priority</span>
            <AlertTriangle size={18} className="text-warning" />
          </div>
          <span className="kpi-big-number text-warning">{summary.highPriorityCount}</span>
          <span className="kpi-footer-note">Attendance shortage or SGPA drop</span>
        </div>

        <div className="insight-kpi-card border-medium">
          <div className="kpi-header-row">
            <span className="kpi-title">Total Flagged Students</span>
            <Users size={18} className="text-primary" />
          </div>
          <span className="kpi-big-number">{summary.studentsRequiringAttention}</span>
          <span className="kpi-footer-note">Across evaluated cohort roster</span>
        </div>

        <div className="insight-kpi-card">
          <div className="kpi-header-row">
            <span className="kpi-title">Flagged Courses</span>
            <BookOpen size={18} className="text-muted" />
          </div>
          <span className="kpi-big-number">{summary.subjectsRequiringAttention}</span>
          <span className="kpi-footer-note">Sub-threshold pass rate or marks</span>
        </div>

        <div className="insight-kpi-card">
          <div className="kpi-header-row">
            <span className="kpi-title">Flagged Sections</span>
            <Layers size={18} className="text-muted" />
          </div>
          <span className="kpi-big-number">{summary.sectionsRequiringAttention}</span>
          <span className="kpi-footer-note">High failure concentration</span>
        </div>
      </div>

      {/* 3. Sub-Navigation Tabs */}
      <div className="analytics-sub-nav">
        <button
          className={`sub-nav-btn ${activeSubTab === 'watchlist' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('watchlist')}
        >
          <ShieldAlert size={15} />
          <span>Student Attention Watchlist</span>
        </button>

        <button
          className={`sub-nav-btn ${activeSubTab === 'subjects' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('subjects')}
        >
          <BookOpen size={15} />
          <span>Course Diagnostics ({summary.subjectsRequiringAttention})</span>
        </button>

        <button
          className={`sub-nav-btn ${activeSubTab === 'sections' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('sections')}
        >
          <Layers size={15} />
          <span>Section Diagnostics ({summary.sectionsRequiringAttention})</span>
        </button>

        <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem' }}>
          <button
            id="insights-export-pdf"
            className="btn btn-secondary btn-sm"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', padding: '0.35rem 0.65rem' }}
            onClick={async () => {
              try {
                await api.exportInsightsReport({
                  batch_id: filters.batchId,
                  semester_id: filters.semesterId,
                  section_id: filters.sectionId,
                  format: 'pdf',
                });
              } catch (e) {
                alert('Export failed: ' + e.message);
              }
            }}
          >
            <Download size={13} />
            <span>Export PDF</span>
          </button>
          <button
            id="insights-export-excel"
            className="btn btn-secondary btn-sm"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', padding: '0.35rem 0.65rem' }}
            onClick={async () => {
              try {
                await api.exportInsightsReport({
                  batch_id: filters.batchId,
                  semester_id: filters.semesterId,
                  section_id: filters.sectionId,
                  format: 'excel',
                });
              } catch (e) {
                alert('Export failed: ' + e.message);
              }
            }}
          >
            <Download size={13} />
            <span>Export Excel</span>
          </button>
        </div>
      </div>

      {/* 4. Tab Views */}
      <div className="insights-tab-content">
        {activeSubTab === 'watchlist' && (
          <StudentWatchlist
            students={watchlistStudents}
            total={watchlistTotal}
            page={watchlistPage}
            limit={20}
            onPageChange={(newPage) => setWatchlistPage(newPage)}
            severityFilter={filters.severity}
            onSeverityChange={(newSev) => handleFilterChange({ severity: newSev })}
            loading={loadingWatchlist}
          />
        )}

        {activeSubTab === 'subjects' && (
          <SubjectInsights
            subjects={overviewData?.flaggedSubjects || []}
            loading={loadingOverview}
          />
        )}

        {activeSubTab === 'sections' && (
          <SectionInsights
            sections={overviewData?.flaggedSections || []}
            loading={loadingOverview}
          />
        )}
      </div>

      {/* 5. Threshold Config Modal */}
      {isConfigOpen && (
        <ThresholdConfigModal
          onClose={() => {
            setIsConfigOpen(false);
            loadOverview();
            loadWatchlist();
          }}
        />
      )}
    </div>
  );
}
