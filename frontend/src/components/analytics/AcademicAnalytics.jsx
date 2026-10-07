import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  Layers,
  BookOpen,
  GitCompare,
  Activity,
  Award,
  User,
} from 'lucide-react';
import { api } from '../../services/api';
import AnalyticsFilters from './AnalyticsFilters';
import AnalyticsOverview from './AnalyticsOverview';
import SectionComparison from './SectionComparison';
import SubjectAnalytics from './SubjectAnalytics';
import SemesterComparison from './SemesterComparison';
import AttendancePerformance from './AttendancePerformance';
import GradeDistribution from './GradeDistribution';
import StudentAnalytics from './StudentAnalytics';

export default function AcademicAnalytics({ batches }) {
  const [activeSubTab, setActiveSubTab] = useState('overview');
  const [selectedStudentId, setSelectedStudentId] = useState(null);
  const [filters, setFilters] = useState({
    batchId: '',
    academicYearId: '',
    semesterId: '',
    sectionId: '',
    subjectId: '',
  });

  const [semestersList, setSemestersList] = useState([]);
  const [overviewData, setOverviewData] = useState(null);
  const [loadingOverview, setLoadingOverview] = useState(false);

  // Initialize batch
  useEffect(() => {
    if (batches && batches.length > 0 && !filters.batchId) {
      const pref = batches.find((b) => b.name === '2025-2029') || batches[0];
      setFilters((prev) => ({ ...prev, batchId: pref.id }));
    }
  }, [batches]);

  // Load all semesters for the selected academic year
  useEffect(() => {
    if (!filters.academicYearId) return;
    api.getSemesters(filters.academicYearId).then((sems) => {
      setSemestersList(sems);
    }).catch(console.error);
  }, [filters.academicYearId]);

  // Load overview data when filters change
  const loadOverview = () => {
    if (!filters.semesterId) return;
    setLoadingOverview(true);
    api.getAnalyticsOverview({
      batch_id: filters.batchId || undefined,
      academic_year_id: filters.academicYearId || undefined,
      semester_id: filters.semesterId || undefined,
      section_id: filters.sectionId || undefined,
    }).then((res) => {
      setOverviewData(res);
      setLoadingOverview(false);
    }).catch((err) => {
      console.error(err);
      setLoadingOverview(false);
    });
  };

  useEffect(() => {
    loadOverview();
  }, [filters.batchId, filters.academicYearId, filters.semesterId, filters.sectionId]);

  const handleFilterChange = (newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const handleDrilldownStudent = (studentId) => {
    setSelectedStudentId(studentId);
    setActiveSubTab('student');
  };

  return (
    <div className="academic-analytics-workspace">
      {/* Global Cascading Filters */}
      <AnalyticsFilters
        batches={batches}
        filters={filters}
        onChange={handleFilterChange}
        onRefresh={loadOverview}
        loading={loadingOverview}
      />

      {/* Analytics Sub-Navigation */}
      <div className="analytics-sub-nav">
        <button
          className={`sub-nav-btn ${activeSubTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('overview')}
        >
          <LayoutDashboard size={15} />
          <span>Department Overview</span>
        </button>

        <button
          className={`sub-nav-btn ${activeSubTab === 'sections' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('sections')}
        >
          <Layers size={15} />
          <span>Section Comparison</span>
        </button>

        <button
          className={`sub-nav-btn ${activeSubTab === 'subjects' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('subjects')}
        >
          <BookOpen size={15} />
          <span>Subject Analytics</span>
        </button>

        <button
          className={`sub-nav-btn ${activeSubTab === 'semester_comp' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('semester_comp')}
        >
          <GitCompare size={15} />
          <span>Semester Comparison (T1 vs T2)</span>
        </button>

        <button
          className={`sub-nav-btn ${activeSubTab === 'student' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('student')}
        >
          <User size={15} />
          <span>Student Analytics</span>
        </button>

        <button
          className={`sub-nav-btn ${activeSubTab === 'attendance_perf' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('attendance_perf')}
        >
          <Activity size={15} />
          <span>Attendance vs Performance</span>
        </button>

        <button
          className={`sub-nav-btn ${activeSubTab === 'grades' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('grades')}
        >
          <Award size={15} />
          <span>Grade Distribution</span>
        </button>
      </div>

      {/* Sub-view Rendering */}
      <div className="analytics-sub-body">
        {activeSubTab === 'overview' && (
          <AnalyticsOverview
            data={overviewData}
            loading={loadingOverview}
          />
        )}

        {activeSubTab === 'sections' && (
          <SectionComparison
            semesterId={filters.semesterId}
          />
        )}

        {activeSubTab === 'subjects' && (
          <SubjectAnalytics
            semesterId={filters.semesterId}
            sectionId={filters.sectionId}
            subjectId={filters.subjectId}
          />
        )}

        {activeSubTab === 'semester_comp' && (
          <SemesterComparison
            batchId={filters.batchId}
            sectionId={filters.sectionId}
            semesters={semestersList}
            onSelectStudent={handleDrilldownStudent}
          />
        )}

        {activeSubTab === 'student' && (
          <StudentAnalytics
            studentId={selectedStudentId}
          />
        )}

        {activeSubTab === 'attendance_perf' && (
          <AttendancePerformance
            semesterId={filters.semesterId}
            sectionId={filters.sectionId}
            subjectId={filters.subjectId}
          />
        )}

        {activeSubTab === 'grades' && (
          <GradeDistribution
            semesterId={filters.semesterId}
            sectionId={filters.sectionId}
            subjectId={filters.subjectId}
          />
        )}
      </div>
    </div>
  );
}
