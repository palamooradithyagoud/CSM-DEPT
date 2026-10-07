from datetime import datetime
import uuid
from app.extensions import db


class Batch(db.Model):
    """
    Cohort Batch entity (e.g., 2025-2029, 2024-2028).
    Batch != Academic Year. A batch spans 4 years of study.
    """
    __tablename__ = "batches"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)  # e.g., "2025-2029"
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Hierarchical Relationships
    academic_years = db.relationship("AcademicYear", backref="batch", lazy=True, cascade="all, delete-orphan", order_by="AcademicYear.year_number")
    students = db.relationship("Student", backref="batch", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "startYear": self.start_year,
            "endYear": self.end_year,
            "isActive": self.is_active,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "academicYearsCount": len(self.academic_years),
            "studentsCount": len(self.students),
        }


class AcademicYear(db.Model):
    """
    Study progression within a Batch (1st Year, 2nd Year, 3rd Year, 4th Year).
    """
    __tablename__ = "academic_years"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = db.Column(db.String(36), db.ForeignKey("batches.id"), nullable=False, index=True)
    year_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    name = db.Column(db.String(50), nullable=False)  # e.g., "2nd Year"
    calendar_year = db.Column(db.String(30), nullable=True)  # e.g., "2026-2027"
    is_current = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint("batch_id", "year_number", name="uq_batch_year_number"),
    )

    # Hierarchical Relationships
    semesters = db.relationship("Semester", backref="academic_year", lazy=True, cascade="all, delete-orphan", order_by="Semester.semester_number")

    def to_dict(self):
        return {
            "id": self.id,
            "batchId": self.batch_id,
            "yearNumber": self.year_number,
            "name": self.name,
            "calendarYear": self.calendar_year,
            "isCurrent": self.is_current,
            "semesters": [s.to_dict_summary() for s in self.semesters],
        }

    def to_dict_summary(self):
        return {
            "id": self.id,
            "batchId": self.batch_id,
            "yearNumber": self.year_number,
            "name": self.name,
            "calendarYear": self.calendar_year,
            "isCurrent": self.is_current,
        }


class Semester(db.Model):
    """
    Academic Semester (1 through 8) belonging to an AcademicYear.
    """
    __tablename__ = "semesters"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    academic_year_id = db.Column(db.String(36), db.ForeignKey("academic_years.id"), nullable=False, index=True)
    semester_number = db.Column(db.Integer, nullable=False)  # 1 through 8
    name = db.Column(db.String(50), nullable=False)  # e.g., "Semester 3"
    is_current = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint("academic_year_id", "semester_number", name="uq_ay_semester_number"),
    )

    # Relationships
    sections = db.relationship("Section", backref="semester", lazy=True, cascade="all, delete-orphan", order_by="Section.name")
    subjects = db.relationship("Subject", backref="semester", lazy=True, cascade="all, delete-orphan", order_by="Subject.code")

    def to_dict(self):
        return {
            "id": self.id,
            "academicYearId": self.academic_year_id,
            "semesterNumber": self.semester_number,
            "name": self.name,
            "isCurrent": self.is_current,
            "sections": [sec.to_dict() for sec in self.sections],
            "subjectsCount": len(self.subjects),
        }

    def to_dict_summary(self):
        return {
            "id": self.id,
            "academicYearId": self.academic_year_id,
            "semesterNumber": self.semester_number,
            "name": self.name,
            "isCurrent": self.is_current,
        }


class Section(db.Model):
    """
    Configurable section (Section A, B, C...) per semester.
    """
    __tablename__ = "sections"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.id"), nullable=False, index=True)
    name = db.Column(db.String(20), nullable=False)  # e.g., "A", "B", "C"
    room_number = db.Column(db.String(50), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("semester_id", "name", name="uq_semester_section_name"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "semesterId": self.semester_id,
            "name": self.name,
            "roomNumber": self.room_number,
        }


class Student(db.Model):
    """
    Student entity belonging to a Batch and assigned to a section.
    """
    __tablename__ = "students"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    roll_number = db.Column(db.String(40), unique=True, nullable=False, index=True)  # e.g., "25881A6601"
    name = db.Column(db.String(120), nullable=False, index=True)
    batch_id = db.Column(db.String(36), db.ForeignKey("batches.id"), nullable=False, index=True)
    current_section_id = db.Column(db.String(36), db.ForeignKey("sections.id"), nullable=True, index=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(40), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    current_section = db.relationship("Section", foreign_keys=[current_section_id])
    attendance_records = db.relationship("AttendanceRecord", backref="student", lazy="dynamic", cascade="all, delete-orphan")
    assessment_records = db.relationship("AssessmentRecord", backref="student", lazy="dynamic", cascade="all, delete-orphan")
    semester_results = db.relationship("SemesterResult", backref="student", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "rollNumber": self.roll_number,
            "name": self.name,
            "batchId": self.batch_id,
            "batchName": self.batch.name if self.batch else None,
            "sectionId": self.current_section_id,
            "sectionName": self.current_section.name if self.current_section else None,
            "email": self.email,
            "phone": self.phone,
            "gender": self.gender,
            "isActive": self.is_active,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Subject(db.Model):
    """
    Curricular subject configured for a semester.
    """
    __tablename__ = "subjects"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.id"), nullable=False, index=True)
    code = db.Column(db.String(40), nullable=False, index=True)  # e.g., "A9001", "CS301PC"
    name = db.Column(db.String(150), nullable=False)  # e.g., "Matrices and Calculus"
    short_name = db.Column(db.String(40), nullable=True)  # e.g., "MAC"
    credits = db.Column(db.Float, default=3.0)
    subject_type = db.Column(db.String(30), default="THEORY")  # THEORY, LAB, ELECTIVE
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint("semester_id", "code", name="uq_semester_subject_code"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "semesterId": self.semester_id,
            "code": self.code,
            "name": self.name,
            "shortName": self.short_name or self.name,
            "credits": self.credits,
            "subjectType": self.subject_type,
            "isActive": self.is_active,
        }


class AttendanceRecord(db.Model):
    """
    Subject-wise attendance percentage for a student in a semester and section.
    Attendance must be between 0 and 100.
    """
    __tablename__ = "attendance_records"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey("students.id"), nullable=False, index=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.id"), nullable=False, index=True)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.id"), nullable=False, index=True)
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.id"), nullable=False, index=True)
    percentage = db.Column(db.Float, nullable=False)  # 0.0 to 100.0
    classes_attended = db.Column(db.Integer, nullable=True)
    total_classes = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("student_id", "semester_id", "subject_id", name="uq_student_sem_subject_attendance"),
    )

    # Relationships
    subject = db.relationship("Subject")
    section = db.relationship("Section")
    semester = db.relationship("Semester")

    def to_dict(self):
        return {
            "id": self.id,
            "studentId": self.student_id,
            "rollNumber": self.student.roll_number if self.student else None,
            "studentName": self.student.name if self.student else None,
            "subjectId": self.subject_id,
            "subjectCode": self.subject.code if self.subject else None,
            "subjectName": self.subject.name if self.subject else None,
            "sectionId": self.section_id,
            "sectionName": self.section.name if self.section else None,
            "semesterId": self.semester_id,
            "percentage": round(self.percentage, 2),
            "classesAttended": self.classes_attended,
            "totalClasses": self.total_classes,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class AssessmentRecord(db.Model):
    """
    Subject-wise assessment record for Mid-1, Mid-2 (OPTIONAL).
    If Mid does not exist, status is 'NOT_AVAILABLE' (Never 0).
    """
    __tablename__ = "assessment_records"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey("students.id"), nullable=False, index=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.id"), nullable=False, index=True)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.id"), nullable=False, index=True)
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.id"), nullable=False, index=True)
    assessment_type = db.Column(db.String(20), nullable=False)  # MID_1, MID_2
    marks_obtained = db.Column(db.Float, nullable=True)
    max_marks = db.Column(db.Float, default=30.0)
    status = db.Column(db.String(30), default="AVAILABLE")  # AVAILABLE, NOT_AVAILABLE, ABSENT
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("student_id", "semester_id", "subject_id", "assessment_type", name="uq_student_sem_subj_assessment"),
    )

    # Relationships
    subject = db.relationship("Subject")
    section = db.relationship("Section")
    semester = db.relationship("Semester")

    def to_dict(self):
        return {
            "id": self.id,
            "studentId": self.student_id,
            "rollNumber": self.student.roll_number if self.student else None,
            "studentName": self.student.name if self.student else None,
            "subjectId": self.subject_id,
            "subjectCode": self.subject.code if self.subject else None,
            "subjectName": self.subject.name if self.subject else None,
            "sectionId": self.section_id,
            "sectionName": self.section.name if self.section else None,
            "semesterId": self.semester_id,
            "assessmentType": self.assessment_type,
            "marksObtained": self.marks_obtained,
            "maxMarks": self.max_marks,
            "status": self.status,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class SemesterResult(db.Model):
    """
    Official end-semester subject-wise results (Marks, Grade, Grade Points).
    Preserves raw uploaded grades accurately without inference.
    """
    __tablename__ = "semester_results"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey("students.id"), nullable=False, index=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.id"), nullable=False, index=True)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.id"), nullable=False, index=True)
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.id"), nullable=False, index=True)
    internal_marks = db.Column(db.Float, nullable=True)
    external_marks = db.Column(db.Float, nullable=True)
    total_marks = db.Column(db.Float, nullable=True)
    grade = db.Column(db.String(10), nullable=True)  # e.g., "O", "A+", "A", "B+", "B", "C", "F", "AB"
    grade_point = db.Column(db.Float, nullable=True)  # e.g., 10.0, 9.0, 8.0, 0.0
    credits_earned = db.Column(db.Float, nullable=True)
    result_status = db.Column(db.String(20), default="PASSED", index=True)  # PASSED, FAILED, ABSENT
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("student_id", "semester_id", "subject_id", name="uq_student_sem_subject_result"),
    )

    # Relationships
    subject = db.relationship("Subject")
    section = db.relationship("Section")
    semester = db.relationship("Semester")

    def to_dict(self):
        return {
            "id": self.id,
            "studentId": self.student_id,
            "rollNumber": self.student.roll_number if self.student else None,
            "studentName": self.student.name if self.student else None,
            "subjectId": self.subject_id,
            "subjectCode": self.subject.code if self.subject else None,
            "subjectName": self.subject.name if self.subject else None,
            "sectionId": self.section_id,
            "sectionName": self.section.name if self.section else None,
            "semesterId": self.semester_id,
            "internalMarks": self.internal_marks,
            "externalMarks": self.external_marks,
            "totalMarks": self.total_marks,
            "grade": self.grade,
            "gradePoint": self.grade_point,
            "creditsEarned": self.credits_earned,
            "resultStatus": self.result_status,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class StudentSemesterSummary(db.Model):
    """
    Stores official SGPA and CGPA from college results if provided in the result sheet.
    """
    __tablename__ = "student_semester_summaries"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey("students.id"), nullable=False, index=True)
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.id"), nullable=False, index=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.id"), nullable=False, index=True)
    sgpa = db.Column(db.Float, nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    total_credits = db.Column(db.Float, nullable=True)
    is_official = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint("student_id", "semester_id", name="uq_student_semester_summary"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "studentId": self.student_id,
            "semesterId": self.semester_id,
            "sectionId": self.section_id,
            "sgpa": self.sgpa,
            "cgpa": self.cgpa,
            "totalCredits": self.total_credits,
            "isOfficial": self.is_official,
        }


class UploadHistory(db.Model):
    """
    Audit log of all academic data imports and file validation records.
    """
    __tablename__ = "upload_history"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.String(120), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    batch_id = db.Column(db.String(36), db.ForeignKey("batches.id"), nullable=False, index=True)
    academic_year_id = db.Column(db.String(36), db.ForeignKey("academic_years.id"), nullable=False, index=True)
    semester_id = db.Column(db.String(36), db.ForeignKey("semesters.id"), nullable=False, index=True)
    section_id = db.Column(db.String(36), db.ForeignKey("sections.id"), nullable=False, index=True)
    data_type = db.Column(db.String(30), nullable=False)  # ATTENDANCE, MID_1, MID_2, SEMESTER_RESULT
    total_rows = db.Column(db.Integer, default=0)
    valid_rows = db.Column(db.Integer, default=0)
    invalid_rows = db.Column(db.Integer, default=0)
    duplicates_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default="VALIDATED")  # VALIDATED, IMPORTED, FAILED, CANCELLED
    details = db.Column(db.Text, nullable=True)  # JSON or text summary of errors/warnings

    # Relationships
    batch = db.relationship("Batch")
    academic_year = db.relationship("AcademicYear")
    semester = db.relationship("Semester")
    section = db.relationship("Section")

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "uploadedBy": self.uploaded_by,
            "uploadedAt": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "batchId": self.batch_id,
            "batchName": self.batch.name if self.batch else None,
            "academicYearId": self.academic_year_id,
            "academicYearName": self.academic_year.name if self.academic_year else None,
            "semesterId": self.semester_id,
            "semesterName": self.semester.name if self.semester else None,
            "sectionId": self.section_id,
            "sectionName": self.section.name if self.section else None,
            "dataType": self.data_type,
            "totalRows": self.total_rows,
            "validRows": self.valid_rows,
            "invalidRows": self.invalid_rows,
            "duplicatesCount": self.duplicates_count,
            "status": self.status,
            "details": self.details,
        }
