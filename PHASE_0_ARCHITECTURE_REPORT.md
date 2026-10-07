# PHASE 0 — PROJECT ARCHITECTURE & DEVELOPMENT SPECIFICATION
**System**: Student Academic Performance & Department Management System  
**Client / Stakeholder**: Department Head (HOD)  
**Primary Year Focus**: Second Year (with full horizontal scaling for 3rd & 4th Years)  
**Date**: October 2026  

---

## 1. Executive Summary & Current Project Assessment

### 1.1 Directory & Workspace Assessment
- **Workspace Path**: `c:\SEM EXAMS\student management by jabbar sir`
- **Initial Status**: Clean, greenfield directory with no pre-existing legacy code or conflicting configurations.
- **Constraints Recognized**:
  - Strict separation of concerns between Flask backend and React frontend.
  - Zero tolerance for hardcoded single-year database structures.
  - Exact adherence to the dark academic design system (#050506 base, #32DC5C primary green, #FF6268 destructive red).
  - Explicit observational language policy (strictly avoid causal claims such as "poor attendance caused poor marks").

---

## 2. Target System Architecture

```
                                  +---------------------------------------+
                                  |            CLIENT BROWSER             |
                                  +---------------------------------------+
                                     /                                 \
                     (Public Routes)/                                   \(Authenticated Routes)
                                   v                                     v
                 +-------------------------------+       +-------------------------------+
                 |    PUBLIC DEPARTMENT PORTAL   |       |   HOD / ADMIN INTELLIGENCE    |
                 | - Department Identity         |       | - Department Analytics        |
                 | - Faculty Showcase            |       | - Year & Section Comparison   |
                 | - Department Events           |       | - Student Drill-down & SGPA   |
                 | - Student Achievements        |       | - Subject Attendance Mapping  |
                 | - Announcements / Gallery     |       | - Risk & Insight Alerts       |
                 +-------------------------------+       +-------------------------------+
                                   \                                     /
                                    \        REST APIs (JSON)           /
                                     \  (Bearer JWT for Admin/HOD)     /
                                      v                               v
                     +---------------------------------------------------+
                     |                FLASK APPLICATION                  |
                     |                 (Python 3.11+)                    |
                     +---------------------------------------------------+
                     | [api/public]   [api/auth]      [api/analytics]    |
                     | [api/students] [api/uploads]   [api/insights]     |
                     +---------------------------------------------------+
                     |               SERVICES & LOGIC LAYER              |
                     | - AnalyticsEngine  - IngestionValidator           |
                     | - ComparisonLogic  - AlertService                 |
                     +---------------------------------------------------+
                                              |
                                     SQLAlchemy ORM
                                              v
                     +---------------------------------------------------+
                     |             PostgreSQL / Supabase DB              |
                     +---------------------------------------------------+
```

---

## 3. Proposed Folder Architecture

```
student-management/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py                # Flask app factory, extension registration
│   │   ├── config.py                  # Environment-specific configs (Dev, Prod, Test)
│   │   ├── extensions.py              # db, migrate, jwt, cors instances
│   │   ├── models/                    # Unified SQLAlchemy entity models
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # Admin / HOD users and roles
│   │   │   ├── student.py             # Unified Student entity (2nd, 3rd, 4th year)
│   │   │   ├── academic.py            # Semesters, Subjects, Marks, Grades, SGPA/CGPA
│   │   │   ├── attendance.py          # Subject-wise attendance records
│   │   │   ├── department.py          # Faculty, Events, News, Achievements
│   │   │   └── config_model.py        # Configurable delta & risk thresholds
│   │   ├── api/                       # Blueprints & REST Controllers
│   │   │   ├── __init__.py
│   │   │   ├── auth_bp.py             # /api/v1/auth (login, refresh, me)
│   │   │   ├── public_bp.py           # /api/v1/public (about, faculty, events, news)
│   │   │   ├── students_bp.py         # /api/v1/students (student directory & drill-down)
│   │   │   ├── academics_bp.py        # /api/v1/academics (subjects, marks, semesters)
│   │   │   ├── attendance_bp.py       # /api/v1/attendance (subject attendance queries)
│   │   │   ├── analytics_bp.py        # /api/v1/analytics (dept, year, section, trends)
│   │   │   ├── insights_bp.py         # /api/v1/insights (students/subjects needing focus)
│   │   │   └── uploads_bp.py          # /api/v1/uploads (CSV/Excel preview, validation, import)
│   │   ├── services/                  # Business & Statistical Logic Layer
│   │   │   ├── analytics_service.py   # Aggregations, SGPA/CGPA delta, stable thresholds
│   │   │   ├── comparison_service.py  # Subject-by-subject semester delta mapping
│   │   │   ├── insight_service.py     # Multi-factor risk queries & attention flags
│   │   │   └── ingestion_service.py   # File parsing, schema validation, transactional commit
│   │   └── utils/
│   │       ├── decorators.py          # @role_required, @jwt_required
│   │       ├── validators.py          # Input schema and range validation
│   │       └── response.py            # Unified standard envelope formatter
│   ├── migrations/                    # Alembic migration scripts
│   ├── requirements.txt               # Flask, Flask-SQLAlchemy, Flask-JWT-Extended, pandas, openpyxl, psycopg2-binary
│   ├── run.py                         # Local backend development runner
│   └── .env.example                   # Environment configuration template
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/                    # Icons, logos, public media
│   │   ├── components/
│   │   │   ├── common/                # Reusable UI primitives
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Card.jsx
│   │   │   │   ├── Badge.jsx          # Success (Green), Danger (Red), Neutral (Dark)
│   │   │   │   ├── Modal.jsx
│   │   │   │   ├── DataTable.jsx      # Sortable, filterable academic tables
│   │   │   │   ├── MetricCard.jsx     # High-impact stat displays
│   │   │   │   └── AlertBanner.jsx
│   │   │   ├── layout/
│   │   │   │   ├── PublicNavbar.jsx
│   │   │   │   ├── PublicFooter.jsx
│   │   │   │   ├── AdminSidebar.jsx
│   │   │   │   ├── AdminHeader.jsx    # Global filters: Year [2nd | 3rd | 4th], Section, Sem
│   │   │   │   └── Breadcrumbs.jsx
│   │   │   └── charts/                # Minimalist, high-contrast dark charts
│   │   │       ├── SgpaTrendChart.jsx
│   │   │       ├── SubjectComparisonBar.jsx
│   │   │       ├── AttendanceScatterPlot.jsx
│   │   │       └── DeltaDistributionChart.jsx
│   │   ├── pages/
│   │   │   ├── public/
│   │   │   │   ├── HomePage.jsx
│   │   │   │   ├── AboutPage.jsx
│   │   │   │   ├── FacultyPage.jsx
│   │   │   │   ├── EventsPage.jsx
│   │   │   │   ├── AchievementsPage.jsx
│   │   │   │   ├── AnnouncementsPage.jsx
│   │   │   │   └── ContactPage.jsx
│   │   │   └── admin/
│   │   │       ├── LoginPage.jsx
│   │   │       ├── DepartmentDashboard.jsx
│   │   │       ├── YearSectionView.jsx
│   │   │       ├── StudentDetailView.jsx
│   │   │       ├── AttendanceMatrixView.jsx
│   │   │       ├── ProblemIdentificationView.jsx
│   │   │       ├── DataUploadView.jsx
│   │   │       └── DepartmentReportsView.jsx
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   └── AcademicFilterContext.jsx # Global active year/section/semester state
│   │   ├── services/
│   │   │   ├── api.js                 # Axios instance with auth interceptor
│   │   │   ├── authService.js
│   │   │   ├── analyticsService.js
│   │   │   ├── studentService.js
│   │   │   ├── uploadService.js
│   │   │   └── publicService.js
│   │   ├── styles/
│   │   │   ├── variables.css          # Color tokens, typography, radii, elevations
│   │   │   └── index.css              # Global dark resets and utilities
│   │   ├── App.jsx                    # Routing configuration
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
└── docs/
    └── PHASE_0_ARCHITECTURE_REPORT.md
```

---

## 4. Proposed Database Entities & Relational Design

The database schema strictly adheres to a **unified student model** with normalized academic and attendance mappings, avoiding separate tables for individual academic years.

```
+---------------------------------------------------------------------------------+
|                                    USERS                                        |
+---------------------------------------------------------------------------------+
| id (UUID, PK)                                                                   |
| email (VARCHAR, UNIQUE)                                                         |
| password_hash (VARCHAR)                                                         |
| role (VARCHAR: 'ADMIN', 'HOD', 'FACULTY')                                       |
| full_name (VARCHAR)                                                             |
| is_active (BOOLEAN)                                                             |
| created_at (TIMESTAMP)                                                          |
+---------------------------------------------------------------------------------+
                                       |
                                       | manages
                                       v
+---------------------------------------------------------------------------------+
|                                  STUDENTS                                       |
+---------------------------------------------------------------------------------+
| id (UUID, PK)                                                                   |
| roll_number (VARCHAR, UNIQUE)                                                   |
| name (VARCHAR)                                                                  |
| branch (VARCHAR, e.g., 'CSE', 'ECE')                                            |
| academic_year (INTEGER: 2, 3, 4)                                                |
| section (VARCHAR: 'A', 'B', 'C', 'D')                                           |
| current_semester (INTEGER: 1 to 8)                                              |
| admission_batch (VARCHAR, e.g., '2023-2027')                                     |
| status (VARCHAR: 'ACTIVE', 'DETAINED', 'ALUMNI')                                |
| created_at (TIMESTAMP)                                                          |
+---------------------------------------------------------------------------------+
         |                                                 |
         | 1:N                                             | 1:N
         v                                                 v
+--------------------------------------+  +---------------------------------------+
|      STUDENT_SEMESTER_SUMMARIES      |  |         SUBJECT_PERFORMANCES          |
+--------------------------------------+  +---------------------------------------+
| id (UUID, PK)                        |  | id (UUID, PK)                         |
| student_id (FK -> students.id)       |  | student_id (FK -> students.id)        |
| semester_number (INTEGER: 1 to 8)    |  | semester_number (INTEGER: 1 to 8)     |
| academic_session (VARCHAR: '2024-25')|  | subject_id (FK -> subjects.id)        |
| sgpa (NUMERIC(4,2))                  |  | internal_marks (NUMERIC(5,2))         |
| cgpa (NUMERIC(4,2))                  |  | external_marks (NUMERIC(5,2))         |
| total_credits (NUMERIC(4,1))         |  | total_marks (NUMERIC(5,2))            |
| overall_attendance_pct (NUMERIC(5,2))|  | grade (VARCHAR: 'O', 'A+', 'A', etc.) |
| prev_sgpa (NUMERIC(4,2))             |  | grade_point (NUMERIC(4,2))            |
| sgpa_delta (NUMERIC(4,2))            |  | attendance_pct (NUMERIC(5,2))         |
| status ('IMPROVED','DECLINED','STABLE|  | classes_attended (INTEGER)            |
| UNIQUE(student_id, semester_number)  |  | total_classes (INTEGER)               |
+--------------------------------------+  | UNIQUE(student_id, sem, subject_id)   |
                                          +---------------------------------------+
                                                             |
                                                             | N:1
                                                             v
                                          +---------------------------------------+
                                          |               SUBJECTS                |
                                          +---------------------------------------+
                                          | id (UUID, PK)                         |
                                          | subject_code (VARCHAR, UNIQUE)        |
                                          | subject_name (VARCHAR)                |
                                          | department (VARCHAR)                  |
                                          | academic_year (INTEGER: 2, 3, 4)      |
                                          | semester_number (INTEGER: 1 to 8)     |
                                          | credits (NUMERIC(3,1))                |
                                          | is_elective (BOOLEAN)                 |
                                          +---------------------------------------+

+---------------------------------------------------------------------------------+
|                       SYSTEM_ANALYTICS_THRESHOLDS                               |
+---------------------------------------------------------------------------------+
| id (INTEGER, PK)                                                                |
| stable_delta_threshold (NUMERIC, default: 0.15)                                 |
| attendance_risk_threshold (NUMERIC, default: 75.0)                              |
| academic_critical_decline (NUMERIC, default: -0.75)                             |
| updated_at (TIMESTAMP)                                                          |
+---------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------+
|                              PUBLIC PORTAL TABLES                               |
+---------------------------------------------------------------------------------+
| FACULTY_MEMBERS   : id, name, designation, qualification, email, photo_url, ord |
| EVENTS            : id, title, description, event_date, category, image_url     |
| ANNOUNCEMENTS     : id, title, content, category, is_pinned, publish_date       |
| ACHIEVEMENTS      : id, title, student_names, category, description, date, img  |
+---------------------------------------------------------------------------------+
```

---

## 5. Proposed RBAC (Role-Based Access Control) Model

| Role | Public Website | Department Analytics | Student CGPA & Data | Upload Data | Reports & Settings |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **PUBLIC (Visitor)** | Read Only | ❌ Forbidden | ❌ Forbidden | ❌ Forbidden | ❌ Forbidden |
| **HOD / ADMIN** | Read/Edit CMS | Full Access | Full Access | Full Access | Full Access |
| **FACULTY (Future)**| Read Only | Assigned Year/Sec | Assigned Students | Attendance Entry | View Scoped |
| **STUDENT (Future)**| Read Only | ❌ Forbidden | Own Profile Only | ❌ Forbidden | Download Own |

### Security Guarantees:
1. **Zero Public Leakage**: The public API blueprint (`/api/v1/public/*`) connects exclusively to public content tables. It has no physical joins or queries to `students`, `subject_performances`, or `student_semester_summaries`.
2. **Backend Decorator Enforcement**: Private endpoints are guarded with `@jwt_required()` and `@role_required(['ADMIN', 'HOD'])`.
3. **Password Security**: Strong hashing using `argon2` or `bcrypt`. Short-lived access JWT tokens with secure HTTP-only refresh tokens.

---

## 6. Proposed API Specification (REST)

### 6.1 Public Endpoints (No Auth Required)
- `GET /api/v1/public/department-info` — Department summary, vision, mission, HOD message.
- `GET /api/v1/public/faculty` — Faculty list with designations, qualifications, and profile images.
- `GET /api/v1/public/events` — Upcoming and past department workshops, hackathons, and symposiums.
- `GET /api/v1/public/achievements` — Student competition winners, research publications, awards.
- `GET /api/v1/public/announcements` — Department notices, circulars, and exam timetables.

### 6.2 Authentication
- `POST /api/v1/auth/login` — Returns JWT Access Token + Refresh Token for verified credentials.
- `POST /api/v1/auth/refresh` — Refreshes expired access tokens.
- `GET /api/v1/auth/me` — Returns current authenticated user session and role.

### 6.3 HOD Analytics Hierarchy & Insights
- `GET /api/v1/analytics/department`
  - Query params: `?academic_year=2&semester=3`
  - Response: Aggregate metrics (Total students, average SGPA, average attendance %, count improved/declined/stable, section-wise comparison summaries).
- `GET /api/v1/analytics/sections`
  - Query params: `?academic_year=2&section=A&semester=3`
  - Response: Section-specific average SGPA, attendance distribution, student list with delta indicators.
- `GET /api/v1/analytics/students/<student_id>`
  - Response: Comprehensive student academic profile:
    - Personal & batch metadata.
    - Semester SGPA timeline & CGPA trajectory.
    - Subject-wise breakdown: Marks, Grade, Grade Points, and Subject Attendance %.
    - Subject delta mapping (Sem N vs Sem N-1).
    - Calculated status tags (`IMPROVED`, `DECLINED`, `STABLE`, `ATTENDANCE_RISK`).
- `GET /api/v1/analytics/subjects`
  - Query params: `?academic_year=2&semester=3`
  - Response: Subject-level average marks, failure rate, average attendance, and subject-wise improvement/decline delta.
- `GET /api/v1/analytics/attendance-correlation`
  - Query params: `?academic_year=2&semester=3&subject_id=<id>`
  - Response: Observational data points mapping subject attendance quartiles to average performance bands.
- `GET /api/v1/insights/alerts`
  - Query params: `?academic_year=2&section=all`
  - Response: Prioritized list of:
    - Students with severe SGPA decline (e.g., delta < -0.75).
    - Students with multiple subject grade drops.
    - Students with attendance < 75%.
    - Subjects exhibiting an aggregate negative performance shift.

### 6.4 Data Ingestion & Validation
- `POST /api/v1/uploads/preview`
  - Multipart file (`.csv`, `.xlsx`).
  - Request fields: `academic_year`, `section`, `semester_number`, `data_type` ('MARKS_ONLY', 'ATTENDANCE_ONLY', 'COMBINED').
  - Action: Validates columns, parses rows, detects duplicates, checks valid roll numbers, verifies marks range (0-100) and attendance range (0-100%).
  - Response: `{ total_rows: 60, valid_rows: 58, errors: [{ row: 12, column: "Attendance", error: "Value 105 exceeds maximum 100%" }] }`
- `POST /api/v1/uploads/confirm`
  - Commits validated batch into the database within an atomic transaction and automatically triggers the analytical aggregation pipeline.

---

## 7. Frontend Design System & Component Architecture

### 7.1 Strict Color Tokens
```css
:root {
  --color-primary: #32DC5C;     /* Action buttons, improvements, positive delta, active state */
  --color-destructive: #FF6268; /* Academic decline, low attendance alert, errors */
  --color-bg-base: #050506;     /* Main window background */
  --color-bg-card: #0F0F11;     /* Card background */
  --color-bg-secondary: #18181C;/* Secondary panels, table headers */
  --color-bg-accent: #1C1C20;   /* Hover states, active tabs */
  --color-border: #242426;      /* Subtle borders */
  --color-text-main: #F4F4F5;   /* High contrast readable text */
  --color-text-muted: #8E8E93;  /* Metadata, secondary labels */
}
```

### 7.2 UI/UX Principles
- **Visual Restraint**: Primary green (#32DC5C) is applied with strict intentionality—never as large background washes, but as crisp badges, chart highlight bars, positive trend indicators (`+0.62`), and primary action triggers. The interface remains predominantly deep black (#050506).
- **Academic Density**: Tables and metrics provide dense, readable information without oversized padding, puffy cards, or cartoonish rounded corners.
- **Context Preservation**: The HOD can change the global year filter (`[2nd Year ▼]`) or section filter from any view without losing place or context.

### 7.3 Workspace Skills & Design Contract Alignment (`.agents/`)
The frontend development strictly incorporates the three workspace skills located in `.agents/skills/`:

1. **`no-ai-design-slop` Quality Gate**:
   - **No Cliché Layouts**: Prohibit the generic "SaaS card kit" (everything chopped into identical rounded cards with identical shadows).
   - **No Gratuitous Accents**: Never apply acid-green washes or glowing borders merely for decoration. The green is reserved strictly for positive delta, improved status, and primary calls to action.
   - **No Artificial Fillers**: No generic tracked-out ALL-CAPS eyebrow labels above every heading, no decorative middle-dot tags (`A · B · C`), no stock SVG fillers. Every visual element must convey concrete academic meaning.
   - **Removal Test**: For every visual embellishment, apply the removal test: if removing it preserves clarity and functionality, eliminate it.

2. **`frontend-design` Discipline**:
   - **Subject-Grounded Hierarchy**: Typography and layout are modeled directly after high-density academic and institutional dashboards.
   - **Deliberate Typography**: Restrict to 1–2 distinct typefaces with clear optical scale. Line lengths under 80 characters for textual copy.
   - **Action-Oriented Verbs**: Button and action labeling uses active, unambiguous verbs ("Upload Semester Results", "Export Section Report", "Save Thresholds").
   - **Meaningful Structure**: Dividers, borders, and numbering are only used when representing real structural hierarchies or chronological sequences.

3. **`antigravity-design-expert` Interaction Standards**:
   - **Purposeful Micro-interactions**: Smooth state transitions (minimum `0.3s ease-out`).
   - **Performance-First GPU Offloading**: Use `will-change: transform` on animated elements. Avoid heavy continuous blur filters or animating expensive properties (`box-shadow`, `filter`).
   - **Accessibility**: Full respect for `prefers-reduced-motion: reduce`, ensuring instantaneous static rendering for users requiring reduced motion.


---

## 8. Phase 1–5 Implementation Roadmap

### Phase 1: Foundation + Public Department Website
- Initialize backend Flask app factory, PostgreSQL database connection, and configuration environments.
- Establish backend database migrations (Alembic) with Public Portal schemas (`faculty_members`, `events`, `achouncements`, `achievements`) and Authentication (`users`).
- Build and seed the authentication system with HOD credentials.
- Build modern React public departmental portal showcasing:
  - Hero with Department Profile & Vision
  - Faculty directory with modal profiles
  - Department events & workshops timeline
  - Student achievements gallery
  - News and circulars
  - Direct login entrance to the HOD Intelligence Portal.
- Deliverable: Fully navigable public website + secure authentication gateway.

### Phase 2: Student + Academic + Attendance Data Management
- Create unified database entities: `students`, `subjects`, `subject_performances`, `student_semester_summaries`.
- Implement robust CSV/Excel Ingestion Engine:
  - Server-side parsing with `pandas` / `openpyxl`.
  - Strict two-stage ingestion flow: Ingestion Preview -> Error Log -> Transactional Confirmation.
  - Automated calculation of SGPA, semester deltas, and subject performance records.
- Build HOD Data Upload UI with drag-and-drop file upload, real-time error tables, and preview reconciliation.
- Deliverable: Reliable, transactional data onboarding system with error prevention.

### Phase 3: Academic Analytics + Semester & Subject Comparison Engine
- Implement analytical computation services:
  - Year-level and Section-level aggregations.
  - Subject-by-subject performance deltas across semesters.
  - Subject-wise attendance distribution and performance grouping.
- Build HOD Department & Section Dashboards:
  - Department Overview with key KPIs (Total Students, Mean SGPA, Attendance %, Improved/Declined/Stable splits).
  - Section Comparison Bar & Trend Views.
  - Student Detail Drill-down with Subject-wise Attendance vs. Performance cards and historical semester trajectory.
- Deliverable: Hierarchical analytical dashboard from Department down to individual Student.

### Phase 4: Problem Identification & Intelligent Insights
- Develop the Problem Identification Service:
  - Detection of multi-subject grade drop patterns.
  - Identification of low attendance outliers (< 75%).
  - Flagging subjects with high failure or sharp decline rates.
  - Observational correlation views between attendance bands and performance.
- Build "Needs Attention" Priority View for the HOD:
  - Actionable student watchlist filterable by severity.
  - Section attention score.
  - Subject remediation alerts.
- Deliverable: Proactive academic intelligence dashboard highlighting areas of concern.

### Phase 5: Integration + Reports + Security Audit + Deployment Prep
- Comprehensive End-to-End verification across all academic years (2nd, 3rd, 4th).
- Exportable HOD Reports: PDF summaries of section performance and student watchlist reports.
- Security hardening:
  - API rate limiting, sanitization, strict SQL parameterization.
  - JWT token rotation and expiry audits.
- Final documentation and deployment instructions (Docker / Gunicorn / Nginx / Supabase PostgreSQL).
- Deliverable: Production-ready academic intelligence and department management platform.

---

## 9. Risk Analysis & Technical Mitigation

| Identified Risk | Impact | Architectural Mitigation |
| :--- | :---: | :--- |
| **Inconsistent Excel/CSV formats** uploaded by staff | High | Two-stage upload engine (Preview + Error Table + Explicit User Confirmation). Strict schema checks before database writes. |
| **Hardcoding to 2nd Year** during initial focus | Critical | Unified `students` table with `academic_year` integer column; global filter state on frontend; API parameterized by year. |
| **Causal Claim Misinterpretation** | Medium | Analytical UI and reports strictly use observational wording ("Attendance is associated with...", "Lower attendance cohort exhibited lower average grade points"). |
| **Data Privacy & Accidental Exposure** | Critical | Physical separation of public and academic API endpoints. Strict `@role_required` guards on all academic blueprints. |

---

## 10. Exact Next Steps for Phase 1 Execution

When Phase 1 implementation begins:
1. Initialize the backend directory structure (`backend/app/`, `backend/requirements.txt`, `backend/run.py`).
2. Initialize the React frontend with Vite in `frontend/` and configure the exact CSS design system variables.
3. Establish PostgreSQL database connection (local Postgres or Supabase connection string).
4. Implement Public Department models, seed data for Department, Faculty, Events, and Announcements.
5. Implement the Public Department Website components and HOD Login Gateway.
6. Verify public endpoints do not expose any student records.
