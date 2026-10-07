import math
from app.extensions import db
from app.models.academic import AttendanceRecord, SemesterResult, Student, Subject


class AnalyticsCorrelation:
    """
    Computes statistical association between Subject-Wise Attendance and Academic Performance (Marks).
    Adheres strictly to statistical guidelines:
    - Pearson r calculation
    - Minimum sample size threshold (n >= 5)
    - Zero variation / constant values safety
    - Strict wording: 'Association between attendance and academic performance' (NOT causality).
    """

    MINIMUM_SAMPLE_SIZE = 5

    @classmethod
    def get_attendance_vs_performance(cls, semester_id, section_id=None, subject_id=None):
        """
        Pairs verified attendance percentages with semester total marks for matched (student, subject) records.
        """
        # Join AttendanceRecord and SemesterResult on student_id, subject_id, semester_id
        query = db.session.query(
            AttendanceRecord.student_id,
            AttendanceRecord.subject_id,
            AttendanceRecord.percentage.label("attendance"),
            SemesterResult.total_marks.label("marks"),
            SemesterResult.grade,
            SemesterResult.grade_point,
            Student.roll_number,
            Student.name.label("student_name"),
            Subject.code.label("subject_code"),
            Subject.name.label("subject_name"),
        ).join(
            SemesterResult,
            (AttendanceRecord.student_id == SemesterResult.student_id) &
            (AttendanceRecord.subject_id == SemesterResult.subject_id) &
            (AttendanceRecord.semester_id == SemesterResult.semester_id)
        ).join(
            Student, AttendanceRecord.student_id == Student.id
        ).join(
            Subject, AttendanceRecord.subject_id == Subject.id
        ).filter(
            AttendanceRecord.semester_id == semester_id,
            AttendanceRecord.percentage.isnot(None),
        )

        if section_id:
            query = query.filter(AttendanceRecord.section_id == section_id)
        if subject_id:
            query = query.filter(AttendanceRecord.subject_id == subject_id)

        rows = query.all()

        data_points = []
        valid_pairs = []

        for r in rows:
            att = float(r.attendance)
            # Use total_marks, or fallback to grade_point * 10 if total_marks is not present
            marks = float(r.marks) if r.marks is not None else (float(r.grade_point * 10) if r.grade_point is not None else None)

            if marks is not None:
                valid_pairs.append((att, marks))
                data_points.append({
                    "studentId": r.student_id,
                    "rollNumber": r.roll_number,
                    "studentName": r.student_name,
                    "subjectCode": r.subject_code,
                    "subjectName": r.subject_name,
                    "attendance": round(att, 2),
                    "marks": round(marks, 2),
                    "grade": r.grade,
                })

        return cls.calculate_correlation(valid_pairs, data_points)

    @classmethod
    def calculate_correlation(cls, valid_pairs, data_points=None):
        if data_points is None:
            data_points = []
        n = len(valid_pairs)

        # 1. Sample Size Check
        if n < cls.MINIMUM_SAMPLE_SIZE:
            return {
                "status": "INSUFFICIENT_DATA",
                "sampleSize": n,
                "minimumRequired": cls.MINIMUM_SAMPLE_SIZE,
                "correlation": None,
                "interpretation": "Insufficient data for correlation (minimum 5 paired samples required).",
                "dataPoints": data_points,
                "trendline": None,
                "terminology": "Association between attendance and academic performance",
            }

        # 2. Compute Means
        x_vals = [p[0] for p in valid_pairs]
        y_vals = [p[1] for p in valid_pairs]

        mean_x = sum(x_vals) / n
        mean_y = sum(y_vals) / n

        # Sum of squares
        ss_xx = sum((x - mean_x) ** 2 for x in x_vals)
        ss_yy = sum((y - mean_y) ** 2 for y in y_vals)
        ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in valid_pairs)

        # 3. Variance / Constant Values Check
        if ss_xx == 0 or ss_yy == 0:
            return {
                "status": "UNDEFINED_VARIATION",
                "sampleSize": n,
                "correlation": None,
                "interpretation": "Correlation cannot be determined from the available variation (constant values detected).",
                "dataPoints": data_points,
                "trendline": None,
                "averageAttendance": round(mean_x, 2),
                "averageMarks": round(mean_y, 2),
                "terminology": "Association between attendance and academic performance",
            }

        # 4. Pearson r
        denom = math.sqrt(ss_xx * ss_yy)
        r = ss_xy / denom
        r = max(min(r, 1.0), -1.0)  # clamp to [-1, 1]
        r_rounded = round(r, 3)

        # Interpretation
        abs_r = abs(r)
        if abs_r >= 0.7:
            strength = "Strong"
        elif abs_r >= 0.4:
            strength = "Moderate"
        elif abs_r >= 0.2:
            strength = "Weak"
        else:
            strength = "Negligible"

        direction = "positive" if r > 0 else "negative"
        interpretation = f"{strength} {direction} association observed between subject attendance and marks."

        # Trendline: y = slope * x + intercept
        slope = round(ss_xy / ss_xx, 4)
        intercept = round(mean_y - (slope * mean_x), 4)

        return {
            "status": "SUCCESS",
            "sampleSize": n,
            "correlation": r_rounded,
            "interpretation": interpretation,
            "averageAttendance": round(mean_x, 2),
            "averageMarks": round(mean_y, 2),
            "trendline": {
                "slope": slope,
                "intercept": intercept,
                "formula": f"Marks = {slope} * Attendance + {intercept}",
            },
            "dataPoints": data_points,
            "terminology": "Association between attendance and academic performance",
            "note": "Statistical association does not imply direct causation.",
        }
