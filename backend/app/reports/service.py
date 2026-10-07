"""
Academic Reports Service Facade.
Assembles verified academic metrics and delegates document generation to PDF, Excel, and CSV builders.
Zero fabricated records: strictly grounded in verified database analytics and insight rules.
"""

from datetime import datetime
from app.extensions import db
from app.models.academic import (
    Batch,
    AcademicYear,
    Semester,
    Section,
    Student,
    Subject,
    SemesterResult,
    AttendanceRecord,
)
from app.analytics.service import AnalyticsService
from app.insights.service import InsightsService
from app.reports.pdf_generator import PDFReportGenerator
from app.reports.excel_generator import ExcelReportGenerator
from app.reports.csv_generator import CSVReportGenerator


class ReportsService:
    """Service orchestrating academic data gathering and multi-format report exports."""

    # ----------------------------------------------------
    # 1. DATA GATHERING METHODS
    # ----------------------------------------------------

    @classmethod
    def get_department_report_data(cls, batch_id=None, academic_year_id=None, semester_id=None):
        """Assembles comprehensive department academic performance dataset."""
        batch = Batch.query.get(batch_id) if batch_id else None
        sem = Semester.query.get(semester_id) if semester_id else None

        overview = AnalyticsService.get_overview(
            batch_id=batch_id,
            academic_year_id=academic_year_id,
            semester_id=semester_id,
        )

        subjects_data = []
        sections_data = []
        grade_dist_data = []
        flagged_count = 0

        if semester_id:
            sub_res = AnalyticsService.get_subject_analytics(semester_id=semester_id)
            subjects_data = sub_res.get("subjects", [])

            sec_res = AnalyticsService.get_section_comparison(semester_id=semester_id)
            sections_data = sec_res.get("sections", [])

            gd_res = AnalyticsService.get_grade_distribution(semester_id=semester_id)
            grade_dist_data = gd_res.get("distribution", [])

            try:
                insights_overview = InsightsService.get_insights_overview(
                    batch_id=batch_id,
                    academic_year_id=academic_year_id,
                    semester_id=semester_id,
                )
                flagged_count = insights_overview.get("summary", {}).get("studentsRequiringAttention", 0)
            except Exception:
                flagged_count = 0

        kpis = dict(overview.get("metrics", {}))
        kpis["totalStudents"] = overview.get("totalStudents", 0)

        return {
            "batchName": batch.name if batch else "All Batches",
            "semesterName": sem.name if sem else "All Semesters",
            "totalStudents": overview.get("totalStudents", 0),
            "kpis": kpis,
            "subjects": subjects_data,
            "sections": sections_data,
            "gradeDistribution": grade_dist_data,
            "flaggedStudentsCount": flagged_count,
        }

    @classmethod
    def get_section_report_data(cls, section_id, semester_id=None):
        """Assembles section-level performance dataset and watchlist."""
        section = Section.query.get(section_id)
        if not section:
            return None

        sem_id = semester_id or section.semester_id
        semester = Semester.query.get(sem_id)
        batch = semester.academic_year.batch if semester and semester.academic_year else None

        # Section KPIs
        overview = AnalyticsService.get_overview(semester_id=sem_id, section_id=section_id)
        kpis = overview.get("metrics", {})

        # Subjects in this semester/section
        sub_res = AnalyticsService.get_subject_analytics(semester_id=sem_id, section_id=section_id)
        subjects = sub_res.get("subjects", [])

        # Flagged students in this section
        flagged_students = []
        try:
            wl = InsightsService.get_student_watchlist(semester_id=sem_id, section_id=section_id, limit=100)
            flagged_students = wl.get("watchlist", [])
        except Exception:
            flagged_students = []

        return {
            "sectionId": section.id,
            "sectionName": section.name,
            "batchName": batch.name if batch else "N/A",
            "semesterName": semester.name if semester else "N/A",
            "studentCount": overview.get("totalStudents", 0),
            "averageSGPA": kpis.get("averageSGPA"),
            "averageAttendance": kpis.get("averageAttendance"),
            "passPercentage": kpis.get("passPercentage"),
            "flaggedStudentsCount": len(flagged_students),
            "subjects": subjects,
            "flaggedStudents": flagged_students,
        }

    @classmethod
    def get_student_report_data(cls, student_id_or_roll, semester_id=None):
        """Assembles individual student academic dossier with trajectory and diagnostic insights."""
        student = Student.query.get(student_id_or_roll)
        if not student:
            student = Student.query.filter_by(roll_number=str(student_id_or_roll).upper()).first()
            if not student:
                return None

        profile = AnalyticsService.get_student_analytics(student.id)
        if not profile:
            return None

        # Diagnostic insights
        diagnostics = {}
        try:
            diagnostics = InsightsService.get_student_diagnostic(student.id, semester_id=semester_id)
        except Exception:
            diagnostics = {}

        return {
            "studentId": student.id,
            "rollNumber": student.roll_number,
            "name": student.name,
            "email": student.email,
            "batchName": student.batch.name if student.batch else "N/A",
            "sectionName": student.current_section.name if student.current_section else "N/A",
            "semesterName": profile.get("profile", {}).get("currentSemester", "N/A"),
            "sgpa": profile.get("profile", {}).get("latestSGPA"),
            "cgpa": profile.get("profile", {}).get("currentCGPA"),
            "attendancePercentage": profile.get("profile", {}).get("averageAttendance"),
            "trend": profile.get("profile", {}).get("trajectoryTrend", "STABLE"),
            "subjects": profile.get("currentSemesterSubjects", []),
            "trajectory": profile.get("trajectory", []),
            "issues": diagnostics.get("signals", []),
            "recommendations": diagnostics.get("recommendations", []),
        }

    @classmethod
    def get_subject_report_data(cls, subject_id, semester_id=None):
        """Assembles course performance diagnostic dataset across sections."""
        subject = Subject.query.get(subject_id)
        if not subject:
            return None

        sem_id = semester_id or subject.semester_id
        semester = Semester.query.get(sem_id)

        # Subject overall stats
        sub_res = AnalyticsService.get_subject_analytics(semester_id=sem_id, subject_id=subject.id)
        subject_metrics = sub_res.get("subjects", [{}])[0] if sub_res.get("subjects") else {}

        # Section-wise breakdown for this subject
        sections_data = []
        if semester:
            for sec in semester.sections:
                sec_sub_res = AnalyticsService.get_subject_analytics(semester_id=sem_id, section_id=sec.id, subject_id=subject.id)
                sec_sub_list = sec_sub_res.get("subjects", [])
                if sec_sub_list:
                    s_info = sec_sub_list[0]
                    sections_data.append({
                        "sectionName": sec.name,
                        "studentCount": s_info.get("evaluatedStudents", 0),
                        "averageMarks": s_info.get("averageMarks"),
                        "passPercentage": s_info.get("passPercentage"),
                        "failureCount": s_info.get("failureCount", 0),
                    })

        return {
            "subjectId": subject.id,
            "code": subject.code,
            "name": subject.name,
            "credits": subject.credits,
            "subjectType": subject.subject_type,
            "semesterName": semester.name if semester else "N/A",
            "studentCount": subject_metrics.get("evaluatedStudents", 0),
            "averageMarks": subject_metrics.get("averageMarks"),
            "highestMarks": subject_metrics.get("highestMarks"),
            "lowestMarks": subject_metrics.get("lowestMarks"),
            "passPercentage": subject_metrics.get("passPercentage"),
            "failureCount": subject_metrics.get("failureCount", 0),
            "averageAttendance": subject_metrics.get("averageAttendance"),
            "sections": sections_data,
        }

    @classmethod
    def get_insights_report_data(cls, batch_id=None, academic_year_id=None, semester_id=None, section_id=None):
        """Assembles academic insights, watchlist, and diagnostic summary dataset."""
        overview = InsightsService.get_insights_overview(
            batch_id=batch_id,
            academic_year_id=academic_year_id,
            semester_id=semester_id,
            section_id=section_id,
        )

        watchlist_res = InsightsService.get_student_watchlist(
            batch_id=batch_id,
            academic_year_id=academic_year_id,
            semester_id=semester_id,
            section_id=section_id,
            limit=250,
        )

        semester = Semester.query.get(semester_id) if semester_id else None

        return {
            "semesterName": semester.name if semester else "All Semesters",
            "summary": overview.get("summary", {}),
            "watchlist": watchlist_res.get("watchlist", []),
        }

    # ----------------------------------------------------
    # 2. DOCUMENT GENERATION DISPATCHER
    # ----------------------------------------------------

    @classmethod
    def export_report(cls, report_type, data, export_format="pdf"):
        """
        Dispatches dataset to corresponding generator.
        Returns: (bytes, mimetype, filename)
        """
        fmt = (export_format or "pdf").lower()
        now_tag = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        if fmt == "csv":
            mimetype = "text/csv; charset=utf-8"
            if report_type == "department":
                content = CSVReportGenerator.generate_department_csv(data)
                filename = f"department_report_{now_tag}.csv"
            elif report_type == "section":
                content = CSVReportGenerator.generate_section_csv(data)
                filename = f"section_{data.get('sectionName', 'report')}_{now_tag}.csv"
            elif report_type == "student":
                content = CSVReportGenerator.generate_student_csv(data)
                filename = f"student_{data.get('rollNumber', 'dossier')}_{now_tag}.csv"
            elif report_type == "subject":
                content = CSVReportGenerator.generate_subject_csv(data)
                filename = f"subject_{data.get('code', 'report')}_{now_tag}.csv"
            elif report_type == "insights":
                content = CSVReportGenerator.generate_insights_csv(data)
                filename = f"academic_insights_{now_tag}.csv"
            else:
                raise ValueError(f"Unsupported report type: {report_type}")

        elif fmt == "excel":
            mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if report_type == "department":
                content = ExcelReportGenerator.generate_department_excel(data)
                filename = f"department_report_{now_tag}.xlsx"
            elif report_type == "section":
                content = ExcelReportGenerator.generate_section_excel(data)
                filename = f"section_{data.get('sectionName', 'report')}_{now_tag}.xlsx"
            elif report_type == "student":
                content = ExcelReportGenerator.generate_student_excel(data)
                filename = f"student_{data.get('rollNumber', 'dossier')}_{now_tag}.xlsx"
            elif report_type == "subject":
                content = ExcelReportGenerator.generate_subject_excel(data)
                filename = f"subject_{data.get('code', 'report')}_{now_tag}.xlsx"
            elif report_type == "insights":
                content = ExcelReportGenerator.generate_insights_excel(data)
                filename = f"academic_insights_{now_tag}.xlsx"
            else:
                raise ValueError(f"Unsupported report type: {report_type}")

        elif fmt == "pdf":
            mimetype = "application/pdf"
            if report_type == "department":
                content = PDFReportGenerator.generate_department_pdf(data)
                filename = f"department_report_{now_tag}.pdf"
            elif report_type == "section":
                content = PDFReportGenerator.generate_section_pdf(data)
                filename = f"section_{data.get('sectionName', 'report')}_{now_tag}.pdf"
            elif report_type == "student":
                content = PDFReportGenerator.generate_student_pdf(data)
                filename = f"student_{data.get('rollNumber', 'dossier')}_{now_tag}.pdf"
            elif report_type == "subject":
                content = PDFReportGenerator.generate_subject_pdf(data)
                filename = f"subject_{data.get('code', 'report')}_{now_tag}.pdf"
            elif report_type == "insights":
                content = PDFReportGenerator.generate_insights_pdf(data)
                filename = f"academic_insights_{now_tag}.pdf"
            else:
                raise ValueError(f"Unsupported report type: {report_type}")

        else:
            raise ValueError(f"Unsupported export format: {fmt}. Allowed: pdf, excel, csv")

        return content, mimetype, filename
