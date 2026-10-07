const API_BASE = '/api/v1';

/**
 * Fetch wrapper with token authorization and JSON / FormData handling
 */
async function request(endpoint, options = {}) {
  const token = localStorage.getItem('dept_access_token');
  const isFormData = options.body instanceof FormData;

  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({
    success: false,
    message: 'Invalid server response.',
  }));

  if (!response.ok) {
    const errorMsg = data.message || `Request failed with status ${response.status}`;
    const error = new Error(errorMsg);
    error.status = response.status;
    error.details = data.error?.details || data.errors;
    throw error;
  }

  return data;
}

/**
 * Downloads binary or attachment file from API with bearer authentication
 */
async function downloadFile(endpoint, defaultFilename = 'report') {
  const token = localStorage.getItem('dept_access_token');
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const response = await fetch(`${API_BASE}${endpoint}`, { headers });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: `Export failed with status ${response.status}` }));
    throw new Error(errorData.message || 'Export failed');
  }

  let filename = defaultFilename;
  const disposition = response.headers.get('Content-Disposition');
  if (disposition && disposition.includes('filename=')) {
    const match = disposition.match(/filename="?([^"]+)"?/);
    if (match && match[1]) filename = match[1];
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
  return { success: true, filename };
}

export const api = {
  // Public Portal Endpoints (Zero authentication required)
  getDepartmentInfo: async () => {
    const res = await request('/public/department-info');
    return res.data?.department;
  },

  getFaculty: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/public/faculty${query ? `?${query}` : ''}`);
    return res.data?.faculty || [];
  },

  getFacultyDetail: async (id) => {
    const res = await request(`/public/faculty/${id}`);
    return res.data?.faculty;
  },

  getEvents: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/public/events${query ? `?${query}` : ''}`);
    return res.data?.events || [];
  },

  getAchievements: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/public/achievements${query ? `?${query}` : ''}`);
    return res.data?.achievements || [];
  },

  getAnnouncements: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/public/announcements${query ? `?${query}` : ''}`);
    return res.data?.announcements || [];
  },

  getPrograms: async () => {
    const res = await request('/public/programs');
    return res.data?.programs || [];
  },

  getGallery: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/public/gallery${query ? `?${query}` : ''}`);
    return res.data?.gallery || [];
  },

  getNews: async () => {
    const res = await request('/public/news');
    return res.data?.news || [];
  },

  getPublicStats: async () => {
    const res = await request('/public/stats');
    return res.data?.stats || {};
  },

  // Authentication Endpoints
  login: async (email, password) => {
    const res = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return res.data;
  },

  getCurrentUser: async () => {
    const res = await request('/auth/me');
    return res.data?.user;
  },

  // ==========================================
  // PHASE 2: ACADEMIC DATA MANAGEMENT ENDPOINTS
  // ==========================================

  // Hierarchy
  getBatches: async () => {
    const res = await request('/batches');
    return res.data || [];
  },

  createBatch: async (data) => {
    const res = await request('/batches', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return res;
  },

  getAcademicYears: async (batchId) => {
    const query = batchId ? `?batch_id=${batchId}` : '';
    const res = await request(`/academic-years${query}`);
    return res.data || [];
  },

  getSemesters: async (academicYearId) => {
    const query = academicYearId ? `?academic_year_id=${academicYearId}` : '';
    const res = await request(`/semesters${query}`);
    return res.data || [];
  },

  getSections: async (semesterId) => {
    const query = semesterId ? `?semester_id=${semesterId}` : '';
    const res = await request(`/sections${query}`);
    return res.data || [];
  },

  createSection: async (data) => {
    const res = await request('/sections', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return res;
  },

  // Subjects
  getSubjects: async (semesterId) => {
    const query = semesterId ? `?semester_id=${semesterId}` : '';
    const res = await request(`/subjects${query}`);
    return res.data || [];
  },

  createSubject: async (data) => {
    const res = await request('/subjects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return res;
  },

  // Students
  getStudents: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/students${query ? `?${query}` : ''}`);
    return res;
  },

  getStudentDetail: async (id) => {
    const res = await request(`/students/${id}`);
    return res.data;
  },

  createStudent: async (data) => {
    const res = await request('/students', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return res;
  },

  // Academic Uploads
  validateUpload: async (formData) => {
    const res = await request('/uploads/validate', {
      method: 'POST',
      body: formData,
    });
    return res;
  },

  confirmUpload: async (payload) => {
    const res = await request('/uploads/confirm', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    return res;
  },

  getUploadHistory: async (page = 1, limit = 20) => {
    const res = await request(`/uploads/history?page=${page}&limit=${limit}`);
    return res;
  },

  // Academic Data Availability Matrix
  getDataAvailability: async (semesterId, sectionId) => {
    const res = await request(`/academic-data/availability?semester_id=${semesterId}&section_id=${sectionId}`);
    return res.data;
  },

  // Academic Data Records
  getAttendanceRecords: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/attendance${query ? `?${query}` : ''}`);
    return res.data || [];
  },

  getAssessmentRecords: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/assessments${query ? `?${query}` : ''}`);
    return res.data || [];
  },

  getSemesterResults: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/results${query ? `?${query}` : ''}`);
    return res.data || [];
  },

  // ==========================================
  // PHASE 3: ACADEMIC ANALYTICS ENDPOINTS
  // ==========================================

  getAnalyticsOverview: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/analytics/overview${query ? `?${query}` : ''}`);
    return res.data;
  },

  getSectionAnalytics: async (semesterId) => {
    const res = await request(`/analytics/sections?semester_id=${semesterId}`);
    return res.data;
  },

  getSubjectAnalytics: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/analytics/subjects${query ? `?${query}` : ''}`);
    return res.data;
  },

  getSemesterComparison: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/analytics/semester-comparison${query ? `?${query}` : ''}`);
    return res.data;
  },

  getStudentAnalytics: async (studentId) => {
    const res = await request(`/analytics/student/${studentId}`);
    return res.data;
  },

  getStudentTrajectory: async (studentId) => {
    const res = await request(`/analytics/student/${studentId}/trajectory`);
    return res.data;
  },

  getAttendancePerformance: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/analytics/attendance-performance${query ? `?${query}` : ''}`);
    return res.data;
  },

  getGradeDistribution: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/analytics/grades${query ? `?${query}` : ''}`);
    return res.data;
  },

  // ==========================================
  // PHASE 4: PROBLEM IDENTIFICATION & INSIGHTS
  // ==========================================

  getInsightsOverview: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/insights/overview${query ? `?${query}` : ''}`);
    return res.data;
  },

  getStudentWatchlist: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/insights/students${query ? `?${query}` : ''}`);
    return res.data;
  },

  getStudentInsights: async (studentId, semesterId) => {
    const query = semesterId ? `?semester_id=${semesterId}` : '';
    const res = await request(`/insights/students/${studentId}${query}`);
    return res.data;
  },

  getSubjectInsights: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/insights/subjects${query ? `?${query}` : ''}`);
    return res.data;
  },

  getSectionInsights: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/insights/sections${query ? `?${query}` : ''}`);
    return res.data;
  },

  getInsightsConfig: async () => {
    const res = await request('/insights/config');
    return res.data;
  },

  updateInsightsConfig: async (payload) => {
    const res = await request('/insights/config', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    return res.data;
  },

  getEntityRecommendations: async (entityType, entityId, params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/insights/recommendations/${entityType}/${entityId}${query ? `?${query}` : ''}`);
    return res.data;
  },

  // ==========================================
  // PHASE 5: REPORTS & DOCUMENT EXPORTS
  // ==========================================

  exportDepartmentReport: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const ext = params.format === 'excel' ? 'xlsx' : (params.format || 'pdf');
    return downloadFile(`/reports/department${query ? `?${query}` : ''}`, `department_report.${ext}`);
  },

  exportSectionReport: async (sectionId, params = {}) => {
    const query = new URLSearchParams(params).toString();
    const ext = params.format === 'excel' ? 'xlsx' : (params.format || 'pdf');
    return downloadFile(`/reports/section/${sectionId}${query ? `?${query}` : ''}`, `section_report.${ext}`);
  },

  exportStudentReport: async (studentId, params = {}) => {
    const query = new URLSearchParams(params).toString();
    const ext = params.format === 'excel' ? 'xlsx' : (params.format || 'pdf');
    return downloadFile(`/reports/student/${studentId}${query ? `?${query}` : ''}`, `student_dossier.${ext}`);
  },

  exportSubjectReport: async (subjectId, params = {}) => {
    const query = new URLSearchParams(params).toString();
    const ext = params.format === 'excel' ? 'xlsx' : (params.format || 'pdf');
    return downloadFile(`/reports/subject/${subjectId}${query ? `?${query}` : ''}`, `subject_report.${ext}`);
  },

  exportInsightsReport: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const ext = params.format === 'excel' ? 'xlsx' : (params.format || 'pdf');
    return downloadFile(`/reports/insights${query ? `?${query}` : ''}`, `academic_insights.${ext}`);
  },

  previewReport: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await request(`/reports/preview${query ? `?${query}` : ''}`);
    return res.data;
  },
};


