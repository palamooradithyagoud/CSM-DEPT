from typing import Dict, Any, Optional, List
from sqlalchemy import func
from app.extensions import db
from app.models.academic import (
    Batch,
    AcademicYear,
    Semester,
    Section,
    Student,
    Subject,
    AttendanceRecord,
    SemesterResult,
    StudentSemesterSummary,
)


class AnalyticsLeaderboard:
    """
    Department Academic Leaderboard & Merit Standings Engine.
    Maps student performance across Semester 1, Semester 2, and cumulative CGPA.
    Provides section-wise and overall year cohort rankings with distinction metrics.
    """

    @classmethod
    def get_leaderboard(
        cls,
        batch_id: Optional[str] = None,
        academic_year_id: Optional[str] = None,
        section_id: Optional[str] = None,
        view_mode: str = "cumulative",
        limit: int = 100,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Builds the complete Leaderboard mapped across Semester 1 and Semester 2.
        view_mode: 'cumulative' | 'sem1' | 'sem2' | 'attendance'
        """
        # 1. Resolve Batch
        if batch_id:
            batch = Batch.query.get(batch_id)
        else:
            batch = Batch.query.filter_by(is_active=True).first() or Batch.query.first()

        if not batch:
            return {
                "cohort": {},
                "summary": {"totalStudents": 0, "rankedCount": 0},
                "rankings": [],
                "podium": [],
                "topImprovers": [],
            }

        # 2. Resolve Academic Year and Semesters (Sem 1 and Sem 2)
        if academic_year_id:
            ay = AcademicYear.query.filter_by(id=academic_year_id, batch_id=batch.id).first()
        else:
            ay = AcademicYear.query.filter_by(batch_id=batch.id, year_number=1).first() or AcademicYear.query.filter_by(batch_id=batch.id).first()

        sem1 = None
        sem2 = None
        if ay:
            sems = Semester.query.filter_by(academic_year_id=ay.id).order_by(Semester.semester_number.asc()).all()
            if len(sems) >= 1:
                sem1 = sems[0]
            if len(sems) >= 2:
                sem2 = sems[1]

        # Fallback if semesters belong to batch across years
        if not sem1:
            sem1 = Semester.query.filter_by(semester_number=1).first()
        if not sem2:
            sem2 = Semester.query.filter_by(semester_number=2).first()

        # 3. Query Students for this Batch
        student_query = Student.query.filter_by(batch_id=batch.id, is_active=True)

        # Section Filter
        filter_section = None
        if section_id and str(section_id).strip().upper() not in ["OVERALL", "ALL", "NONE", ""]:
            student_query = student_query.filter(Student.current_section_id == section_id)
            filter_section = Section.query.get(section_id)

        # Search Filter
        if search and search.strip():
            term = f"%{search.strip().upper()}%"
            student_query = student_query.filter(
                db.or_(
                    Student.roll_number.ilike(term),
                    Student.name.ilike(term)
                )
            )

        students = student_query.all()

        # 4. Preload Performance Data
        sem1_id = sem1.id if sem1 else None
        sem2_id = sem2.id if sem2 else None

        # Summaries
        s1_summaries = {}
        s2_summaries = {}
        if sem1_id:
            for s in StudentSemesterSummary.query.filter_by(semester_id=sem1_id).all():
                s1_summaries[s.student_id] = s
        if sem2_id:
            for s in StudentSemesterSummary.query.filter_by(semester_id=sem2_id).all():
                s2_summaries[s.student_id] = s

        # Results
        s1_results = {}
        s2_results = {}
        if sem1_id:
            for r in SemesterResult.query.filter_by(semester_id=sem1_id).all():
                s1_results.setdefault(r.student_id, []).append(r)
        if sem2_id:
            for r in SemesterResult.query.filter_by(semester_id=sem2_id).all():
                s2_results.setdefault(r.student_id, []).append(r)

        # Attendance
        s1_attendance = {}
        s2_attendance = {}
        if sem1_id:
            for a in AttendanceRecord.query.filter_by(semester_id=sem1_id).all():
                s1_attendance.setdefault(a.student_id, []).append(a.percentage)
        if sem2_id:
            for a in AttendanceRecord.query.filter_by(semester_id=sem2_id).all():
                s2_attendance.setdefault(a.student_id, []).append(a.percentage)

        # 5. Build Student Rows
        student_rows = []
        for st in students:
            # Sem 1 metrics
            sum1 = s1_summaries.get(st.id)
            res1 = s1_results.get(st.id, [])
            att1 = s1_attendance.get(st.id, [])

            sgpa1 = sum1.sgpa if sum1 and sum1.sgpa is not None else None
            if sgpa1 is None and res1:
                pts = [r.grade_point for r in res1 if r.grade_point is not None]
                if pts:
                    sgpa1 = round(sum(pts) / len(pts), 2)

            passed1 = sum(1 for r in res1 if r.result_status == "PASSED" or (r.grade and r.grade not in ["F", "AB"]))
            total1 = len(res1)
            tot_marks1 = round(sum(r.total_marks for r in res1 if r.total_marks is not None), 1) if res1 else None
            att_avg1 = round(sum(att1) / len(att1), 1) if att1 else None

            # Sem 2 metrics
            sum2 = s2_summaries.get(st.id)
            res2 = s2_results.get(st.id, [])
            att2 = s2_attendance.get(st.id, [])

            sgpa2 = sum2.sgpa if sum2 and sum2.sgpa is not None else None
            if sgpa2 is None and res2:
                pts = [r.grade_point for r in res2 if r.grade_point is not None]
                if pts:
                    sgpa2 = round(sum(pts) / len(pts), 2)

            passed2 = sum(1 for r in res2 if r.result_status == "PASSED" or (r.grade and r.grade not in ["F", "AB"]))
            total2 = len(res2)
            tot_marks2 = round(sum(r.total_marks for r in res2 if r.total_marks is not None), 1) if res2 else None
            att_avg2 = round(sum(att2) / len(att2), 1) if att2 else None

            # Cumulative Calculation
            if sgpa1 is not None and sgpa2 is not None:
                cgpa = round((sgpa1 + sgpa2) / 2.0, 2)
                sgpa_change = round(sgpa2 - sgpa1, 2)
            elif sgpa1 is not None:
                cgpa = round(sgpa1, 2)
                sgpa_change = None
            elif sgpa2 is not None:
                cgpa = round(sgpa2, 2)
                sgpa_change = None
            else:
                cgpa = None
                sgpa_change = None

            # Overall Attendance
            all_atts = att1 + att2
            overall_att = round(sum(all_atts) / len(all_atts), 1) if all_atts else None

            # Academic Standing
            if cgpa is not None:
                if cgpa >= 9.0:
                    standing = "Outstanding"
                    standing_color = "gold"
                elif cgpa >= 8.0:
                    standing = "Distinction"
                    standing_color = "purple"
                elif cgpa >= 6.5:
                    standing = "First Class"
                    standing_color = "blue"
                elif cgpa >= 5.0:
                    standing = "Second Class"
                    standing_color = "cyan"
                else:
                    standing = "Remedial Needed"
                    standing_color = "danger"
            else:
                standing = "Awaiting Results"
                standing_color = "gray"

            sec_name = st.current_section.name if st.current_section else "—"

            student_rows.append({
                "studentId": st.id,
                "rollNumber": st.roll_number,
                "name": st.name,
                "section": sec_name,
                "sectionId": st.current_section_id,
                "email": st.email,
                "sem1": {
                    "sgpa": sgpa1,
                    "passedSubjects": passed1,
                    "totalSubjects": total1,
                    "totalMarks": tot_marks1,
                    "attendancePct": att_avg1,
                    "available": bool(res1 or sum1),
                },
                "sem2": {
                    "sgpa": sgpa2,
                    "passedSubjects": passed2,
                    "totalSubjects": total2,
                    "totalMarks": tot_marks2,
                    "attendancePct": att_avg2,
                    "available": bool(res2 or sum2),
                },
                "cumulative": {
                    "cgpa": cgpa,
                    "sgpaChange": sgpa_change,
                    "overallAttendancePct": overall_att,
                    "totalPassed": passed1 + passed2,
                    "totalCourses": total1 + total2,
                    "standing": standing,
                    "standingColor": standing_color,
                },
            })

        # 6. Sorting & Ranking based on view_mode
        if view_mode == "sem1":
            student_rows.sort(
                key=lambda s: (
                    s["sem1"]["sgpa"] is not None,
                    s["sem1"]["sgpa"] or 0.0,
                    s["sem1"]["totalMarks"] or 0.0,
                    -(s["sem1"]["totalSubjects"] - s["sem1"]["passedSubjects"]),
                ),
                reverse=True,
            )
        elif view_mode == "sem2":
            student_rows.sort(
                key=lambda s: (
                    s["sem2"]["sgpa"] is not None,
                    s["sem2"]["sgpa"] or 0.0,
                    s["sem2"]["totalMarks"] or 0.0,
                    -(s["sem2"]["totalSubjects"] - s["sem2"]["passedSubjects"]),
                ),
                reverse=True,
            )
        elif view_mode == "attendance":
            student_rows.sort(
                key=lambda s: (
                    s["cumulative"]["overallAttendancePct"] is not None,
                    s["cumulative"]["overallAttendancePct"] or 0.0,
                    s["cumulative"]["cgpa"] or 0.0,
                ),
                reverse=True,
            )
        else:  # 'cumulative'
            student_rows.sort(
                key=lambda s: (
                    s["cumulative"]["cgpa"] is not None,
                    s["cumulative"]["cgpa"] or 0.0,
                    s["sem2"]["sgpa"] or 0.0,
                    s["sem1"]["sgpa"] or 0.0,
                ),
                reverse=True,
            )

        # Assign Ranks
        ranked_list = []
        for idx, row in enumerate(student_rows, start=1):
            rank_obj = dict(row)
            rank_obj["rank"] = idx
            if idx == 1:
                rank_obj["medal"] = "🥇"
                rank_obj["rankBadge"] = "Rank 1 (Gold)"
            elif idx == 2:
                rank_obj["medal"] = "🥈"
                rank_obj["rankBadge"] = "Rank 2 (Silver)"
            elif idx == 3:
                rank_obj["medal"] = "🥉"
                rank_obj["rankBadge"] = "Rank 3 (Bronze)"
            elif idx <= 10:
                rank_obj["medal"] = None
                rank_obj["rankBadge"] = "Top 10"
            else:
                rank_obj["medal"] = None
                rank_obj["rankBadge"] = None
            ranked_list.append(rank_obj)

        # 7. Cohort Summary & Top Improvers
        active_ranked = [s for s in ranked_list if s["cumulative"]["cgpa"] is not None]
        valid_cgpas = [s["cumulative"]["cgpa"] for s in active_ranked]
        s1_sgpas = [s["sem1"]["sgpa"] for s in ranked_list if s["sem1"]["sgpa"] is not None]
        s2_sgpas = [s["sem2"]["sgpa"] for s in ranked_list if s["sem2"]["sgpa"] is not None]

        improvers = [
            s for s in ranked_list
            if s["cumulative"]["sgpaChange"] is not None and s["cumulative"]["sgpaChange"] > 0
        ]
        improvers.sort(key=lambda s: s["cumulative"]["sgpaChange"], reverse=True)

        # Podium: Top 3 students with available scores
        podium = [s for s in ranked_list if s.get("medal")][:3]

        return {
            "cohort": {
                "batchName": batch.name,
                "academicYear": ay.name if ay else "1st Year",
                "sem1Name": sem1.name if sem1 else "Semester 1",
                "sem2Name": sem2.name if sem2 else "Semester 2",
                "sectionScope": filter_section.name if filter_section else "Overall Year (All Sections)",
                "viewMode": view_mode,
            },
            "summary": {
                "totalStudents": len(students),
                "rankedCount": len(active_ranked),
                "bothSemestersCount": sum(1 for s in ranked_list if s["sem1"]["available"] and s["sem2"]["available"]),
                "highestCgpa": max(valid_cgpas, default=0.0),
                "highestSgpaSem1": max(s1_sgpas, default=0.0),
                "highestSgpaSem2": max(s2_sgpas, default=0.0),
                "averageCgpa": round(sum(valid_cgpas) / len(valid_cgpas), 2) if valid_cgpas else 0.0,
                "distinctionCount": sum(1 for c in valid_cgpas if c >= 8.0),
                "firstClassCount": sum(1 for c in valid_cgpas if 6.5 <= c < 8.0),
                "passPercentage": round((sum(1 for c in valid_cgpas if c >= 5.0) / len(valid_cgpas) * 100), 1) if valid_cgpas else 0.0,
            },
            "podium": podium,
            "topImprovers": improvers[:5],
            "rankings": ranked_list[:limit],
        }
