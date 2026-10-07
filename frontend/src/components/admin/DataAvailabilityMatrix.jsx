import React, { useState, useEffect } from 'react';
import { CheckCircle2, Clock, XCircle, RefreshCw, Layers } from 'lucide-react';
import { api } from '../../services/api';

export default function DataAvailabilityMatrix({ batches, onNavigateToUpload }) {
  const [selectedBatch, setSelectedBatch] = useState('');
  const [academicYears, setAcademicYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState('');
  const [semesters, setSemesters] = useState([]);
  const [selectedSemester, setSelectedSemester] = useState('');
  const [sections, setSections] = useState([]);
  const [sectionStatuses, setSectionStatuses] = useState({});
  const [loading, setLoading] = useState(false);

  // Initialize selected batch
  useEffect(() => {
    if (batches && batches.length > 0 && !selectedBatch) {
      const primary = batches.find(b => b.name === '2025-2029') || batches[0];
      setSelectedBatch(primary.id);
    }
  }, [batches]);

  // Load Academic Years when Batch changes
  useEffect(() => {
    if (!selectedBatch) return;
    api.getAcademicYears(selectedBatch).then(years => {
      setAcademicYears(years);
      // Select 2nd year if available, else first
      const defaultYear = years.find(y => y.yearNumber === 2) || years[0];
      if (defaultYear) {
        setSelectedYear(defaultYear.id);
      }
    }).catch(console.error);
  }, [selectedBatch]);

  // Load Semesters when Academic Year changes
  useEffect(() => {
    if (!selectedYear) return;
    api.getSemesters(selectedYear).then(sems => {
      setSemesters(sems);
      // Select semester 3 if available, else first
      const defaultSem = sems.find(s => s.semesterNumber === 3) || sems[0];
      if (defaultSem) {
        setSelectedSemester(defaultSem.id);
      }
    }).catch(console.error);
  }, [selectedYear]);

  // Load Sections and check availability for each section
  useEffect(() => {
    if (!selectedSemester) return;
    setLoading(true);
    api.getSections(selectedSemester).then(async (secs) => {
      setSections(secs);
      const statuses = {};
      for (const sec of secs) {
        try {
          const avail = await api.getDataAvailability(selectedSemester, sec.id);
          statuses[sec.id] = avail;
        } catch {
          statuses[sec.id] = null;
        }
      }
      setSectionStatuses(statuses);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [selectedSemester]);

  const refreshMatrix = () => {
    if (!selectedSemester) return;
    setLoading(true);
    api.getSections(selectedSemester).then(async (secs) => {
      setSections(secs);
      const statuses = {};
      for (const sec of secs) {
        try {
          const avail = await api.getDataAvailability(selectedSemester, sec.id);
          statuses[sec.id] = avail;
        } catch {
          statuses[sec.id] = null;
        }
      }
      setSectionStatuses(statuses);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  const renderStatusPill = (item) => {
    if (!item) {
      return (
        <span className="status-pill status-missing">
          <Clock size={13} />
          <span>Not Available</span>
        </span>
      );
    }
    if (item.available) {
      return (
        <span className="status-pill status-available">
          <CheckCircle2 size={13} />
          <span>Uploaded ({item.recordCount})</span>
        </span>
      );
    }
    return (
      <span className="status-pill status-missing">
        <Clock size={13} />
        <span>Not Available</span>
      </span>
    );
  };

  return (
    <div className="availability-card card">
      <div className="availability-header">
        <div>
          <h2 className="card-title">Academic Data Availability Matrix</h2>
          <p className="card-subtitle">
            Real-time track of academic records across sections. Verifies readiness for departmental review.
          </p>
        </div>
        <button
          onClick={refreshMatrix}
          className="btn btn-secondary btn-sm"
          disabled={loading}
          title="Refresh Data Status"
        >
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Context Selectors */}
      <div className="availability-filters">
        <div className="filter-group">
          <label>Batch</label>
          <select
            value={selectedBatch}
            onChange={(e) => setSelectedBatch(e.target.value)}
            className="form-select"
          >
            {batches.map((b) => (
              <option key={b.id} value={b.id}>
                Batch {b.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Academic Year</label>
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
            className="form-select"
          >
            {academicYears.map((ay) => (
              <option key={ay.id} value={ay.id}>
                {ay.name} ({ay.calendarYear || 'AY'})
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Semester</label>
          <select
            value={selectedSemester}
            onChange={(e) => setSelectedSemester(e.target.value)}
            className="form-select"
          >
            {semesters.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Matrix Table */}
      <div className="table-responsive">
        <table className="matrix-table">
          <thead>
            <tr>
              <th>Section</th>
              <th>Enrolled Students</th>
              <th>Attendance</th>
              <th>Mid-1 Result</th>
              <th>Mid-2 Result</th>
              <th>Semester Result</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {sections.length === 0 ? (
              <tr>
                <td colSpan="7" className="text-center empty-cell">
                  {loading ? 'Querying section statuses...' : 'No sections configured for this semester.'}
                </td>
              </tr>
            ) : (
              sections.map((sec) => {
                const stat = sectionStatuses[sec.id];
                return (
                  <tr key={sec.id}>
                    <td>
                      <div className="section-pill">Section {sec.name}</div>
                    </td>
                    <td>
                      <span className="student-count">{stat?.totalStudents ?? '—'} Students</span>
                    </td>
                    <td>{renderStatusPill(stat?.attendance)}</td>
                    <td>{renderStatusPill(stat?.mid1)}</td>
                    <td>{renderStatusPill(stat?.mid2)}</td>
                    <td>{renderStatusPill(stat?.semesterResult)}</td>
                    <td>
                      <button
                        onClick={() => onNavigateToUpload({
                          batchId: selectedBatch,
                          academicYearId: selectedYear,
                          semesterId: selectedSemester,
                          sectionId: sec.id,
                        })}
                        className="btn btn-outline btn-xs"
                      >
                        Upload
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <div className="matrix-footer">
        <div className="legend-items">
          <span className="legend-item">
            <CheckCircle2 size={13} className="text-success" /> Uploaded & Verified
          </span>
          <span className="legend-item">
            <Clock size={13} className="text-muted" /> Not Available (Optional for Mid-1/Mid-2)
          </span>
        </div>
      </div>
    </div>
  );
}
