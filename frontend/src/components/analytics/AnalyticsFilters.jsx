import React, { useState, useEffect } from 'react';
import { Filter, RefreshCw } from 'lucide-react';
import { api } from '../../services/api';

export default function AnalyticsFilters({ batches, filters, onChange, onRefresh, loading }) {
  const [academicYears, setAcademicYears] = useState([]);
  const [semesters, setSemesters] = useState([]);
  const [sections, setSections] = useState([]);
  const [subjects, setSubjects] = useState([]);

  // 1. Fetch Academic Years when Batch changes
  useEffect(() => {
    if (!filters.batchId) return;
    api.getAcademicYears(filters.batchId).then((years) => {
      setAcademicYears(years);
      // Select 2nd year if available, else first
      const defaultYear = years.find((y) => y.yearNumber === 2) || years[0];
      if (defaultYear && defaultYear.id !== filters.academicYearId) {
        onChange({ academicYearId: defaultYear.id });
      }
    }).catch(console.error);
  }, [filters.batchId]);

  // 2. Fetch Semesters when Academic Year changes
  useEffect(() => {
    if (!filters.academicYearId) {
      setSemesters([]);
      return;
    }
    api.getSemesters(filters.academicYearId).then((sems) => {
      setSemesters(sems);
      // Select Semester 3 if available, else first
      const defaultSem = sems.find((s) => s.semesterNumber === 3) || sems[0];
      if (defaultSem && defaultSem.id !== filters.semesterId) {
        onChange({ semesterId: defaultSem.id });
      }
    }).catch(console.error);
  }, [filters.academicYearId]);

  // 3. Fetch Sections & Subjects when Semester changes
  useEffect(() => {
    if (!filters.semesterId) {
      setSections([]);
      setSubjects([]);
      return;
    }
    api.getSections(filters.semesterId).then((secs) => {
      setSections(secs);
    }).catch(console.error);

    api.getSubjects(filters.semesterId).then((subs) => {
      setSubjects(subs);
    }).catch(console.error);
  }, [filters.semesterId]);

  return (
    <div className="analytics-filters-bar card">
      <div className="filters-header">
        <div className="filter-title-group">
          <Filter size={16} className="text-primary" />
          <span className="filters-title">Academic Hierarchy Filter</span>
        </div>
        <button
          onClick={onRefresh}
          className="btn btn-secondary btn-xs"
          disabled={loading}
          title="Refresh Current Analytics Metrics"
        >
          <RefreshCw size={13} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="filters-controls-grid">
        {/* Batch */}
        <div className="filter-field">
          <label>Batch</label>
          <select
            value={filters.batchId || ''}
            onChange={(e) => onChange({ batchId: e.target.value })}
            className="form-select form-select-sm"
          >
            {batches.map((b) => (
              <option key={b.id} value={b.id}>
                Batch {b.name}
              </option>
            ))}
          </select>
        </div>

        {/* Academic Year */}
        <div className="filter-field">
          <label>Academic Year</label>
          <select
            value={filters.academicYearId || ''}
            onChange={(e) => onChange({ academicYearId: e.target.value })}
            className="form-select form-select-sm"
          >
            {academicYears.map((ay) => (
              <option key={ay.id} value={ay.id}>
                {ay.name} ({ay.calendarYear || 'AY'})
              </option>
            ))}
          </select>
        </div>

        {/* Semester */}
        <div className="filter-field">
          <label>Semester</label>
          <select
            value={filters.semesterId || ''}
            onChange={(e) => onChange({ semesterId: e.target.value })}
            className="form-select form-select-sm"
          >
            {semesters.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        {/* Section */}
        <div className="filter-field">
          <label>Section</label>
          <select
            value={filters.sectionId || ''}
            onChange={(e) => onChange({ sectionId: e.target.value })}
            className="form-select form-select-sm"
          >
            <option value="">All Sections</option>
            {sections.map((sec) => (
              <option key={sec.id} value={sec.id}>
                Section {sec.name}
              </option>
            ))}
          </select>
        </div>

        {/* Subject */}
        <div className="filter-field">
          <label>Subject</label>
          <select
            value={filters.subjectId || ''}
            onChange={(e) => onChange({ subjectId: e.target.value })}
            className="form-select form-select-sm"
          >
            <option value="">All Subjects</option>
            {subjects.map((sub) => (
              <option key={sub.id} value={sub.id}>
                {sub.code} - {sub.shortName || sub.name}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
