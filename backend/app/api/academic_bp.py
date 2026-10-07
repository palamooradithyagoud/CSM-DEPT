from flask import Blueprint, request, jsonify
from app.extensions import db
from app.utils.decorators import role_required
from app.models.academic import (
    Batch,
    AcademicYear,
    Semester,
    Section,
    Student,
    Subject,
    AttendanceRecord,
    AssessmentRecord,
    SemesterResult,
    StudentSemesterSummary,
)

academic_bp = Blueprint("academic", __name__, url_prefix="/api/v1")


# ----------------------------------------------------
# 1. BATCHES
# ----------------------------------------------------
@academic_bp.route("/batches", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_batches():
    """List all batches in the department."""
    batches = Batch.query.order_by(Batch.start_year.desc()).all()
    return jsonify({
        "success": True,
        "data": [b.to_dict() for b in batches],
        "total": len(batches),
    }), 200


@academic_bp.route("/batches", methods=["POST"])
@role_required(["ADMIN", "HOD"])
def create_batch():
    """Create a new batch entity and automatically generate 4 academic years (1st, 2nd, 3rd, 4th Year) and 8 semesters."""
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    start_year = data.get("startYear") or data.get("start_year")
    end_year = data.get("endYear") or data.get("end_year")

    if not name or not start_year or not end_year:
        return jsonify({"success": False, "message": "Batch name, start year, and end year are required."}), 400

    existing = Batch.query.filter_by(name=name).first()
    if existing:
        return jsonify({"success": False, "message": f"Batch '{name}' already exists."}), 409

    batch = Batch(
        name=name,
        start_year=int(start_year),
        end_year=int(end_year),
        is_active=True,
    )
    db.session.add(batch)
    db.session.flush()

    # Generate 4 Academic Years with Semesters
    year_labels = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
    for y_idx, label in enumerate(year_labels, start=1):
        cal_start = int(start_year) + (y_idx - 1)
        cal_end = cal_start + 1
        ay = AcademicYear(
            batch_id=batch.id,
            year_number=y_idx,
            name=label,
            calendar_year=f"{cal_start}-{cal_end}",
            is_current=(y_idx == 1),
        )
        db.session.add(ay)
        db.session.flush()

        # Generate 2 Semesters per Academic Year
        sem_num_1 = (y_idx * 2) - 1
        sem_num_2 = y_idx * 2

        s1 = Semester(
            academic_year_id=ay.id,
            semester_number=sem_num_1,
            name=f"Semester {sem_num_1}",
            is_current=(y_idx == 1 and sem_num_1 == 1),
        )
        s2 = Semester(
            academic_year_id=ay.id,
            semester_number=sem_num_2,
            name=f"Semester {sem_num_2}",
            is_current=False,
        )
        db.session.add_all([s1, s2])

    db.session.commit()
    return jsonify({
        "success": True,
        "message": f"Batch '{name}' created successfully with academic years and semesters.",
        "data": batch.to_dict(),
    }), 201


# ----------------------------------------------------
# 2. ACADEMIC YEARS
# ----------------------------------------------------
@academic_bp.route("/academic-years", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_academic_years():
    """Get academic years, optionally filtered by batch_id."""
    batch_id = request.args.get("batch_id")
    query = AcademicYear.query
    if batch_id:
        query = query.filter_by(batch_id=batch_id)
    years = query.order_by(AcademicYear.year_number.asc()).all()
    return jsonify({
        "success": True,
        "data": [y.to_dict() for y in years],
        "total": len(years),
    }), 200


# ----------------------------------------------------
# 3. SEMESTERS
# ----------------------------------------------------
@academic_bp.route("/semesters", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_semesters():
    """Get semesters, optionally filtered by academic_year_id."""
    academic_year_id = request.args.get("academic_year_id")
    query = Semester.query
    if academic_year_id:
        query = query.filter_by(academic_year_id=academic_year_id)
    semesters = query.order_by(Semester.semester_number.asc()).all()
    return jsonify({
        "success": True,
        "data": [s.to_dict() for s in semesters],
        "total": len(semesters),
    }), 200


# ----------------------------------------------------
# 4. SECTIONS
# ----------------------------------------------------
@academic_bp.route("/sections", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_sections():
    """Get configurable sections, optionally filtered by semester_id."""
    semester_id = request.args.get("semester_id")
    query = Section.query
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
    sections = query.order_by(Section.name.asc()).all()
    return jsonify({
        "success": True,
        "data": [sec.to_dict() for sec in sections],
        "total": len(sections),
    }), 200


@academic_bp.route("/sections", methods=["POST"])
@role_required(["ADMIN", "HOD"])
def create_section():
    """Create a new section for a semester (e.g. Section A, Section B, Section C)."""
    data = request.get_json() or {}
    semester_id = data.get("semesterId") or data.get("semester_id")
    name = (data.get("name") or "").strip().upper()
    room_number = (data.get("roomNumber") or data.get("room_number") or "").strip()

    if not semester_id or not name:
        return jsonify({"success": False, "message": "Semester ID and Section name are required."}), 400

    semester = Semester.query.get(semester_id)
    if not semester:
        return jsonify({"success": False, "message": "Semester not found."}), 404

    existing = Section.query.filter_by(semester_id=semester_id, name=name).first()
    if existing:
        return jsonify({"success": False, "message": f"Section '{name}' already exists in {semester.name}."}), 409

    sec = Section(
        semester_id=semester_id,
        name=name,
        room_number=room_number,
    )
    db.session.add(sec)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Section '{name}' created successfully.",
        "data": sec.to_dict(),
    }), 201


# ----------------------------------------------------
# 5. SUBJECTS
# ----------------------------------------------------
@academic_bp.route("/subjects", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_subjects():
    """Get curriculum subjects configured for a semester."""
    semester_id = request.args.get("semester_id")
    query = Subject.query
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
    subjects = query.order_by(Subject.code.asc()).all()
    return jsonify({
        "success": True,
        "data": [s.to_dict() for s in subjects],
        "total": len(subjects),
    }), 200


@academic_bp.route("/subjects", methods=["POST"])
@role_required(["ADMIN", "HOD"])
def create_subject():
    """Create a subject entity."""
    data = request.get_json() or {}
    semester_id = data.get("semesterId") or data.get("semester_id")
    code = (data.get("code") or "").strip().upper()
    name = (data.get("name") or "").strip()
    short_name = (data.get("shortName") or data.get("short_name") or "").strip()
    credits_val = data.get("credits", 3.0)
    subject_type = (data.get("subjectType") or data.get("subject_type") or "THEORY").strip().upper()

    if not semester_id or not code or not name:
        return jsonify({"success": False, "message": "Semester ID, Subject Code, and Subject Name are required."}), 400

    existing = Subject.query.filter_by(semester_id=semester_id, code=code).first()
    if existing:
        return jsonify({"success": False, "message": f"Subject with code '{code}' already exists in this semester."}), 409

    subj = Subject(
        semester_id=semester_id,
        code=code,
        name=name,
        short_name=short_name or code,
        credits=float(credits_val),
        subject_type=subject_type,
        is_active=True,
    )
    db.session.add(subj)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Subject '{code} - {name}' created successfully.",
        "data": subj.to_dict(),
    }), 201


# ----------------------------------------------------
# 6. STUDENTS
# ----------------------------------------------------
@academic_bp.route("/students", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_students():
    """
    Get students with search (roll_number, name) and filters (batch_id, section_id).
    Supports pagination.
    """
    batch_id = request.args.get("batch_id")
    section_id = request.args.get("section_id")
    search = (request.args.get("search") or "").strip()
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))

    query = Student.query
    if batch_id:
        query = query.filter_by(batch_id=batch_id)
    if section_id:
        query = query.filter_by(current_section_id=section_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Student.roll_number.ilike(search_pattern),
                Student.name.ilike(search_pattern),
            )
        )

    total = query.count()
    students = query.order_by(Student.roll_number.asc()).offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        "success": True,
        "data": [s.to_dict() for s in students],
        "page": page,
        "limit": limit,
        "total": total,
    }), 200


@academic_bp.route("/students/<student_id>", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_student_detail(student_id):
    """
    Get full student profile with REAL verified academic records.
    No fake or invented records.
    """
    student = Student.query.get(student_id)
    if not student:
        # Also check by roll_number
        student = Student.query.filter_by(roll_number=student_id.upper()).first()
        if not student:
            return jsonify({"success": False, "message": "Student not found."}), 404

    # Fetch verified records
    attendance_records = AttendanceRecord.query.filter_by(student_id=student.id).all()
    assessment_records = AssessmentRecord.query.filter_by(student_id=student.id).all()
    semester_results = SemesterResult.query.filter_by(student_id=student.id).all()
    summaries = StudentSemesterSummary.query.filter_by(student_id=student.id).all()

    return jsonify({
        "success": True,
        "data": {
            **student.to_dict(),
            "attendanceRecords": [a.to_dict() for a in attendance_records],
            "assessmentRecords": [a.to_dict() for a in assessment_records],
            "semesterResults": [r.to_dict() for r in semester_results],
            "semesterSummaries": [s.to_dict() for s in summaries],
        },
    }), 200


@academic_bp.route("/students", methods=["POST"])
@role_required(["ADMIN", "HOD"])
def create_student():
    """Create a single student record."""
    data = request.get_json() or {}
    roll_number = (data.get("rollNumber") or data.get("roll_number") or "").strip().upper()
    name = (data.get("name") or "").strip()
    batch_id = data.get("batchId") or data.get("batch_id")
    section_id = data.get("sectionId") or data.get("section_id")

    if not roll_number or not name or not batch_id:
        return jsonify({"success": False, "message": "Roll Number, Name, and Batch ID are required."}), 400

    existing = Student.query.filter_by(roll_number=roll_number).first()
    if existing:
        return jsonify({"success": False, "message": f"Student with roll number '{roll_number}' already exists."}), 409

    student = Student(
        roll_number=roll_number,
        name=name,
        batch_id=batch_id,
        current_section_id=section_id,
        email=data.get("email"),
        phone=data.get("phone"),
        gender=data.get("gender"),
        is_active=True,
    )
    db.session.add(student)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Student '{roll_number} - {name}' registered successfully.",
        "data": student.to_dict(),
    }), 201


# ----------------------------------------------------
# 7. ACADEMIC DATA AVAILABILITY MATRIX
# ----------------------------------------------------
@academic_bp.route("/academic-data/availability", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_data_availability():
    """
    Reports whether required academic data (Attendance, Mid-1, Mid-2, Semester Result)
    exists for the selected context.
    Batch -> Academic Year -> Semester -> Section
    """
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")

    if not semester_id or not section_id:
        return jsonify({"success": False, "message": "semester_id and section_id are required."}), 400

    att_count = AttendanceRecord.query.filter_by(semester_id=semester_id, section_id=section_id).count()
    mid1_count = AssessmentRecord.query.filter_by(
        semester_id=semester_id, section_id=section_id, assessment_type="MID_1"
    ).count()
    mid2_count = AssessmentRecord.query.filter_by(
        semester_id=semester_id, section_id=section_id, assessment_type="MID_2"
    ).count()
    res_count = SemesterResult.query.filter_by(semester_id=semester_id, section_id=section_id).count()

    total_students = Student.query.filter_by(current_section_id=section_id).count()

    return jsonify({
        "success": True,
        "data": {
            "sectionId": section_id,
            "semesterId": semester_id,
            "totalStudents": total_students,
            "attendance": {
                "available": att_count > 0,
                "recordCount": att_count,
                "status": "UPLOADED" if att_count > 0 else "NOT_AVAILABLE",
            },
            "mid1": {
                "available": mid1_count > 0,
                "recordCount": mid1_count,
                "status": "UPLOADED" if mid1_count > 0 else "NOT_AVAILABLE",
            },
            "mid2": {
                "available": mid2_count > 0,
                "recordCount": mid2_count,
                "status": "UPLOADED" if mid2_count > 0 else "NOT_AVAILABLE",
            },
            "semesterResult": {
                "available": res_count > 0,
                "recordCount": res_count,
                "status": "UPLOADED" if res_count > 0 else "NOT_AVAILABLE",
            },
        },
    }), 200


# ----------------------------------------------------
# 8. ACADEMIC RECORDS RETRIEVAL
# ----------------------------------------------------
@academic_bp.route("/attendance", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_attendance_records():
    """Get attendance records filtered by semester, section, subject."""
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")
    subject_id = request.args.get("subject_id")

    query = AttendanceRecord.query
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
    if section_id:
        query = query.filter_by(section_id=section_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)

    records = query.order_by(AttendanceRecord.student_id).all()
    return jsonify({
        "success": True,
        "data": [r.to_dict() for r in records],
        "total": len(records),
    }), 200


@academic_bp.route("/assessments", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_assessment_records():
    """Get assessment records (Mid-1, Mid-2)."""
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")
    assessment_type = request.args.get("assessment_type")

    query = AssessmentRecord.query
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
    if section_id:
        query = query.filter_by(section_id=section_id)
    if assessment_type:
        query = query.filter_by(assessment_type=assessment_type.upper())

    records = query.all()
    return jsonify({
        "success": True,
        "data": [r.to_dict() for r in records],
        "total": len(records),
    }), 200


@academic_bp.route("/results", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_semester_results():
    """Get semester results."""
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")

    query = SemesterResult.query
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
    if section_id:
        query = query.filter_by(section_id=section_id)

    results = query.all()
    return jsonify({
        "success": True,
        "data": [r.to_dict() for r in results],
        "total": len(results),
    }), 200
