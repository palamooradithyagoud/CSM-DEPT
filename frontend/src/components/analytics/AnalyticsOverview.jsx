import React from 'react';
import {
  Users,
  Award,
  BookOpen,
  Clock,
  CheckCircle2,
  XCircle,
  HelpCircle,
  TrendingUp,
} from 'lucide-react';

export default function AnalyticsOverview({ data, loading }) {
  if (loading) {
    return (
      <div className="analytics-loading-box card">
        <div className="spin-loader" />
        <span>Computing real-time departmental analytics from verified records...</span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="card empty-analytics-card">
        <HelpCircle size={24} className="text-muted" />
        <p>Select an academic context from the filter bar above to compute performance metrics.</p>
      </div>
    );
  }

  const { totalStudents, dataAvailability, metrics } = data;
  const isResultsAvail = dataAvailability?.results === 'AVAILABLE';
  const isAttAvail = dataAvailability?.attendance === 'AVAILABLE';

  return (
    <div className="analytics-overview-view">
      {/* KPI Cards Grid */}
      <div className="kpi-grid">
        {/* Total Students */}
        <div className="kpi-card card">
          <div className="kpi-icon-wrap bg-blue-subtle text-blue">
            <Users size={20} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Total Enrolled Cohort</span>
            <span className="kpi-value font-mono">{totalStudents}</span>
            <span className="kpi-subtext text-muted">
              {metrics?.studentsWithResults || 0} with results • {metrics?.studentsWithAttendance || 0} with attendance
            </span>
          </div>
        </div>

        {/* Average SGPA */}
        <div className="kpi-card card">
          <div className="kpi-icon-wrap bg-green-subtle text-primary">
            <Award size={20} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Average SGPA</span>
            {isResultsAvail && metrics?.averageSGPA !== null ? (
              <span className="kpi-value font-mono text-primary">{metrics.averageSGPA}</span>
            ) : (
              <span className="kpi-not-avail">
                <Clock size={14} /> Not Available
              </span>
            )}
            <span className="kpi-subtext text-muted">
              {isResultsAvail ? 'Official semester performance' : 'Result data not yet imported'}
            </span>
          </div>
        </div>

        {/* Average CGPA */}
        <div className="kpi-card card">
          <div className="kpi-icon-wrap bg-purple-subtle text-purple">
            <TrendingUp size={20} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Average CGPA</span>
            {isResultsAvail && metrics?.averageCGPA !== null ? (
              <span className="kpi-value font-mono">{metrics.averageCGPA}</span>
            ) : (
              <span className="kpi-not-avail">
                <Clock size={14} /> Not Available
              </span>
            )}
            <span className="kpi-subtext text-muted">Cumulative grade progression</span>
          </div>
        </div>

        {/* Average Attendance */}
        <div className="kpi-card card">
          <div className="kpi-icon-wrap bg-yellow-subtle text-yellow">
            <Clock size={20} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Average Attendance</span>
            {isAttAvail && metrics?.averageAttendance !== null ? (
              <span className="kpi-value font-mono">
                {metrics.averageAttendance}%
              </span>
            ) : (
              <span className="kpi-not-avail">
                <Clock size={14} /> Not Available
              </span>
            )}
            <span className="kpi-subtext text-muted">
              {isAttAvail ? 'Across all enrolled subjects' : 'Attendance sheets not yet imported'}
            </span>
          </div>
        </div>

        {/* Pass Percentage */}
        <div className="kpi-card card">
          <div className="kpi-icon-wrap bg-teal-subtle text-teal">
            <CheckCircle2 size={20} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label">Pass Percentage</span>
            {isResultsAvail && metrics?.passPercentage !== null ? (
              <span className={`kpi-value font-mono ${metrics.passPercentage >= 85 ? 'text-primary' : 'text-yellow'}`}>
                {metrics.passPercentage}%
              </span>
            ) : (
              <span className="kpi-not-avail">
                <Clock size={14} /> Not Available
              </span>
            )}
            <span className="kpi-subtext text-muted">
              {metrics?.totalPassedStudents ?? 0} Passed • {metrics?.totalFailedStudents ?? 0} Backlogs
            </span>
          </div>
        </div>
      </div>

      {/* Cohort Progression Summary Box */}
      <div className="card cohort-summary-card">
        <h3 className="section-title">Cohort Assessment Status</h3>
        <div className="status-indicator-strip">
          <div className="indicator-box">
            <div className="indicator-title-row">
              <span className="indicator-label">Semester Result Records</span>
              <span className={`badge ${isResultsAvail ? 'badge-success' : 'badge-outline'}`}>
                {isResultsAvail ? 'UPLOADED & VERIFIED' : 'NOT AVAILABLE'}
              </span>
            </div>
            <p className="text-muted text-sm">
              {isResultsAvail
                ? `Results available for ${metrics.studentsWithResults} students in this context.`
                : 'Upload end-semester result spreadsheet to view SGPA, CGPA, and grade distributions.'}
            </p>
          </div>

          <div className="indicator-box">
            <div className="indicator-title-row">
              <span className="indicator-label">Subject Attendance Records</span>
              <span className={`badge ${isAttAvail ? 'badge-success' : 'badge-outline'}`}>
                {isAttAvail ? 'UPLOADED & VERIFIED' : 'NOT AVAILABLE'}
              </span>
            </div>
            <p className="text-muted text-sm">
              {isAttAvail
                ? `Subject attendance tracked for ${metrics.studentsWithAttendance} students.`
                : 'Upload subject attendance spreadsheet to view attendance averages and correlations.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
