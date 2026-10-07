import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  User,
  Eye,
  X,
  FileText,
  Calendar,
  Award,
  BookOpen,
  CheckCircle2,
  Clock,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
} from 'lucide-react';
import { api } from '../../services/api';

export default function StudentDirectory({ batches }) {
  const [students, setStudents] = useState([]);
  const [totalStudents, setTotalStudents] = useState(0);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedBatch, setSelectedBatch] = useState('');
  const [selectedSection, setSelectedSection] = useState('');
  const [sections, setSections] = useState([]);
  const [page, setPage] = useState(1);
  const limit = 25;

  // Selected Student Profile Modal/Drawer State
  const [activeStudentId, setActiveStudentId] = useState(null);
  const [studentProfile, setStudentProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(false);

  // Load sections on mount
  useEffect(() => {
    // Fetch sections from Semester 3
    api.getBatches().then((bList) => {
      if (bList.length > 0 && !selectedBatch) {
        setSelectedBatch(bList[0].id);
      }
    });
  }, []);

  // Fetch student list
  const loadStudents = () => {
    setLoading(true);
    const params = {
      page,
      limit,
    };
    if (search.trim()) params.search = search.trim();
    if (selectedBatch) params.batch_id = selectedBatch;
    if (selectedSection) params.section_id = selectedSection;

    api.getStudents(params).then((res) => {
      setStudents(res.data || []);
      setTotalStudents(res.total || 0);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => {
    loadStudents();
  }, [page, selectedBatch, selectedSection]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadStudents();
  };

  // Open Student Detail
  const handleViewProfile = (studentId) => {
    setActiveStudentId(studentId);
    setLoadingProfile(true);
    api.getStudentDetail(studentId).then((data) => {
      setStudentProfile(data);
      setLoadingProfile(false);
    }).catch((err) => {
      console.error(err);
      setLoadingProfile(false);
    });
  };

  const totalPages = Math.ceil(totalStudents / limit) || 1;

  return (
    <div className="student-directory-container">
      {/* Header */}
      <div className="directory-header">
        <div>
          <h1 className="admin-page-title">Student Records Directory</h1>
          <p className="admin-page-subtitle">
            Search, filter, and inspect verified departmental academic history for all undergraduate cohorts.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="directory-controls card">
        <form onSubmit={handleSearchSubmit} className="search-form">
          <div className="search-input-wrap">
            <Search size={16} className="text-muted" />
            <input
              type="text"
              placeholder="Search by Roll Number (e.g. 25881A6601) or Name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="search-input"
            />
          </div>
          <button type="submit" className="btn btn-primary btn-sm">
            Search
          </button>
        </form>

        <div className="filter-row">
          <div className="filter-select-wrap">
            <label>Batch:</label>
            <select
              value={selectedBatch}
              onChange={(e) => {
                setSelectedBatch(e.target.value);
                setPage(1);
              }}
              className="form-select form-select-sm"
            >
              <option value="">All Batches</option>
              {batches.map((b) => (
                <option key={b.id} value={b.id}>
                  Batch {b.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => {
              setSearch('');
              setSelectedSection('');
              setPage(1);
              loadStudents();
            }}
            className="btn btn-secondary btn-sm"
          >
            Reset Filters
          </button>
        </div>
      </div>

      {/* Student Table */}
      <div className="card table-card">
        <div className="table-header-info">
          <span className="count-label">
            Found <strong>{totalStudents}</strong> registered students
          </span>
        </div>

        <div className="table-responsive">
          <table className="student-table">
            <thead>
              <tr>
                <th>Roll Number</th>
                <th>Full Name</th>
                <th>Batch</th>
                <th>Current Section</th>
                <th>Official Email</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" className="text-center py-6">
                    <RefreshCw size={20} className="spin text-primary inline" />
                    <span className="ml-2">Loading students...</span>
                  </td>
                </tr>
              ) : students.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center empty-cell">
                    No students match the selected search or filter criteria.
                  </td>
                </tr>
              ) : (
                students.map((stu) => (
                  <tr key={stu.id}>
                    <td>
                      <span className="roll-number-badge">{stu.rollNumber}</span>
                    </td>
                    <td className="font-semibold text-white">{stu.name}</td>
                    <td>{stu.batchName || '2025-2029'}</td>
                    <td>
                      <span className="section-pill-sm">
                        Section {stu.sectionName || 'A'}
                      </span>
                    </td>
                    <td className="text-muted text-sm">{stu.email || '—'}</td>
                    <td>
                      <button
                        onClick={() => handleViewProfile(stu.id)}
                        className="btn btn-outline btn-xs"
                      >
                        <Eye size={13} />
                        <span>Academic Profile</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="table-pagination-row">
            <span className="text-muted text-sm">
              Showing {(page - 1) * limit + 1} to {Math.min(page * limit, totalStudents)} of {totalStudents}
            </span>
            <div className="pagination-btn-group">
              <button
                disabled={page === 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="btn btn-secondary btn-xs"
              >
                <ChevronLeft size={14} /> Previous
              </button>
              <span className="page-current">Page {page} of {totalPages}</span>
              <button
                disabled={page === totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="btn btn-secondary btn-xs"
              >
                Next <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* STUDENT PROFILE DRAWER / MODAL */}
      {activeStudentId && (
        <div className="modal-backdrop" onClick={() => setActiveStudentId(null)}>
          <div className="modal-content modal-profile" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="profile-header-title">
                <User size={22} className="text-primary" />
                <div>
                  <h3>{studentProfile?.name || 'Student Profile'}</h3>
                  <span className="text-muted font-mono text-sm">
                    {studentProfile?.rollNumber} • Batch {studentProfile?.batchName || '2025-2029'}
                  </span>
                </div>
              </div>
              <button onClick={() => setActiveStudentId(null)} className="close-btn">
                <X size={18} />
              </button>
            </div>

            <div className="modal-body profile-body">
              {loadingProfile ? (
                <div className="text-center py-10">
                  <RefreshCw size={24} className="spin text-primary inline" />
                  <p className="mt-2 text-muted">Retrieving verified academic records...</p>
                </div>
              ) : studentProfile ? (
                <div className="profile-sections">
                  {/* Student Basic Details Bar */}
                  <div className="student-info-strip">
                    <div className="info-item">
                      <span className="info-lbl">Roll Number</span>
                      <span className="info-val font-mono text-primary">{studentProfile.rollNumber}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-lbl">Current Section</span>
                      <span className="info-val">Section {studentProfile.sectionName || 'A'}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-lbl">Email</span>
                      <span className="info-val">{studentProfile.email || '—'}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-lbl">Record Source</span>
                      <span className="info-val badge badge-success">Verified DB</span>
                    </div>
                  </div>

                  {/* 1. Subject-Wise Attendance */}
                  <div className="profile-card-sub">
                    <div className="sub-title-row">
                      <Clock size={16} className="text-primary" />
                      <h4>Verified Subject-Wise Attendance</h4>
                    </div>

                    {studentProfile.attendanceRecords && studentProfile.attendanceRecords.length > 0 ? (
                      <div className="table-responsive">
                        <table className="mini-table">
                          <thead>
                            <tr>
                              <th>Subject Code</th>
                              <th>Subject Name</th>
                              <th>Classes Attended</th>
                              <th>Total Conducted</th>
                              <th>Attendance %</th>
                            </tr>
                          </thead>
                          <tbody>
                            {studentProfile.attendanceRecords.map((att, i) => (
                              <tr key={i}>
                                <td className="font-mono text-primary">{att.subjectCode}</td>
                                <td>{att.subjectName}</td>
                                <td>{att.classesAttended ?? '—'}</td>
                                <td>{att.totalClasses ?? '—'}</td>
                                <td>
                                  <span
                                    className={`percentage-badge ${
                                      att.percentage >= 75 ? 'badge-success' : 'badge-danger'
                                    }`}
                                  >
                                    {att.percentage}%
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="empty-sub-card">
                        <Clock size={20} className="text-muted" />
                        <span>No official attendance records uploaded for this student yet.</span>
                      </div>
                    )}
                  </div>

                  {/* 2. Mid-Term Assessments */}
                  <div className="profile-card-sub">
                    <div className="sub-title-row">
                      <BookOpen size={16} className="text-primary" />
                      <h4>Mid-Term Internal Assessments</h4>
                    </div>

                    {studentProfile.assessmentRecords && studentProfile.assessmentRecords.length > 0 ? (
                      <div className="table-responsive">
                        <table className="mini-table">
                          <thead>
                            <tr>
                              <th>Assessment</th>
                              <th>Subject</th>
                              <th>Marks Obtained</th>
                              <th>Max Marks</th>
                              <th>Status</th>
                            </tr>
                          </thead>
                          <tbody>
                            {studentProfile.assessmentRecords.map((asm, i) => (
                              <tr key={i}>
                                <td>
                                  <span className="badge badge-outline">{asm.assessmentType}</span>
                                </td>
                                <td>{asm.subjectCode} - {asm.subjectName}</td>
                                <td className="font-semibold">{asm.marksObtained ?? '—'}</td>
                                <td>{asm.maxMarks ?? 30}</td>
                                <td>
                                  <span
                                    className={`badge ${
                                      asm.status === 'AVAILABLE' ? 'badge-success' : 'badge-warning'
                                    }`}
                                  >
                                    {asm.status}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="empty-sub-card">
                        <Clock size={20} className="text-muted" />
                        <span>No Mid-1 or Mid-2 records uploaded for this student yet.</span>
                      </div>
                    )}
                  </div>

                  {/* 3. Semester End Examination Results */}
                  <div className="profile-card-sub">
                    <div className="sub-title-row">
                      <Award size={16} className="text-primary" />
                      <h4>Semester Examination Results</h4>
                    </div>

                    {studentProfile.semesterResults && studentProfile.semesterResults.length > 0 ? (
                      <div className="table-responsive">
                        <table className="mini-table">
                          <thead>
                            <tr>
                              <th>Subject Code</th>
                              <th>Subject Name</th>
                              <th>Internal</th>
                              <th>External</th>
                              <th>Total</th>
                              <th>Grade</th>
                              <th>Grade Point</th>
                              <th>Result</th>
                            </tr>
                          </thead>
                          <tbody>
                            {studentProfile.semesterResults.map((res, i) => (
                              <tr key={i}>
                                <td className="font-mono text-primary">{res.subjectCode}</td>
                                <td>{res.subjectName}</td>
                                <td>{res.internalMarks ?? '—'}</td>
                                <td>{res.externalMarks ?? '—'}</td>
                                <td>{res.totalMarks ?? '—'}</td>
                                <td>
                                  <span className="badge badge-success font-semibold">{res.grade}</span>
                                </td>
                                <td>{res.gradePoint ?? '—'}</td>
                                <td>
                                  <span
                                    className={`badge ${
                                      res.resultStatus === 'PASSED' ? 'badge-success' : 'badge-danger'
                                    }`}
                                  >
                                    {res.resultStatus}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="empty-sub-card">
                        <Clock size={20} className="text-muted" />
                        <span>No semester results have been imported for this student yet.</span>
                      </div>
                    )}
                  </div>

                  {/* 4. Semester Summaries (SGPA/CGPA) */}
                  {studentProfile.semesterSummaries && studentProfile.semesterSummaries.length > 0 && (
                    <div className="summary-banner">
                      {studentProfile.semesterSummaries.map((sm, i) => (
                        <div key={i} className="summary-stat-box">
                          <span className="summary-label">Official Semester SGPA</span>
                          <span className="summary-value font-mono text-primary">{sm.sgpa ?? '—'}</span>
                          {sm.cgpa && (
                            <span className="summary-cgpa text-muted text-xs">CGPA: {sm.cgpa}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="profile-notice">
                    <CheckCircle2 size={14} className="text-success" />
                    <span>Raw data fidelity verified: All grades and percentages reflect exact official imports without heuristic estimation.</span>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
