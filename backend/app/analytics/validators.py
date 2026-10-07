from app.models.academic import SemesterResult, AttendanceRecord, StudentSemesterSummary


class AnalyticsValidator:
    """
    Validates academic dataset availability prior to performing analytics.
    Enforces the core principle: NEVER display 0 or 0% when data is 'NOT AVAILABLE'.
    """

    @staticmethod
    def check_result_availability(semester_id, section_id=None):
        """
        Checks whether official semester results or summaries exist for the given semester and optional section.
        """
        query_res = SemesterResult.query.filter_by(semester_id=semester_id)
        if section_id:
            query_res = query_res.filter_by(section_id=section_id)
        has_results = query_res.first() is not None

        query_sum = StudentSemesterSummary.query.filter_by(semester_id=semester_id)
        if section_id:
            query_sum = query_sum.filter_by(section_id=section_id)
        has_summaries = query_sum.first() is not None

        return {
            "available": has_results or has_summaries,
            "has_detailed_results": has_results,
            "has_summaries": has_summaries,
            "message": "Semester result data is available." if (has_results or has_summaries) else "Semester result data is not available.",
        }

    @staticmethod
    def check_attendance_availability(semester_id, section_id=None, subject_id=None):
        """
        Checks whether subject attendance records exist for the given context.
        """
        query = AttendanceRecord.query.filter_by(semester_id=semester_id)
        if section_id:
            query = query.filter_by(section_id=section_id)
        if subject_id:
            query = query.filter_by(subject_id=subject_id)

        count = query.count()
        return {
            "available": count > 0,
            "record_count": count,
            "message": "Attendance data is available." if count > 0 else "Attendance data is not available.",
        }
