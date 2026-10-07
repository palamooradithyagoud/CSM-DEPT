"""
Deterministic Problem Detectors for Students, Subjects, and Sections.
Directly queries verified database records without duplicating analytical calculations.
Missing data is strictly treated as NOT_AVAILABLE and never produces false-positive alerts.
"""

from sqlalchemy import func
from app.extensions import db
from app.models.academic import (
    Student,
    Semester,
    Subject,
    AttendanceRecord,
    SemesterResult,
    StudentSemesterSummary,
    Section,
)
from app.insights.rules import InsightRules
from app.insights.severity import SeverityLevel, InsightSeverityClassifier
from app.insights.recommendations import RecommendationEngine


class AcademicDetectors:
    """
    Deterministic rule-based detectors identifying academic distress signals.
    """

    @classmethod
    def detect_student_problems(cls, student_id, semester_id=None):
        """
        Runs the complete suite of deterministic detection rules on a single student.
        Returns a structured dictionary with signals, overall severity, and recommendations.
        """
        student = Student.query.get(student_id)
        if not student:
            return None

        thresholds = InsightRules.get_all()
        signals = []

        # -------------------------------------------------------------
        # 1. Fetch Verified Attendance Records
        # -------------------------------------------------------------
        att_query = AttendanceRecord.query.filter_by(student_id=student.id)
        if semester_id:
            att_query = att_query.filter_by(semester_id=semester_id)
        att_records = att_query.all()

        if att_records:
            valid_atts = [a.percentage for a in att_records if a.percentage is not None]
            if valid_atts:
                avg_attendance = round(sum(valid_atts) / len(valid_atts), 2)
                low_att_thresh = thresholds["low_attendance_threshold"]
                crit_att_thresh = thresholds["critical_attendance_threshold"]

                if avg_attendance < low_att_thresh:
                    # Find specific subjects with low attendance
                    affected_subs = []
                    for a in att_records:
                        if a.percentage is not None and a.percentage < low_att_thresh:
                            affected_subs.append({
                                "subject_id": a.subject_id,
                                "subject_code": a.subject.code if a.subject else "UNKNOWN",
                                "subject_name": a.subject.name if a.subject else "Unknown Course",
                                "attendance": round(a.percentage, 2),
                                "classes_attended": a.classes_attended,
                                "total_classes": a.total_classes,
                            })

                    severity = SeverityLevel.CRITICAL if avg_attendance < crit_att_thresh else SeverityLevel.MEDIUM
                    signals.append({
                        "category": "LOW_ATTENDANCE",
                        "severity": severity,
                        "title": "Low Attendance Alert",
                        "reason": f"Overall verified attendance is {avg_attendance}%, below the {low_att_thresh}% monitoring threshold.",
                        "evidence": {
                            "current_attendance": avg_attendance,
                            "threshold": low_att_thresh,
                            "critical_threshold": crit_att_thresh,
                            "total_subjects_evaluated": len(valid_atts),
                        },
                        "affected_subjects": affected_subs,
                    })

        # -------------------------------------------------------------
        # 2. Fetch Verified Results & Failures for Target Semester
        # -------------------------------------------------------------
        res_query = SemesterResult.query.filter_by(student_id=student.id)
        if semester_id:
            res_query = res_query.filter_by(semester_id=semester_id)
        results = res_query.all()

        if results:
            failed_records = [
                r for r in results
                if (r.result_status == "FAILED" or r.grade == "F")
            ]
            if failed_records:
                fail_count = len(failed_records)
                crit_fail_thresh = thresholds["critical_failed_subjects_count"]
                severity = SeverityLevel.CRITICAL if fail_count >= crit_fail_thresh else (
                    SeverityLevel.HIGH if fail_count >= 2 else SeverityLevel.MEDIUM
                )

                failed_subs = [
                    {
                        "subject_id": r.subject_id,
                        "subject_code": r.subject.code if r.subject else "UNKNOWN",
                        "subject_name": r.subject.name if r.subject else "Unknown Course",
                        "grade": r.grade,
                        "total_marks": r.total_marks,
                        "internal_marks": r.internal_marks,
                        "external_marks": r.external_marks,
                    }
                    for r in failed_records
                ]

                signals.append({
                    "category": "FAILED_SUBJECTS",
                    "severity": severity,
                    "title": f"Recorded Course Backlog ({fail_count} Subject{'s' if fail_count > 1 else ''})",
                    "reason": f"Student has recorded failure in {fail_count} subject{'s' if fail_count > 1 else ''} in official examinations.",
                    "evidence": {
                        "failed_count": fail_count,
                        "critical_threshold": crit_fail_thresh,
                    },
                    "affected_subjects": failed_subs,
                })

            # Check for Low Subject Marks (Marks < 50 even if not failed)
            low_marks_subs = [
                r for r in results
                if r.total_marks is not None and r.total_marks < thresholds["combined_low_marks_cutoff"] and r not in failed_records
            ]
            if low_marks_subs:
                signals.append({
                    "category": "LOW_SUBJECT_MARKS",
                    "severity": SeverityLevel.LOW,
                    "title": "Low Course Marks Detected",
                    "reason": f"Student scored below {thresholds['combined_low_marks_cutoff']} marks in {len(low_marks_subs)} passed course(s).",
                    "evidence": {
                        "threshold": thresholds["combined_low_marks_cutoff"],
                        "count": len(low_marks_subs),
                    },
                    "affected_subjects": [
                        {
                            "subject_id": r.subject_id,
                            "subject_code": r.subject.code if r.subject else "UNKNOWN",
                            "subject_name": r.subject.name if r.subject else "Unknown Course",
                            "marks": r.total_marks,
                        }
                        for r in low_marks_subs
                    ],
                })

        # -------------------------------------------------------------
        # 3. Repeated Subject Failure Check (Historical Multi-Semester)
        # -------------------------------------------------------------
        all_student_results = SemesterResult.query.filter_by(student_id=student.id).all()
        failures_by_subject = {}
        for r in all_student_results:
            if r.result_status == "FAILED" or r.grade == "F":
                sub_code = r.subject.code if r.subject else r.subject_id
                sub_name = r.subject.name if r.subject else "Course"
                if sub_code not in failures_by_subject:
                    failures_by_subject[sub_code] = {"name": sub_name, "semesters": set()}
                failures_by_subject[sub_code]["semesters"].add(r.semester_id)

        repeated_failures = [
            (code, data["name"], len(data["semesters"]))
            for code, data in failures_by_subject.items()
            if len(data["semesters"]) > 1
        ]

        for code, name, sem_count in repeated_failures:
            signals.append({
                "category": "REPEATED_FAILURE",
                "severity": SeverityLevel.CRITICAL,
                "title": f"Repeated Subject Failure: {name}",
                "reason": f"Student has recorded failures in {name} ({code}) across {sem_count} distinct semesters.",
                "evidence": {
                    "subject_code": code,
                    "subject_name": name,
                    "distinct_failed_semesters": sem_count,
                },
                "affected_subjects": [{"subject_code": code, "subject_name": name}],
            })

        # -------------------------------------------------------------
        # 4. Longitudinal Progression Trajectory (SGPA Decline & Consecutive Decline)
        # -------------------------------------------------------------
        summaries = StudentSemesterSummary.query.filter_by(student_id=student.id).all()
        if summaries:
            # Order summaries chronologically by semester_number
            sem_ids = [s.semester_id for s in summaries]
            sems = Semester.query.filter(Semester.id.in_(sem_ids)).all()
            sem_num_map = {s.id: s.semester_number for s in sems}
            sem_name_map = {s.id: s.name for s in sems}

            valid_summaries = [s for s in summaries if s.sgpa is not None and s.semester_id in sem_num_map]
            valid_summaries.sort(key=lambda s: sem_num_map[s.semester_id])

            if len(valid_summaries) >= 2:
                tol = thresholds["sgpa_decline_tolerance"]
                sig_thresh = thresholds["significant_decline_threshold"]
                sev_thresh = thresholds["severe_decline_threshold"]

                # A. Immediate Semester Decline Check (T1 -> T2)
                # If semester_id was specified, check transition into this semester
                target_idx = len(valid_summaries) - 1
                if semester_id:
                    for idx, sm in enumerate(valid_summaries):
                        if sm.semester_id == semester_id:
                            target_idx = idx
                            break

                if target_idx > 0:
                    prev_sm = valid_summaries[target_idx - 1]
                    curr_sm = valid_summaries[target_idx]
                    delta = round(curr_sm.sgpa - prev_sm.sgpa, 2)

                    if delta < -tol:
                        drop_mag = abs(delta)
                        severity = SeverityLevel.CRITICAL if drop_mag >= sev_thresh else (
                            SeverityLevel.HIGH if drop_mag >= sig_thresh else SeverityLevel.MEDIUM
                        )
                        signals.append({
                            "category": "SGPA_DECLINE",
                            "severity": severity,
                            "title": "Semester SGPA Performance Decline",
                            "reason": f"SGPA declined by {drop_mag} points from {sem_name_map.get(prev_sm.semester_id, 'Previous')} ({prev_sm.sgpa}) to {sem_name_map.get(curr_sm.semester_id, 'Current')} ({curr_sm.sgpa}).",
                            "evidence": {
                                "previous_semester": sem_name_map.get(prev_sm.semester_id),
                                "previous_sgpa": prev_sm.sgpa,
                                "current_semester": sem_name_map.get(curr_sm.semester_id),
                                "current_sgpa": curr_sm.sgpa,
                                "delta": delta,
                                "tolerance": tol,
                            },
                            "affected_subjects": [],
                        })

                # B. Consecutive Decline Check (Across >= 3 Semesters)
                if len(valid_summaries) >= 3:
                    consec_drops = 0
                    for i in range(1, len(valid_summaries)):
                        step_delta = valid_summaries[i].sgpa - valid_summaries[i - 1].sgpa
                        if step_delta < -tol:
                            consec_drops += 1
                        else:
                            consec_drops = 0

                    if consec_drops >= thresholds["consecutive_decline_min_semesters"]:
                        traj_str = " → ".join([f"{sem_name_map.get(s.semester_id, 'Sem')}: {s.sgpa}" for s in valid_summaries[-(consec_drops + 1):]])
                        signals.append({
                            "category": "CONSECUTIVE_DECLINE",
                            "severity": SeverityLevel.CRITICAL,
                            "title": "Persistent Consecutive SGPA Decline",
                            "reason": f"Student performance has steadily declined across {consec_drops} consecutive semester transitions ({traj_str}).",
                            "evidence": {
                                "consecutive_drop_count": consec_drops,
                                "trajectory_sequence": traj_str,
                            },
                            "affected_subjects": [],
                        })

            # Check Absolute Low SGPA
            latest_sm = valid_summaries[-1]
            if latest_sm.sgpa < thresholds["low_sgpa_threshold"]:
                is_crit = latest_sm.sgpa < thresholds["critical_low_sgpa_threshold"]
                signals.append({
                    "category": "LOW_SGPA",
                    "severity": SeverityLevel.HIGH if is_crit else SeverityLevel.MEDIUM,
                    "title": "Sub-Threshold Semester SGPA",
                    "reason": f"Current semester SGPA is {latest_sm.sgpa}, falling below the {thresholds['low_sgpa_threshold']} academic threshold.",
                    "evidence": {
                        "current_sgpa": latest_sm.sgpa,
                        "threshold": thresholds["low_sgpa_threshold"],
                    },
                    "affected_subjects": [],
                })

        # -------------------------------------------------------------
        # 5. Combined Attendance + Performance Association Signal
        # -------------------------------------------------------------
        # Pair attendance and results for matched subjects in this semester
        if att_records and results:
            att_by_sub = {a.subject_id: a for a in att_records if a.percentage is not None}
            combined_subs = []
            for r in results:
                if r.subject_id in att_by_sub:
                    att_rec = att_by_sub[r.subject_id]
                    if att_rec.percentage < thresholds["combined_low_attendance_cutoff"]:
                        is_low_perf = (
                            (r.total_marks is not None and r.total_marks < thresholds["combined_low_marks_cutoff"]) or
                            r.result_status == "FAILED" or
                            r.grade == "F"
                        )
                        if is_low_perf:
                            combined_subs.append({
                                "subject_code": r.subject.code if r.subject else "UNKNOWN",
                                "subject_name": r.subject.name if r.subject else "Course",
                                "attendance": round(att_rec.percentage, 2),
                                "marks": r.total_marks,
                                "grade": r.grade,
                            })

            if combined_subs:
                sub_names = ", ".join([f"{s['subject_name']} (Att: {s['attendance']}%, Marks: {s['marks'] if s['marks'] is not None else s['grade']})" for s in combined_subs])
                signals.append({
                    "category": "COMBINED_ATTENDANCE_PERFORMANCE",
                    "severity": SeverityLevel.HIGH,
                    "title": "Concurrent Attendance Shortage & Academic Deficit",
                    "reason": f"Low attendance is associated with lower performance in observed records for: {sub_names}.",
                    "evidence": {
                        "subjects": combined_subs,
                        "note": "Observational association between attendance and performance; does not claim direct causation.",
                    },
                    "affected_subjects": combined_subs,
                })

        # -------------------------------------------------------------
        # 6. Overall Severity & Grounded Recommendations Synthesis
        # -------------------------------------------------------------
        overall_severity, primary_reasons = InsightSeverityClassifier.evaluate_student_signals(signals)
        recommendations = RecommendationEngine.generate_student_recommendations(
            signals,
            student_info={"name": student.name, "roll_number": student.roll_number}
        )

        ai_explanation = RecommendationEngine.generate_ai_explanation({
            "student_name": student.name,
            "roll_number": student.roll_number,
            "signals": signals,
        })

        return {
            "student_id": student.id,
            "roll_number": student.roll_number,
            "name": student.name,
            "section_name": student.current_section.name if student.current_section else None,
            "overall_severity": overall_severity,
            "signals_count": len(signals),
            "signals": signals,
            "primary_reasons": primary_reasons,
            "recommendations": recommendations,
            "ai_explanation": ai_explanation,
            "requires_attention": len(signals) > 0,
        }

    @classmethod
    def detect_subject_problems(cls, semester_id, section_id=None):
        """
        Runs deterministic problem detection across all curriculum subjects in a semester.
        """
        from app.analytics.aggregations import AnalyticsAggregations
        from app.analytics.correlation import AnalyticsCorrelation

        thresholds = InsightRules.get_all()
        subj_analytics = AnalyticsAggregations.get_subject_analytics(semester_id, section_id)
        subjects = subj_analytics.get("subjects", [])

        flagged_subjects = []

        for sub in subjects:
            signals = []
            pass_rate = sub.get("passPercentage")
            avg_marks = sub.get("averageMarks")
            fail_count = sub.get("failCount", 0)
            enrolled = sub.get("enrolledStudents", 0)

            # 1. Low Pass Rate
            if pass_rate is not None and pass_rate < thresholds["subject_low_pass_rate_threshold"]:
                signals.append({
                    "category": "LOW_PASS_RATE",
                    "severity": SeverityLevel.HIGH if pass_rate < 50.0 else SeverityLevel.MEDIUM,
                    "reason": f"Pass rate is {pass_rate}%, falling below the {thresholds['subject_low_pass_rate_threshold']}% departmental standard.",
                })

            # 2. Low Average Marks
            if avg_marks is not None and avg_marks < thresholds["subject_low_marks_threshold"]:
                signals.append({
                    "category": "LOW_AVERAGE_MARKS",
                    "severity": SeverityLevel.HIGH if avg_marks < 40.0 else SeverityLevel.MEDIUM,
                    "reason": f"Cohort average mark is {avg_marks}/100, indicating widespread syllabus difficulty.",
                })

            # 3. High Failure Volume
            if fail_count >= thresholds["subject_critical_fail_count"]:
                signals.append({
                    "category": "HIGH_FAILURE_VOLUME",
                    "severity": SeverityLevel.CRITICAL if fail_count >= 20 else SeverityLevel.HIGH,
                    "reason": f"{fail_count} students recorded backlogs in this course ({round((fail_count / enrolled) * 100, 1) if enrolled else 0}% of cohort).",
                })

            if signals:
                highest_sev = SeverityLevel.INFO
                for s in signals:
                    if SeverityLevel.RANK.get(s["severity"], 0) > SeverityLevel.RANK.get(highest_sev, 0):
                        highest_sev = s["severity"]

                recommends = RecommendationEngine.generate_subject_recommendations(sub)

                flagged_subjects.append({
                    "subject_id": sub.get("id"),
                    "subject_code": sub.get("code"),
                    "subject_name": sub.get("name"),
                    "credits": sub.get("credits"),
                    "enrolled_students": enrolled,
                    "average_marks": avg_marks,
                    "pass_percentage": pass_rate,
                    "fail_count": fail_count,
                    "highest_marks": sub.get("highestMarks"),
                    "lowest_marks": sub.get("lowestMarks"),
                    "severity": highest_sev,
                    "signals": signals,
                    "recommendations": recommends,
                    "reason": " • ".join([s["reason"] for s in signals]),
                })

        # Sort by severity descending
        flagged_subjects.sort(key=lambda s: SeverityLevel.RANK.get(s["severity"], 0), reverse=True)
        return flagged_subjects

    @classmethod
    def detect_section_problems(cls, semester_id):
        """
        Runs deterministic problem detection comparing sections within a semester.
        """
        from app.analytics.comparisons import AnalyticsComparisons

        thresholds = InsightRules.get_all()
        sec_data = AnalyticsComparisons.get_section_comparison(semester_id)
        sections = sec_data.get("sections", [])

        if not sections:
            return []

        flagged_sections = []
        for sec in sections:
            signals = []
            avg_att = sec.get("averageAttendance")
            pass_rate = sec.get("passPercentage")
            avg_sgpa = sec.get("averageSGPA")
            total_students = sec.get("totalStudents", 0)

            if avg_att is not None and avg_att < thresholds["section_low_attendance_threshold"]:
                signals.append({
                    "category": "LOW_SECTION_ATTENDANCE",
                    "severity": SeverityLevel.MEDIUM,
                    "reason": f"Section average attendance is {avg_att}%, below the {thresholds['section_low_attendance_threshold']}% benchmark.",
                })

            if pass_rate is not None and pass_rate < thresholds["section_low_pass_rate_threshold"]:
                signals.append({
                    "category": "LOW_SECTION_PASS_RATE",
                    "severity": SeverityLevel.HIGH if pass_rate < 60.0 else SeverityLevel.MEDIUM,
                    "reason": f"Section pass rate is {pass_rate}%, showing elevated failure concentration.",
                })

            if signals:
                highest_sev = SeverityLevel.INFO
                for s in signals:
                    if SeverityLevel.RANK.get(s["severity"], 0) > SeverityLevel.RANK.get(highest_sev, 0):
                        highest_sev = s["severity"]

                recommends = RecommendationEngine.generate_section_recommendations(sec)

                flagged_sections.append({
                    "section_id": sec.get("sectionId"),
                    "section_name": sec.get("sectionName"),
                    "total_students": total_students,
                    "average_sgpa": avg_sgpa,
                    "average_attendance": avg_att,
                    "pass_percentage": pass_rate,
                    "severity": highest_sev,
                    "signals": signals,
                    "recommendations": recommends,
                    "reason": " • ".join([s["reason"] for s in signals]),
                })

        flagged_sections.sort(key=lambda s: SeverityLevel.RANK.get(s["severity"], 0), reverse=True)
        return flagged_sections
