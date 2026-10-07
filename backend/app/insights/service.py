"""
Main Academic Insights Service Coordinator.
Integrates deterministic detectors, severity evaluation, and recommendation generation.
Operates strictly server-side; avoids N+1 query patterns by pre-filtering active cohorts.
"""

from app.models.academic import Student, Semester, Section
from app.insights.detectors import AcademicDetectors
from app.insights.rules import InsightRules
from app.insights.severity import SeverityLevel
from app.insights.serializers import InsightSerializer


class InsightsService:
    """
    Coordinates problem identification across Department, Batch, Semester, and Student hierarchies.
    """

    @classmethod
    def get_insights_overview(cls, batch_id=None, academic_year_id=None, semester_id=None, section_id=None):
        """
        Calculates high-level problem identification metrics:
        - Total students requiring attention
        - Counts by severity (Critical, High, Medium, Low)
        - Flagged subjects and sections counts
        - Priority insights feed
        """
        # 1. Fetch cohort students
        student_query = Student.query.filter_by(is_active=True)
        if batch_id:
            student_query = student_query.filter_by(batch_id=batch_id)
        if section_id:
            student_query = student_query.filter_by(current_section_id=section_id)
        students = student_query.all()

        flagged_students = []
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0

        # Evaluate each student in cohort
        for stu in students:
            detected = AcademicDetectors.detect_student_problems(stu.id, semester_id)
            if detected and detected["requires_attention"]:
                sev = detected["overall_severity"]
                if sev == SeverityLevel.CRITICAL:
                    critical_count += 1
                elif sev == SeverityLevel.HIGH:
                    high_count += 1
                elif sev == SeverityLevel.MEDIUM:
                    medium_count += 1
                elif sev == SeverityLevel.LOW:
                    low_count += 1

                flagged_students.append(InsightSerializer.serialize_student_insight(detected))

        # Sort flagged students by severity rank descending
        flagged_students.sort(
            key=lambda s: SeverityLevel.RANK.get(s["severity"], 0),
            reverse=True
        )

        # 2. Evaluate Subjects if semester is provided
        flagged_subjects = []
        if semester_id:
            flagged_subjects = AcademicDetectors.detect_subject_problems(semester_id, section_id)

        # 3. Evaluate Sections if semester is provided
        flagged_sections = []
        if semester_id:
            flagged_sections = AcademicDetectors.detect_section_problems(semester_id)

        return {
            "summary": {
                "totalCohortStudents": len(students),
                "studentsRequiringAttention": len(flagged_students),
                "criticalIssuesCount": critical_count,
                "highPriorityCount": high_count,
                "mediumPriorityCount": medium_count,
                "lowPriorityCount": low_count,
                "subjectsRequiringAttention": len(flagged_subjects),
                "sectionsRequiringAttention": len(flagged_sections),
            },
            "priorityInsights": flagged_students[:10],  # Top 10 priority issues
            "flaggedSubjects": [InsightSerializer.serialize_subject_insight(s) for s in flagged_subjects],
            "flaggedSections": [InsightSerializer.serialize_section_insight(s) for s in flagged_sections],
        }

    @classmethod
    def get_student_watchlist(
        cls,
        batch_id=None,
        academic_year_id=None,
        semester_id=None,
        section_id=None,
        severity=None,
        category=None,
        search=None,
        page=1,
        limit=25,
    ):
        """
        Retrieves a filtered, paginated student watchlist of identified academic attention cases.
        """
        student_query = Student.query.filter_by(is_active=True)
        if batch_id:
            student_query = student_query.filter_by(batch_id=batch_id)
        if section_id:
            student_query = student_query.filter_by(current_section_id=section_id)
        if search:
            search_term = f"%{search.strip().upper()}%"
            student_query = student_query.filter(
                (Student.roll_number.ilike(search_term)) | (Student.name.ilike(search_term))
            )

        students = student_query.all()
        flagged_students = []

        for stu in students:
            detected = AcademicDetectors.detect_student_problems(stu.id, semester_id)
            if not detected or not detected["requires_attention"]:
                continue

            # Severity filter
            if severity and severity.upper() != "ALL" and detected["overall_severity"] != severity.upper():
                continue

            # Category filter
            if category and category.upper() != "ALL":
                has_cat = any(s.get("category") == category.upper() for s in detected["signals"])
                if not has_cat:
                    continue

            flagged_students.append(InsightSerializer.serialize_student_insight(detected))

        # Sort by severity rank descending, then roll number ascending
        flagged_students.sort(
            key=lambda s: (-SeverityLevel.RANK.get(s["severity"], 0), s["roll_number"])
        )

        total_flagged = len(flagged_students)
        offset = (page - 1) * limit
        paginated_items = flagged_students[offset : offset + limit]

        return {
            "total": total_flagged,
            "page": page,
            "limit": limit,
            "totalPages": (total_flagged + limit - 1) // limit if total_flagged else 1,
            "data": paginated_items,
        }

    @classmethod
    def get_single_student_insights(cls, student_id_or_roll, semester_id=None):
        """
        Retrieves complete insight details and recommendations for an individual student.
        """
        student = Student.query.get(student_id_or_roll)
        if not student:
            student = Student.query.filter_by(roll_number=str(student_id_or_roll).upper()).first()
            if not student:
                raise ValueError(f"Student with ID or Roll Number '{student_id_or_roll}' not found.")

        detected = AcademicDetectors.detect_student_problems(student.id, semester_id)
        return InsightSerializer.serialize_student_insight(detected)

    @classmethod
    def get_subject_insights(cls, semester_id, section_id=None):
        """
        Retrieves subject-level problem detection insights.
        """
        subjects = AcademicDetectors.detect_subject_problems(semester_id, section_id)
        return [InsightSerializer.serialize_subject_insight(s) for s in subjects]

    @classmethod
    def get_section_insights(cls, semester_id):
        """
        Retrieves comparative section insights.
        """
        sections = AcademicDetectors.detect_section_problems(semester_id)
        return [InsightSerializer.serialize_section_insight(s) for s in sections]

    @classmethod
    def get_thresholds(cls):
        """Retrieves active configurable thresholds."""
        return InsightRules.get_all()

    @classmethod
    def update_thresholds(cls, new_thresholds):
        """Updates configurable thresholds."""
        return InsightRules.update(new_thresholds)
