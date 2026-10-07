# Department of Computer Science & Engineering
## Student Academic Performance & Department Management System

[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](#)
[![Tests: 81/81 Passing](https://img.shields.io/badge/Tests-81%2F81%20Passed-brightgreen.svg)](#)
[![Stack: React + Flask + PostgreSQL](https://img.shields.io/badge/Stack-React%20%7C%20Flask%20%7C%20PostgreSQL-blue.svg)](#)

---

## 1. Overview

The **Student Academic Performance & Department Management System** is a unified, institutional-grade academic portal built specifically for the **Department of Computer Science & Engineering** under the leadership of **Dr. M. A. Jabbar, Professor & HOD**.

The system merges a polished, public-facing departmental portal with a secure, high-precision academic analytics, diagnostics, problem detection, and multi-format reporting suite for departmental leadership.

---

## 2. Core Capabilities

- **Public Department Portal**: Mission, vision, NBA/NAAC accreditations, faculty directory with specialization filters, research publications, campus gallery, circulars, and departmental announcements.
- **Academic Hierarchy Management**: True 4-tier college progression (`Batch` $\to$ `Academic Year` $\to$ `Semester` $\to$ `Section`).
- **Curriculum Architecture**:
  - Each cohort batch spans **4 Academic Years**.
  - Each academic year spans **exactly 2 Semesters** (Semesters 1 through 8).
  - Every semester contains **completely distinct, non-overlapping subjects** with course codes, lecture credits, lab classifications, and syllabus tracking.
  - Configurable sections (A, B, C) per semester.
- **Academic Data Ingestion**: Bulk spreadsheet ingestion (`.xlsx`, `.csv`) with column auto-mapping, row-level validation, atomic transactions, and duplicate resolution.
- **Academic Analytics & Comparisons**: Real-time cohort KPIs, SGPA/CGPA distribution, subject pass percentages, multi-semester comparative trajectory, and section benchmarks.
- **Deterministic Problem Identification**: Rule-based detection algorithms identifying at-risk students (attendance deficits, grade declines, repeated subject failures) without synthetic/hallucinatory scores.
- **Institutional Multi-Format Reporting Engine**: Generates branded **PDF documents** (two-pass pagination with ReportLab), styled **Excel spreadsheets** (openpyxl), and **RFC 4180 CSV** datasets across 5 operational scopes:
  1. Department Executive Summary
  2. Section Performance Roster
  3. Student Comprehensive Dossier
  4. Subject Course Diagnostics
  5. Academic Watchlist & Pedagogical Interventions
- **Disaster Recovery & Database Backups**: Automated snapshot scripts with SHA-256 cryptographic checksum verification (`backend/scripts/backup_restore.py`).

---

## 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite, Lucide Icons, Vanilla CSS Design System (`#050506`, `#0F0F11`, `#32DC5C`, `#FF6268`) |
| **Backend** | Python 3.14+, Flask 3.1+, Flask-JWT-Extended, Flask-SQLAlchemy, Flask-CORS |
| **Database** | PostgreSQL / Supabase PostgreSQL (production) with local SQLite fallback |
| **Reporting** | ReportLab 4.4+ (PDF with `NumberedCanvas`), openpyxl 3.1+ (Excel), Python CSV (UTF-8 BOM) |
| **Security** | Role-Based Access Control (RBAC: `HOD`, `ADMIN`, `FACULTY`, `STUDENT`), Argon2/Bcrypt Password Hashing, JWT Bearer Tokens |

---

## 4. Academic Hierarchy & Curriculum Structure

```
DEPARTMENT (Computer Science & Engineering)
  └── BATCH (e.g., 2025–2029)
        ├── 1st Year (AY 2025–2026)
        │     ├── Semester 1 (10 subjects: MAC, PPS, EW, CCDT, EP, BEE, FDS, + Labs)
        │     └── Semester 2 (10 subjects: LAAC, AC, PPPS, ESE, EDC, EVS, + Labs)
        ├── 2nd Year (AY 2026–2027)
        │     ├── Semester 3 (10 subjects: ODECV, EC, ESE, DS, DE, CAEG, PDD, + Labs)
        │     └── Semester 4 (10 subjects: DMGT, DBMS, OS, COA, JAVA, DAA, COI, + Labs)
        ├── 3rd Year (AY 2027–2028)
        │     ├── Semester 5 (8 subjects: CN, FLAT, ML, SE, WT, + Labs)
        │     └── Semester 6 (8 subjects: AI, CD, DL, CC, IPR, Industry Mini Project, + Labs)
        └── 4th Year (AY 2028–2029)
              ├── Semester 7 (7 subjects: CNS, NLP, BDA, DevOps Elective, Major Project Stage 1)
              └── Semester 8 (4 subjects: Deep RL, Autonomous Systems, MFE, Capstone Internship)
```

Each semester has **Sections A, B, and C**.

---

## 5. Project Layout

```
.
├── backend/
│   ├── app/
│   │   ├── api/                 # Flask REST Blueprints (auth, public, academic, analytics, insights, reports)
│   │   ├── models/              # SQLAlchemy Models (academic, user, public, upload)
│   │   ├── analytics/           # Analytics calculation services & aggregators
│   │   ├── insights/            # Deterministic problem detection & watchlists
│   │   └── reports/             # Multi-format report generators (PDF, Excel, CSV)
│   ├── scripts/
│   │   ├── backup_restore.py    # Database backup, restore, and SHA-256 verification
│   │   └── seed_curriculum.py   # Complete 4-year curriculum populator
│   ├── seed.py                  # Full institutional master seed script
│   ├── test_api.py              # Phase 1 automated tests (17 tests)
│   ├── test_phase2.py           # Phase 2 academic data tests (11 tests)
│   ├── test_phase3.py           # Phase 3 analytics tests (13 tests)
│   ├── test_phase4.py           # Phase 4 problem detection tests (20 tests)
│   ├── test_phase5.py           # Phase 5 reports, security & backup tests (20 tests)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── admin/           # HOD Admin workspace & navigation
│   │   │   ├── analytics/       # Analytics charts & comparison views
│   │   │   ├── insights/        # Problem watchlists & diagnostic drawers
│   │   │   ├── reports/         # Reports Hub & export configuration
│   │   │   └── public/          # Public department website components
│   │   ├── services/api.js      # Centralized HTTP & binary download client
│   │   └── styles/              # Design system styling files
│   └── package.json
└── PHASE_1_to_5_REPORTS.md      # Detailed phase completion reports
```

---

## 6. Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

### A. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your secret keys and database URI

# Seed database with master curriculum and sample data
python seed.py

# Run development server
python run.py
```
Backend runs on `http://localhost:5000`.

### B. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Frontend runs on `http://localhost:5173`.

---

## 7. Automated Testing Suite

The application includes an extensive automated test suite covering all 5 implementation phases.

To execute all 81 tests:
```bash
cd backend
.\venv\Scripts\activate

# Phase 1 Tests (17 tests)
python test_api.py

# Phases 2, 3, 4, 5 Tests (64 tests)
python -m unittest test_phase2.py test_phase3.py test_phase4.py test_phase5.py
```

### Test Coverage Summary:
- **Phase 1 (17/17)**: Public endpoints, authentication, password verification, token lifecycle, role isolation.
- **Phase 2 (11/11)**: Hierarchy cascading, CSV/Excel file validation, atomic batch ingestion, duplicate prevention.
- **Phase 3 (13/13)**: KPI calculations, CGPA distributions, multi-semester trajectories, comparative benchmarks.
- **Phase 4 (20/20)**: Attendance signals, grade drop detection, repeated failures, watchlist pagination, threshold controls.
- **Phase 5 (20/20)**: PDF/Excel/CSV binary generation, RBAC security gates, empty state handling, database transactions, backup verification, curriculum integrity.

**Total: 81 Passed, 0 Failed.**

---

## 8. Database Backups & Disaster Recovery

Run disaster recovery commands via `backend/scripts/backup_restore.py`:

```bash
cd backend
.\venv\Scripts\activate

# Create a timestamped backup with SHA-256 checksum
python scripts/backup_restore.py backup

# Verify integrity and restore from a backup
python scripts/backup_restore.py restore backups/backup_YYYYMMDD_HHMMSS.db
```

---

## 9. Environment Configuration

Example configuration (`backend/.env`):
```ini
FLASK_ENV=development
SECRET_KEY=change-in-production-institutional-secret
JWT_SECRET_KEY=change-in-production-jwt-signing-key
JWT_ACCESS_TOKEN_EXPIRES=86400

# SQLite fallback or Supabase PostgreSQL
DATABASE_URL=sqlite:///student_management.db
# DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres
```

---

## 10. Credentials for Demonstration

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **HOD / Professor** | `hod.cse@college.edu` | `HOD@cse2026` | Full Academic Portal & Leadership Hub |
| **Academic Admin** | `admin.cse@college.edu` | `Admin@cse2026` | Administrative Ingestion & Hierarchy Config |

---

## 11. Institutional Documentation

Detailed technical completion records for each milestone:
- [Phase 0: Technical Architecture Specification](PHASE_0_ARCHITECTURE_REPORT.md)
- [Phase 1: Foundation & Public Department Website](PHASE_1_COMPLETION_REPORT.md)
- [Phase 2: Student & Academic Data Management](PHASE_2_COMPLETION_REPORT.md)
- [Phase 3: Academic Analytics & Performance Engine](PHASE_3_COMPLETION_REPORT.md)
- [Phase 4: Problem Identification & Academic Insights](PHASE_4_COMPLETION_REPORT.md)
- [Phase 5: Final Productionization & Reports Hub](PHASE_5_COMPLETION_REPORT.md)
