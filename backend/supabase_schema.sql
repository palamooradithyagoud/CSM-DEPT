-- ============================================================================
-- SUPABASE POSTGRESQL PRODUCTION SCHEMA
-- Student Academic Performance & Department Management System
-- College of Engineering & Technology | Department of Computer Science
-- Project Ref: wehwepjchdclhwsaxadg
-- ============================================================================

-- 0. Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. AUTHENTICATION & RBAC
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'HOD',
    department VARCHAR(80) NOT NULL DEFAULT 'Computer Science & Engineering',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITHOUT TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ============================================================================
-- 2. PUBLIC DEPARTMENT PORTAL TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS department_info (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(150) NOT NULL DEFAULT 'Department of Computer Science & Engineering',
    short_code VARCHAR(20) NOT NULL DEFAULT 'CSE',
    tagline VARCHAR(255) DEFAULT 'Empowering Future Innovators & Academic Excellence',
    about TEXT NOT NULL,
    vision TEXT NOT NULL,
    mission TEXT NOT NULL,
    hod_name VARCHAR(120) NOT NULL DEFAULT 'Dr. M. A. Jabbar',
    hod_designation VARCHAR(120) DEFAULT 'Professor & Head of Department',
    hod_qualification VARCHAR(120) DEFAULT 'Ph.D. (CSE), M.Tech, B.Tech, SMIEEE',
    hod_message TEXT NOT NULL,
    hod_photo_url VARCHAR(255),
    contact_email VARCHAR(120) DEFAULT 'hod.cse@college.edu',
    contact_phone VARCHAR(50) DEFAULT '+91 40 2345 6789',
    office_location VARCHAR(150) DEFAULT 'Block-A, Room 302, Academic Enclave',
    established_year INTEGER DEFAULT 2008
);

CREATE TABLE IF NOT EXISTS faculty_members (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    designation VARCHAR(120) NOT NULL,
    qualification VARCHAR(120) NOT NULL,
    specialization VARCHAR(200) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(50),
    experience_years INTEGER DEFAULT 5,
    bio TEXT,
    photo_url VARCHAR(255),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_faculty_order ON faculty_members(display_order);

CREATE TABLE IF NOT EXISTS department_events (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(80) NOT NULL,
    event_date DATE NOT NULL,
    location VARCHAR(150) NOT NULL,
    image_url VARCHAR(255),
    is_featured BOOLEAN DEFAULT FALSE,
    is_upcoming BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_events_date ON department_events(event_date);

CREATE TABLE IF NOT EXISTS student_achievements (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    student_names VARCHAR(255) NOT NULL,
    category VARCHAR(80) NOT NULL,
    event_name VARCHAR(200) NOT NULL,
    award VARCHAR(120) NOT NULL,
    achievement_date DATE NOT NULL,
    description TEXT,
    image_url VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_achievements_date ON student_achievements(achievement_date);

CREATE TABLE IF NOT EXISTS announcements (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'Circular',
    is_pinned BOOLEAN DEFAULT FALSE,
    publish_date DATE DEFAULT CURRENT_DATE
);

CREATE INDEX IF NOT EXISTS idx_announcements_pinned ON announcements(is_pinned, publish_date DESC);

-- ============================================================================
-- 3. ACADEMIC HIERARCHY TABLES
-- ============================================================================

-- BATCH (e.g. 2025-2029)
CREATE TABLE IF NOT EXISTS batches (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    start_year INTEGER NOT NULL,
    end_year INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_batches_name ON batches(name);

-- ACADEMIC YEAR (1st Year, 2nd Year...)
CREATE TABLE IF NOT EXISTS academic_years (
    id VARCHAR(36) PRIMARY KEY,
    batch_id VARCHAR(36) NOT NULL REFERENCES batches(id) ON DELETE CASCADE,
    year_number INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    calendar_year VARCHAR(30),
    is_current BOOLEAN DEFAULT FALSE,
    CONSTRAINT uq_batch_year_number UNIQUE (batch_id, year_number)
);

CREATE INDEX IF NOT EXISTS idx_academic_years_batch ON academic_years(batch_id);

-- SEMESTER (Semester 1 through 8)
CREATE TABLE IF NOT EXISTS semesters (
    id VARCHAR(36) PRIMARY KEY,
    academic_year_id VARCHAR(36) NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
    semester_number INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,
    CONSTRAINT uq_ay_semester_number UNIQUE (academic_year_id, semester_number)
);

CREATE INDEX IF NOT EXISTS idx_semesters_ay ON semesters(academic_year_id);

-- SECTION (A, B, C...)
CREATE TABLE IF NOT EXISTS sections (
    id VARCHAR(36) PRIMARY KEY,
    semester_id VARCHAR(36) NOT NULL REFERENCES semesters(id) ON DELETE CASCADE,
    name VARCHAR(20) NOT NULL,
    room_number VARCHAR(50),
    CONSTRAINT uq_semester_section_name UNIQUE (semester_id, name)
);

CREATE INDEX IF NOT EXISTS idx_sections_sem ON sections(semester_id);

-- ============================================================================
-- 4. STUDENTS & CURRICULUM
-- ============================================================================

-- STUDENT
CREATE TABLE IF NOT EXISTS students (
    id VARCHAR(36) PRIMARY KEY,
    roll_number VARCHAR(40) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    batch_id VARCHAR(36) NOT NULL REFERENCES batches(id),
    current_section_id VARCHAR(36) REFERENCES sections(id),
    email VARCHAR(120),
    phone VARCHAR(40),
    gender VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_students_roll ON students(roll_number);
CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);
CREATE INDEX IF NOT EXISTS idx_students_batch ON students(batch_id);
CREATE INDEX IF NOT EXISTS idx_students_section ON students(current_section_id);

-- SUBJECT
CREATE TABLE IF NOT EXISTS subjects (
    id VARCHAR(36) PRIMARY KEY,
    semester_id VARCHAR(36) NOT NULL REFERENCES semesters(id) ON DELETE CASCADE,
    code VARCHAR(40) NOT NULL,
    name VARCHAR(150) NOT NULL,
    short_name VARCHAR(40),
    credits FLOAT DEFAULT 3.0,
    subject_type VARCHAR(30) DEFAULT 'THEORY',
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT uq_semester_subject_code UNIQUE (semester_id, code)
);

CREATE INDEX IF NOT EXISTS idx_subjects_sem ON subjects(semester_id);
CREATE INDEX IF NOT EXISTS idx_subjects_code ON subjects(code);

-- ============================================================================
-- 5. ACADEMIC RECORDS & PERFORMANCE
-- ============================================================================

-- ATTENDANCE RECORDS (Section-wise)
CREATE TABLE IF NOT EXISTS attendance_records (
    id VARCHAR(36) PRIMARY KEY,
    student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    section_id VARCHAR(36) NOT NULL REFERENCES sections(id),
    subject_id VARCHAR(36) NOT NULL REFERENCES subjects(id),
    semester_id VARCHAR(36) NOT NULL REFERENCES semesters(id),
    percentage FLOAT NOT NULL,
    classes_attended INTEGER,
    total_classes INTEGER,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_sem_subject_attendance UNIQUE (student_id, semester_id, subject_id)
);

CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance_records(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_sem ON attendance_records(semester_id);
CREATE INDEX IF NOT EXISTS idx_attendance_sec ON attendance_records(section_id);

-- ASSESSMENT RECORDS (Internal Mids)
CREATE TABLE IF NOT EXISTS assessment_records (
    id VARCHAR(36) PRIMARY KEY,
    student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    section_id VARCHAR(36) NOT NULL REFERENCES sections(id),
    subject_id VARCHAR(36) NOT NULL REFERENCES subjects(id),
    semester_id VARCHAR(36) NOT NULL REFERENCES semesters(id),
    assessment_type VARCHAR(20) NOT NULL,
    marks_obtained FLOAT,
    max_marks FLOAT DEFAULT 30.0,
    status VARCHAR(30) DEFAULT 'AVAILABLE',
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_sem_subj_assessment UNIQUE (student_id, semester_id, subject_id, assessment_type)
);

CREATE INDEX IF NOT EXISTS idx_assessments_student ON assessment_records(student_id);
CREATE INDEX IF NOT EXISTS idx_assessments_sem ON assessment_records(semester_id);

-- SEMESTER RESULTS (Overall End-Semester Exam)
CREATE TABLE IF NOT EXISTS semester_results (
    id VARCHAR(36) PRIMARY KEY,
    student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    section_id VARCHAR(36) NOT NULL REFERENCES sections(id),
    subject_id VARCHAR(36) NOT NULL REFERENCES subjects(id),
    semester_id VARCHAR(36) NOT NULL REFERENCES semesters(id),
    internal_marks FLOAT,
    external_marks FLOAT,
    total_marks FLOAT,
    grade VARCHAR(10),
    grade_point FLOAT,
    credits_earned FLOAT,
    result_status VARCHAR(20) DEFAULT 'PASSED',
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_sem_subject_result UNIQUE (student_id, semester_id, subject_id)
);

CREATE INDEX IF NOT EXISTS idx_results_student ON semester_results(student_id);
CREATE INDEX IF NOT EXISTS idx_results_sem ON semester_results(semester_id);
CREATE INDEX IF NOT EXISTS idx_results_status ON semester_results(result_status);

-- STUDENT SEMESTER SUMMARIES (Official SGPA / CGPA)
CREATE TABLE IF NOT EXISTS student_semester_summaries (
    id VARCHAR(36) PRIMARY KEY,
    student_id VARCHAR(36) NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    semester_id VARCHAR(36) NOT NULL REFERENCES semesters(id),
    section_id VARCHAR(36) NOT NULL REFERENCES sections(id),
    sgpa FLOAT,
    cgpa FLOAT,
    total_credits FLOAT,
    is_official BOOLEAN DEFAULT TRUE,
    CONSTRAINT uq_student_semester_summary UNIQUE (student_id, semester_id)
);

CREATE INDEX IF NOT EXISTS idx_summaries_student ON student_semester_summaries(student_id);
CREATE INDEX IF NOT EXISTS idx_summaries_sem ON student_semester_summaries(semester_id);
CREATE INDEX IF NOT EXISTS idx_summaries_sgpa ON student_semester_summaries(sgpa);
CREATE INDEX IF NOT EXISTS idx_summaries_cgpa ON student_semester_summaries(cgpa);

-- ============================================================================
-- 6. AUDIT & UPLOAD HISTORY
-- ============================================================================

CREATE TABLE IF NOT EXISTS upload_history (
    id VARCHAR(36) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    uploaded_by VARCHAR(120) NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(36) NOT NULL REFERENCES batches(id),
    academic_year_id VARCHAR(36) NOT NULL REFERENCES academic_years(id),
    semester_id VARCHAR(36) NOT NULL REFERENCES semesters(id),
    section_id VARCHAR(36) REFERENCES sections(id),
    data_type VARCHAR(30) NOT NULL,
    total_rows INTEGER DEFAULT 0,
    valid_rows INTEGER DEFAULT 0,
    invalid_rows INTEGER DEFAULT 0,
    duplicates_count INTEGER DEFAULT 0,
    status VARCHAR(30) DEFAULT 'VALIDATED',
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_upload_sem ON upload_history(semester_id);
CREATE INDEX IF NOT EXISTS idx_upload_batch ON upload_history(batch_id);
CREATE INDEX IF NOT EXISTS idx_upload_time ON upload_history(uploaded_at DESC);

-- ============================================================================
-- 7. SUPABASE ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE department_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE faculty_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE department_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_years ENABLE ROW LEVEL SECURITY;
ALTER TABLE semesters ENABLE ROW LEVEL SECURITY;
ALTER TABLE sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE semester_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_semester_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE upload_history ENABLE ROW LEVEL SECURITY;

-- Service Role (Full Access for backend operations)
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS "service_role_all" ON %I;', t);
        EXECUTE format('CREATE POLICY "service_role_all" ON %I FOR ALL TO service_role USING (true) WITH CHECK (true);', t);
        EXECUTE format('DROP POLICY IF EXISTS "public_read_all" ON %I;', t);
        EXECUTE format('CREATE POLICY "public_read_all" ON %I FOR SELECT TO anon, authenticated USING (true);', t);
    END LOOP;
END $$;

-- Reload Supabase PostgREST Schema Cache
NOTIFY pgrst, 'reload schema';
