from sqlalchemy import func, distinct
from app.extensions import db
from app.models.academic import (
    Semester,
    Section,
    Student,
    StudentSemesterSummary,
    SemesterResult,
    AttendanceRecord,
)
from app.analytics.validators import AnalyticsValidator


class AnalyticsComparisons:
    """
    Deterministic comparative analytics:
    1. Cross-Section comparison within a semester.
    2. Longitudinal Semester-to-Semester progression analysis.
    """

    @classmethod
    def get_section_comparison(cls, semester_id):
        """
        Compares all sections in a semester across Enrolled Students, Avg SGPA, Avg Attendance, and Pass %.
        """
        semester = Semester.query.get(semester_id)
        if not semester:
            raise ValueError(f"Semester with ID '{semester_id}' not found.")

        sections = Section.query.filter_by(semester_id=semester_id).order_by(Section.name.asc()).all()

        comparisons = []
        for sec in sections:
            # 1. Total Enrolled Students
            total_students = Student.query.filter_by(current_section_id=sec.id, is_active=True).count()

            # 2. Avg SGPA
            sgpa_row = db.session.query(
                func.avg(StudentSemesterSummary.sgpa).label("avg_sgpa"),
                func.count(distinct(StudentSemesterSummary.student_id)).label("count"),
            ).filter(
                StudentSemesterSummary.semester_id == semester_id,
                StudentSemesterSummary.section_id == sec.id,
                StudentSemesterSummary.sgpa.isnot(None)
            ).first()

            avg_sgpa = round(float(sgpa_row.avg_sgpa), 2) if sgpa_row and sgpa_row.avg_sgpa is not None else None
            students_with_results = int(sgpa_row.count) if sgpa_row and sgpa_row.count else 0

            # Fallback to SemesterResult grade_point if summary not uploaded
            if avg_sgpa is None:
                gp_row = db.session.query(
                    func.avg(SemesterResult.grade_point).label("avg_gp"),
                    func.count(distinct(SemesterResult.student_id)).label("count"),
                ).filter(
                    SemesterResult.semester_id == semester_id,
                    SemesterResult.section_id == sec.id,
                    SemesterResult.grade_point.isnot(None)
                ).first()
                if gp_row and gp_row.avg_gp is not None:
                    avg_sgpa = round(float(gp_row.avg_gp), 2)
                    students_with_results = int(gp_row.count)

            # 3. Avg Attendance
            att_row = db.session.query(
                func.avg(AttendanceRecord.percentage).label("avg_att"),
                func.count(distinct(AttendanceRecord.student_id)).label("count"),
            ).filter(
                AttendanceRecord.semester_id == semester_id,
                AttendanceRecord.section_id == sec.id,
            ).first()

            avg_att = round(float(att_row.avg_att), 2) if att_row and att_row.avg_att is not None else None
            students_with_att = int(att_row.count) if att_row and att_row.count else 0

            # 4. Pass Percentage
            # Distinct students in section with results
            sec_res_q = db.session.query(SemesterResult.student_id).filter(
                SemesterResult.semester_id == semester_id,
                SemesterResult.section_id == sec.id,
            ).distinct()
            sec_students_res_set = {r[0] for r in sec_res_q.all()}

            # Failed students in section
            sec_failed_q = db.session.query(SemesterResult.student_id).filter(
                SemesterResult.semester_id == semester_id,
                SemesterResult.section_id == sec.id,
                db.or_(SemesterResult.result_status == "FAILED", SemesterResult.grade == "F")
            ).distinct()
            sec_failed_set = {r[0] for r in sec_failed_q.all()}


            pass_count = len(sec_students_res_set) - len(sec_failed_set)
            pass_pct = round((pass_count / len(sec_students_res_set)) * 100, 2) if len(sec_students_res_set) > 0 else None

            comparisons.append({
                "sectionId": sec.id,
                "sectionName": sec.name,
                "roomNumber": sec.room_number,
                "totalStudents": total_students,
                "averageSGPA": avg_sgpa,
                "averageAttendance": avg_att,
                "passPercentage": pass_pct,
                "studentsWithResults": len(sec_students_res_set) if len(sec_students_res_set) > 0 else students_with_results,
                "studentsWithAttendance": students_with_att,
                "resultsAvailable": avg_sgpa is not None or len(sec_students_res_set) > 0,
                "attendanceAvailable": avg_att is not None,
            })

        return {
            "semesterId": semester.id,
            "semesterName": semester.name,
            "totalSections": len(comparisons),
            "sections": comparisons,
        }

    @classmethod
    def get_semester_comparison(cls, batch_id, sem1_id, sem2_id, section_id=None, tolerance=0.10):
        """
        Compares consecutive semesters with deterministic classification:
        change > tolerance  => 'IMPROVED'
        change < -tolerance => 'DECLINED'
        otherwise           => 'STABLE'
        Only compares students with verified SGPA data in BOTH semesters.
        """
        sem1 = Semester.query.get(sem1_id)
        sem2 = Semester.query.get(sem2_id)
        if not sem1 or not sem2:
            raise ValueError("Both Semester 1 and Semester 2 must be valid entities.")

        # Check availability
        avail1 = AnalyticsValidator.check_result_availability(sem1_id, section_id)
        avail2 = AnalyticsValidator.check_result_availability(sem2_id, section_id)

        if not avail1["available"] or not avail2["available"]:
            return {
                "available": False,
                "sem1Name": sem1.name,
                "sem2Name": sem2.name,
                "studentsCompared": 0,
                "message": f"Comparison requires results in both semesters. Missing in: {sem1.name if not avail1['available'] else ''} {sem2.name if not avail2['available'] else ''}".strip(),
            }

        # Helper to fetch map of {student_id: sgpa} for a semester
        def fetch_sgpa_map(sem_id):
            # Check summaries first
            q = db.session.query(
                StudentSemesterSummary.student_id,
                StudentSemesterSummary.sgpa
            ).filter(
                StudentSemesterSummary.semester_id == sem_id,
                StudentSemesterSummary.sgpa.isnot(None)
            )
            if section_id:
                q = q.filter(StudentSemesterSummary.section_id == section_id)
            mapping = {r[0]: float(r[1]) for r in q.all()}

            # If empty, check average grade points from results
            if not mapping:
                q_res = db.session.query(
                    SemesterResult.student_id,
                    func.avg(SemesterResult.grade_point).label("avg_gp")
                ).filter(
                    SemesterResult.semester_id == sem_id,
                    SemesterResult.grade_point.isnot(None)
                ).group_by(SemesterResult.student_id)
                if section_id:
                    q_res = q_res.filter(SemesterResult.section_id == section_id)
                mapping = {r[0]: round(float(r[1]), 2) for r in q_res.all()}

            return mapping

        map1 = fetch_sgpa_map(sem1_id)
        map2 = fetch_sgpa_map(sem2_id)

        # Intersect students present in both semesters
        common_student_ids = set(map1.keys()) & set(map2.keys())
        if not common_student_ids:
            return {
                "available": True,
                "sem1Name": sem1.name,
                "sem2Name": sem2.name,
                "studentsCompared": 0,
                "message": "No students found with result records in both selected semesters.",
                "summary": None,
                "students": [],
            }

        # Fetch student entity details
        students = Student.query.filter(Student.id.in_(list(common_student_ids))).all()
        student_obj_map = {s.id: s for s in students}

        student_comparisons = []
        improved_count = 0
        declined_count = 0
        stable_count = 0

        sum_sem1 = 0.0
        sum_sem2 = 0.0
        sum_change = 0.0

        for s_id in common_student_ids:
            st = student_obj_map.get(s_id)
            if not st:
                continue

            s1_val = map1[s_id]
            s2_val = map2[s_id]
            change = round(s2_val - s1_val, 2)

            if change > tolerance:
                status = "IMPROVED"
                improved_count += 1
            elif change < -tolerance:
                status = "DECLINED"
                declined_count += 1
            else:
                status = "STABLE"
                stable_count += 1

            sum_sem1 += s1_val
            sum_sem2 += s2_val
            sum_change += change

            student_comparisons.append({
                "studentId": st.id,
                "rollNumber": st.roll_number,
                "studentName": st.name,
                "sectionName": st.current_section.name if st.current_section else None,
                "sem1SGPA": s1_val,
                "sem2SGPA": s2_val,
                "change": change,
                "status": status,
            })

        # Sort students by roll number
        student_comparisons.sort(key=lambda x: x["rollNumber"])
        n = len(student_comparisons)

        avg_sem1 = round(sum_sem1 / n, 2) if n > 0 else 0.0
        avg_sem2 = round(sum_sem2 / n, 2) if n > 0 else 0.0
        avg_change = round(sum_change / n, 2) if n > 0 else 0.0

        return {
            "available": True,
            "sem1Id": sem1.id,
            "sem1Name": sem1.name,
            "sem2Id": sem2.id,
            "sem2Name": sem2.name,
            "tolerance": tolerance,
            "classificationRule": f"change > +{tolerance} (IMPROVED) | change < -{tolerance} (DECLINED) | otherwise (STABLE)",
            "summary": {
                "studentsCompared": n,
                "improvedCount": improved_count,
                "declinedCount": declined_count,
                "stableCount": stable_count,
                "improvedPercentage": round((improved_count / n) * 100, 1) if n > 0 else 0.0,
                "declinedPercentage": round((declined_count / n) * 100, 1) if n > 0 else 0.0,
                "stablePercentage": round((stable_count / n) * 100, 1) if n > 0 else 0.0,
                "averageSem1SGPA": avg_sem1,
                "averageSem2SGPA": avg_sem2,
                "averageChange": avg_change,
            },
            "students": student_comparisons,
        }
