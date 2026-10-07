import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, CheckCircle2, AlertTriangle, Layers, X, RefreshCw } from 'lucide-react';
import { api } from '../../services/api';

export default function SubjectManager({ batches }) {
  const [academicYears, setAcademicYears] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [semesters, setSemesters] = useState([]);
  const [selectedSemester, setSelectedSemester] = useState('');
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(false);

  // Add Subject Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [formCode, setFormCode] = useState('');
  const [formName, setFormName] = useState('');
  const [formShortName, setFormShortName] = useState('');
  const [formCredits, setFormCredits] = useState(3.0);
  const [formType, setFormType] = useState('THEORY');
  const [modalError, setModalError] = useState('');
  const [modalSuccess, setModalSuccess] = useState('');

  // 1. Initial Batch selection
  useEffect(() => {
    if (batches && batches.length > 0 && !selectedBatch) {
      const pref = batches.find((b) => b.name === '2025-2029') || batches[0];
      setSelectedBatch(pref.id);
    }
  }, [batches]);

  // 2. Load Years
  useEffect(() => {
    if (!selectedBatch) return;
    api.getAcademicYears(selectedBatch).then((years) => {
      setAcademicYears(years);
      const prefYear = years.find((y) => y.yearNumber === 2) || years[0];
      if (prefYear) setSelectedYear(prefYear.id);
    }).catch(console.error);
  }, [selectedBatch]);

  // 3. Load Semesters
  useEffect(() => {
    if (!selectedYear) return;
    api.getSemesters(selectedYear).then((sems) => {
      setSemesters(sems);
      const prefSem = sems.find((s) => s.semesterNumber === 3) || sems[0];
      if (prefSem) setSelectedSemester(prefSem.id);
    }).catch(console.error);
  }, [selectedYear]);

  // 4. Load Subjects for selected semester
  const loadSubjects = () => {
    if (!selectedSemester) return;
    setLoading(true);
    api.getSubjects(selectedSemester).then((list) => {
      setSubjects(list);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => {
    loadSubjects();
  }, [selectedSemester]);

  // Handle Add Subject Submit
  const handleAddSubject = async (e) => {
    e.preventDefault();
    setModalError('');
    setModalSuccess('');

    if (!formCode.trim() || !formName.trim()) {
      setModalError('Subject Code and Subject Name are required.');
      return;
    }

    try {
      await api.createSubject({
        semesterId: selectedSemester,
        code: formCode.trim().toUpperCase(),
        name: formName.trim(),
        shortName: formShortName.trim() || formCode.trim(),
        credits: parseFloat(formCredits),
        subjectType: formType,
      });

      setModalSuccess(`Subject '${formCode.toUpperCase()}' registered successfully.`);
      setFormCode('');
      setFormName('');
      setFormShortName('');
      loadSubjects();
      setTimeout(() => {
        setIsAddModalOpen(false);
        setModalSuccess('');
      }, 1200);
    } catch (err) {
      setModalError(err.message || 'Failed to add subject.');
    }
  };

  return (
    <div className="subject-manager-container">
      {/* Header */}
      <div className="view-header-flex">
        <div>
          <h1 className="admin-page-title">Curriculum Subjects Configuration</h1>
          <p className="admin-page-subtitle">
            Configure curricular courses and credit allocations. The upload validator ensures uploaded records strictly map to these subjects.
          </p>
        </div>
        <button onClick={() => setIsAddModalOpen(true)} className="btn btn-primary btn-sm">
          <Plus size={16} />
          <span>Add Subject</span>
        </button>
      </div>

      {/* Selectors Bar */}
      <div className="card filters-card">
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

      {/* Subjects Table */}
      <div className="card table-card">
        <div className="table-header-info">
          <span className="count-label">
            Configured Subjects ({subjects.length})
          </span>
        </div>

        <div className="table-responsive">
          <table className="subjects-table">
            <thead>
              <tr>
                <th>Subject Code</th>
                <th>Subject Name</th>
                <th>Short Name</th>
                <th>Credits</th>
                <th>Course Type</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" className="text-center py-6">
                    <RefreshCw size={20} className="spin text-primary inline" />
                    <span className="ml-2">Loading configured subjects...</span>
                  </td>
                </tr>
              ) : subjects.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center empty-cell">
                    No subjects configured for this semester yet. Use 'Add Subject' to register courses.
                  </td>
                </tr>
              ) : (
                subjects.map((sub) => (
                  <tr key={sub.id}>
                    <td>
                      <span className="subject-code-pill font-mono">{sub.code}</span>
                    </td>
                    <td className="font-semibold text-white">{sub.name}</td>
                    <td className="text-muted">{sub.shortName || '—'}</td>
                    <td>
                      <span className="credits-badge">{sub.credits} Credits</span>
                    </td>
                    <td>
                      <span
                        className={`badge ${
                          sub.subjectType === 'LAB'
                            ? 'badge-warning'
                            : sub.subjectType === 'ELECTIVE'
                            ? 'badge-info'
                            : 'badge-outline'
                        }`}
                      >
                        {sub.subjectType}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-success">Active</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ADD SUBJECT MODAL */}
      {isAddModalOpen && (
        <div className="modal-backdrop" onClick={() => setIsAddModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title-wrap">
                <BookOpen size={20} className="text-primary" />
                <h3>Configure New Subject</h3>
              </div>
              <button onClick={() => setIsAddModalOpen(false)} className="close-btn">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleAddSubject} className="modal-form">
              {modalError && (
                <div className="alert alert-error">
                  <AlertTriangle size={16} />
                  <span>{modalError}</span>
                </div>
              )}

              {modalSuccess && (
                <div className="alert alert-success">
                  <CheckCircle2 size={16} />
                  <span>{modalSuccess}</span>
                </div>
              )}

              <div className="form-group">
                <label>Subject Code (e.g. A9002, A9503)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. A9503"
                  value={formCode}
                  onChange={(e) => setFormCode(e.target.value.toUpperCase())}
                  className="form-input font-mono"
                />
              </div>

              <div className="form-group">
                <label>Subject Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Data Structures using C++"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  className="form-input"
                />
              </div>

              <div className="form-row-2">
                <div className="form-group">
                  <label>Short Name / Abbreviation</label>
                  <input
                    type="text"
                    placeholder="e.g. DS"
                    value={formShortName}
                    onChange={(e) => setFormShortName(e.target.value)}
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label>Credits</label>
                  <input
                    type="number"
                    step="0.5"
                    min="1"
                    max="10"
                    value={formCredits}
                    onChange={(e) => setFormCredits(e.target.value)}
                    className="form-input"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Course Type</label>
                <select
                  value={formType}
                  onChange={(e) => setFormType(e.target.value)}
                  className="form-select"
                >
                  <option value="THEORY">THEORY</option>
                  <option value="LAB">LAB / PRACTICAL</option>
                  <option value="ELECTIVE">ELECTIVE</option>
                </select>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Subject
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
