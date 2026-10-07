from sqlalchemy import func, distinct
from app.extensions import db
from app.models.academic import (
    Student,
    Subject,
    AttendanceRecord,
    SemesterResult,
    StudentSemesterSummary,
    Section,
)
from app.analytics.validators import AnalyticsValidator


class AnalyticsAggregations:
    """
    Deterministic academic aggregations across Department, Semester, Section, and Subject hierarchies.
    Zero fabricated numbers: every metric is derived directly from verified database records.
    """

    @classmethod
    def get_overview_kpis(cls, batch_id=None, academic_year_id=None, semester_id=None, section_id=None):
        """
        Calculates overarching academic performance KPIs for the selected hierarchical context.
        """
        # 1. Base Student Count
        student_query = Student.query.filter_by(is_active=True)
        if batch_id:
            student_query = student_query.filter_by(batch_id=batch_id)
        if section_id:
            student_query = student_query.filter_by(current_section_id=section_id)
        total_students = student_query.count()

        if not semester_id:
            return {
                "totalStudents": total_students,
                "dataAvailability": {
                    "results": "NOT_AVAILABLE",
                    "attendance": "NOT_AVAILABLE",
                },
                "metrics": {
                    "averageSGPA": None,
                    "averageCGPA": None,
                    "averageAttendance": None,
                    "passPercentage": None,
                    "studentsWithResults": 0,
                    "studentsWithAttendance": 0,
                    "totalPassedStudents": 0,
                    "totalFailedStudents": 0,
                },
                "message": "Select a semester to view academic performance metrics.",
            }

        # 2. Check Data Availability
        res_avail = AnalyticsValidator.check_result_availability(semester_id, section_id)
        att_avail = AnalyticsValidator.check_attendance_availability(semester_id, section_id)

        # 3. Aggregate SGPA and CGPA from StudentSemesterSummary
        summary_query = db.session.query(
            func.avg(StudentSemesterSummary.sgpa).label("avg_sgpa"),
            func.avg(StudentSemesterSummary.cgpa).label("avg_cgpa"),
            func.count(distinct(StudentSemesterSummary.student_id)).label("students_count"),
        ).filter(StudentSemesterSummary.semester_id == semester_id)

        if section_id:
            summary_query = summary_query.filter(StudentSemesterSummary.section_id == section_id)

        sum_res = summary_query.first()
        avg_sgpa = round(float(sum_res.avg_sgpa), 2) if sum_res and sum_res.avg_sgpa is not None else None
        avg_cgpa = round(float(sum_res.avg_cgpa), 2) if sum_res and sum_res.avg_cgpa is not None else None
        students_with_summaries = int(sum_res.students_count) if sum_res and sum_res.students_count else 0

        # If summary SGPA is not populated, calculate from SemesterResult if grade points exist
        if avg_sgpa is None:
            # Query grade points from SemesterResult
            gp_query = db.session.query(
                func.avg(SemesterResult.grade_point).label("avg_gp"),
                func.count(distinct(SemesterResult.student_id)).label("students_count"),
            ).filter(SemesterResult.semester_id == semester_id, SemesterResult.grade_point.isnot(None))
            if section_id:
                gp_query = gp_query.filter(SemesterResult.section_id == section_id)
            gp_res = gp_query.first()
            if gp_res and gp_res.avg_gp is not None:
                avg_sgpa = round(float(gp_res.avg_gp), 2)

        # 4. Aggregate Attendance
        att_query = db.session.query(
            func.avg(AttendanceRecord.percentage).label("avg_att"),
            func.count(distinct(AttendanceRecord.student_id)).label("students_count"),
        ).filter(AttendanceRecord.semester_id == semester_id)

        if section_id:
            att_query = att_query.filter(AttendanceRecord.section_id == section_id)

        att_res = att_query.first()
        avg_attendance = round(float(att_res.avg_att), 2) if att_res and att_res.avg_att is not None else None
        students_with_att = int(att_res.students_count) if att_res and att_res.students_count else 0

        # 5. Pass / Fail Calculation from SemesterResult
        # Distinct students with results in this semester
        res_students_query = db.session.query(SemesterResult.student_id).filter(
            SemesterResult.semester_id == semester_id
        ).distinct()
        if section_id:
            res_students_query = res_students_query.filter(SemesterResult.section_id == section_id)
        students_with_results_set = {r[0] for r in res_students_query.all()}
        students_with_results_count = len(students_with_results_set)

        # Students with at least one FAILED record in this semester
        failed_query = db.session.query(SemesterResult.student_id).filter(
            SemesterResult.semester_id == semester_id,
            db.or_(
                SemesterResult.result_status == "FAILED",
                SemesterResult.grade == "F",
            )
        ).distinct()
        if section_id:
            failed_query = failed_query.filter(SemesterResult.section_id == section_id)
        failed_students_set = {r[0] for r in failed_query.all()}


        passed_students_count = students_with_results_count - len(failed_students_set)
        pass_percentage = None
        if students_with_results_count > 0:
            pass_percentage = round((passed_students_count / students_with_results_count) * 100, 2)

        return {
            "totalStudents": total_students,
            "dataAvailability": {
                "results": "AVAILABLE" if res_avail["available"] else "NOT_AVAILABLE",
                "attendance": "AVAILABLE" if att_avail["available"] else "NOT_AVAILABLE",
            },
            "metrics": {
                "averageSGPA": avg_sgpa,
                "averageCGPA": avg_cgpa,
                "averageAttendance": avg_attendance,
                "passPercentage": pass_percentage,
                "studentsWithResults": students_with_results_count if students_with_results_count > 0 else students_with_summaries,
                "studentsWithAttendance": students_with_att,
                "totalPassedStudents": passed_students_count,
                "totalFailedStudents": len(failed_students_set),
            },
        }

    @classmethod
    def get_grade_distribution(cls, semester_id, section_id=None, subject_id=None):
        """
        Returns dynamic distribution of grades that actually exist in the verified dataset.
        Zero fabricated grade buckets.
        """
        query = db.session.query(
            SemesterResult.grade,
            func.count(SemesterResult.id).label("count")
        ).filter(
            SemesterResult.semester_id == semester_id,
            SemesterResult.grade.isnot(None),
            SemesterResult.grade != ""
        )

        if section_id:
            query = query.filter(SemesterResult.section_id == section_id)
        if subject_id:
            query = query.filter(SemesterResult.subject_id == subject_id)

        rows = query.group_by(SemesterResult.grade).all()

        # Sort with standard academic priority if recognized, otherwise alphabetical
        grade_order = ["O", "A+", "A", "B+", "B", "C", "P", "F", "AB"]
        def sort_key(item):
            g = item[0].upper()
            if g in grade_order:
                return grade_order.index(g)
            return 100

        sorted_rows = sorted(rows, key=sort_key)
        total_grades = sum(r[1] for r in sorted_rows)

        distribution = []
        for g, count in sorted_rows:
            pct = round((count / total_grades) * 100, 1) if total_grades > 0 else 0.0
            distribution.append({
                "grade": g.strip(),
                "count": count,
                "percentage": pct,
            })

        return {
            "available": len(distribution) > 0,
            "totalGradesRecorded": total_grades,
            "distribution": distribution,
            "message": "Grade distribution calculated." if distribution else "No grade records available for this selection.",
        }

    @classmethod
    def get_subject_analytics(cls, semester_id, section_id=None, subject_id=None):
        """
        Calculates detailed subject-level performance metrics:
        Enrolled students, average marks, highest, lowest, pass/fail counts, pass %, and average attendance.
        """
        subj_query = Subject.query.filter_by(semester_id=semester_id, is_active=True)
        if subject_id:
            subj_query = subj_query.filter_by(id=subject_id)
        subjects = subj_query.order_by(Subject.code.asc()).all()

        results_list = []
        for sub in subjects:
            # 1. Performance Query from SemesterResult
            res_query = db.session.query(
                func.count(SemesterResult.id).label("total_records"),
                func.avg(SemesterResult.total_marks).label("avg_marks"),
                func.max(SemesterResult.total_marks).label("max_marks"),
                func.min(SemesterResult.total_marks).label("min_marks"),
            ).filter(SemesterResult.semester_id == semester_id, SemesterResult.subject_id == sub.id)

            if section_id:
                res_query = res_query.filter(SemesterResult.section_id == section_id)

            stat = res_query.first()
            total_res = int(stat.total_records) if stat and stat.total_records else 0

            # Pass / Fail breakdown
            pass_count = 0
            fail_count = 0
            if total_res > 0:
                pass_q = db.session.query(func.count(SemesterResult.id)).filter(
                    SemesterResult.semester_id == semester_id,
                    SemesterResult.subject_id == sub.id,
                    db.or_(
                        SemesterResult.result_status == "PASSED",
                        SemesterResult.grade != "F",
                    )
                )
                if section_id:
                    pass_q = pass_q.filter(SemesterResult.section_id == section_id)
                pass_count = pass_q.scalar() or 0
                fail_count = total_res - pass_count

            pass_pct = round((pass_count / total_res) * 100, 2) if total_res > 0 else None
            avg_m = round(float(stat.avg_marks), 2) if stat and stat.avg_marks is not None else None
            highest_m = float(stat.max_marks) if stat and stat.max_marks is not None else None
            lowest_m = float(stat.min_marks) if stat and stat.min_marks is not None else None

            # 2. Attendance Query for this Subject
            att_query = db.session.query(
                func.avg(AttendanceRecord.percentage).label("avg_att"),
                func.count(AttendanceRecord.id).label("total_att_records"),
            ).filter(AttendanceRecord.semester_id == semester_id, AttendanceRecord.subject_id == sub.id)

            if section_id:
                att_query = att_query.filter(AttendanceRecord.section_id == section_id)

            att_stat = att_query.first()
            avg_att = round(float(att_stat.avg_att), 2) if att_stat and att_stat.avg_att is not None else None
            total_att = int(att_stat.total_att_records) if att_stat and att_stat.total_att_records else 0

            # 3. Grade breakdown for this subject
            grade_query = db.session.query(
                SemesterResult.grade,
                func.count(SemesterResult.id)
            ).filter(
                SemesterResult.semester_id == semester_id,
                SemesterResult.subject_id == sub.id,
                SemesterResult.grade.isnot(None),
            )
            if section_id:
                grade_query = grade_query.filter(SemesterResult.section_id == section_id)
            subject_grades = {g[0]: g[1] for g in grade_query.group_by(SemesterResult.grade).all()}

            results_list.append({
                "subjectId": sub.id,
                "code": sub.code,
                "name": sub.name,
                "shortName": sub.short_name or sub.code,
                "credits": sub.credits,
                "subjectType": sub.subject_type,
                "studentsWithResults": total_res,
                "studentsWithAttendance": total_att,
                "hasResultData": total_res > 0,
                "hasAttendanceData": total_att > 0,
                "averageMarks": avg_m,
                "highestMarks": highest_m,
                "lowestMarks": lowest_m,
                "passCount": pass_count,
                "failCount": fail_count,
                "passPercentage": pass_pct,
                "averageAttendance": avg_att,
                "gradeDistribution": subject_grades,
            })

        return {
            "semesterId": semester_id,
            "sectionId": section_id,
            "totalSubjects": len(results_list),
            "subjects": results_list,
        }
