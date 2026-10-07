import React, { useState, useEffect } from 'react';
 import { Filter, RefreshCw, Sliders, AlertTriangle } from 'lucide-react';
 import { api } from '../../services/api';

export default function InsightsFilters({
  batches,
  filters,
  onChange,
  onRefresh,
  loading,
  onOpenConfig,
}) {
  const [academicYears, setAcademicYears] = useState([]);
  const [semesters, setSemesters] = useState([]);
  const [sections, setSections] = useState([]);
  const [loadingDep, setLoadingDep] = useState(false);

  // 1. Fetch Academic Years when batch changes
  useEffect(() => {
    if (!filters.batchId) {
      setAcademicYears([]);
      return;
    }
    setLoadingDep(true);
    api.getAcademicYears(filters.batchId)
      .then((years) => {
        setAcademicYears(years);
        if (years.length > 0 && !filters.academicYearId) {
          const pref = years.find((y) => y.yearNumber === 2) || years[0];
          onChange({ academicYearId: pref.id });
        }
        setLoadingDep(false);
      })
      .catch(() => setLoadingDep(false));
  }, [filters.batchId]);

  // 2. Fetch Semesters when academic year changes
  useEffect(() => {
    if (!filters.academicYearId) {
      setSemesters([]);
      return;
    }
    setLoadingDep(true);
    api.getSemesters(filters.academicYearId)
      .then((sems) => {
        setSemesters(sems);
        if (sems.length > 0 && !filters.semesterId) {
          const pref = sems.find((s) => s.semesterNumber === 3) || sems[0];
          onChange({ semesterId: pref.id });
        }
        setLoadingDep(false);
      })
      .catch(() => setLoadingDep(false));
  }, [filters.academicYearId]);

  // 3. Fetch Sections when semester changes
  useEffect(() => {
    if (!filters.semesterId) {
      setSections([]);
      return;
    }
    setLoadingDep(true);
    api.getSections(filters.semesterId)
      .then((secs) => {
        setSections(secs);
        setLoadingDep(false);
      })
      .catch(() => setLoadingDep(false));
  }, [filters.semesterId]);

  return (
    <div className="analytics-filter-bar card">
      <div className="filter-bar-header">
        <div className="flex items-center gap-2">
          <AlertTriangle size={18} className="text-danger" />
          <span className="filter-bar-title font-semibold">Diagnostic & Problem Filters</span>
        </div>
        <div className="flex items-center gap-2">
          {onOpenConfig && (
            <button
              onClick={onOpenConfig}
              className="btn btn-secondary btn-xs flex items-center gap-1"
              title="Inspect or adjust diagnostic thresholds"
            >
              <Sliders size={13} />
              <span>Thresholds</span>
            </button>
          )}
          <button
            onClick={onRefresh}
            disabled={loading || loadingDep}
            className="btn btn-secondary btn-xs flex items-center gap-1"
            title="Refresh Diagnostic Data"
          >
            <RefreshCw size={13} className={loading ? 'spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <div className="filter-selectors-grid">
        {/* Batch */}
        <div className="filter-group">
          <label>Batch</label>
          <select
            value={filters.batchId || ''}
            onChange={(e) => onChange({ batchId: e.target.value, academicYearId: '', semesterId: '', sectionId: '' })}
            className="form-select"
          >
            <option value="">All Batches</option>
            {batches && batches.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
        </div>

        {/* Academic Year */}
        <div className="filter-group">
          <label>Academic Year</label>
          <select
            value={filters.academicYearId || ''}
            onChange={(e) => onChange({ academicYearId: e.target.value, semesterId: '', sectionId: '' })}
            disabled={!filters.batchId || academicYears.length === 0}
            className="form-select"
          >
            <option value="">All Years</option>
            {academicYears.map((ay) => (
              <option key={ay.id} value={ay.id}>
                {ay.name}
              </option>
            ))}
          </select>
        </div>

        {/* Semester */}
        <div className="filter-group">
          <label>Semester</label>
          <select
            value={filters.semesterId || ''}
            onChange={(e) => onChange({ semesterId: e.target.value, sectionId: '' })}
            disabled={!filters.academicYearId || semesters.length === 0}
            className="form-select font-mono"
          >
            <option value="">All Semesters</option>
            {semesters.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        {/* Section */}
        <div className="filter-group">
          <label>Section</label>
          <select
            value={filters.sectionId || ''}
            onChange={(e) => onChange({ sectionId: e.target.value })}
            disabled={!filters.semesterId || sections.length === 0}
            className="form-select"
          >
            <option value="">All Sections</option>
            {sections.map((sec) => (
              <option key={sec.id} value={sec.id}>
                Section {sec.name}
              </option>
            ))}
          </select>
        </div>

        {/* Severity */}
        <div className="filter-group">
          <label>Severity</label>
          <select
            value={filters.severity || 'ALL'}
            onChange={(e) => onChange({ severity: e.target.value })}
            className="form-select font-semibold"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical Only</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>

        {/* Category */}
        <div className="filter-group">
          <label>Issue Signal Type</label>
          <select
            value={filters.category || 'ALL'}
            onChange={(e) => onChange({ category: e.target.value })}
            className="form-select"
          >
            <option value="ALL">All Diagnostic Signals</option>
            <option value="LOW_ATTENDANCE">Low Attendance (&lt;75%)</option>
            <option value="FAILED_SUBJECTS">Failed Subjects</option>
            <option value="SGPA_DECLINE">SGPA Performance Decline</option>
            <option value="CONSECUTIVE_DECLINE">Consecutive Multi-Sem Decline</option>
            <option value="REPEATED_FAILURE">Repeated Backlog</option>
            <option value="COMBINED_ATTENDANCE_PERFORMANCE">Attendance + Performance Deficit</option>
          </select>
        </div>
      </div>
    </div>
  );
}
