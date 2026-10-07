"""
Actionable Academic Recommendations Engine & Grounded Explanations.
Recommendations are structured, pedagogical suggestions grounded directly in detected evidence.
Never fatalistic ('Student will fail'); always supportive ('Student may benefit from academic mentoring').
"""

import os
from app.insights.severity import SeverityLevel


class RecommendationEngine:
    """
    Generates grounded departmental and student-level recommendations based on detected signals.
    """

    @classmethod
    def generate_student_recommendations(cls, signals, student_info=None):
        """
        Produces prioritized, evidence-backed recommendations for a flagged student.
        """
        recommendations = []
        categories = {s.get("category") for s in signals}

        # 1. Low Attendance Recommendations
        if "LOW_ATTENDANCE" in categories:
            att_signal = next(s for s in signals if s.get("category") == "LOW_ATTENDANCE")
            evidence = att_signal.get("evidence", {})
            curr_att = evidence.get("current_attendance")
            aff_subs = att_signal.get("affected_subjects", [])

            if aff_subs:
                sub_names = ", ".join([f"{s.get('subject_name')} ({s.get('attendance')}%)" for s in aff_subs[:2]])
                recommendations.append({
                    "action_type": "ATTENDANCE_INTERVENTION",
                    "title": "Subject-Specific Attendance Counseling",
                    "description": f"Schedule counseling with student regarding attendance deficits in {sub_names}.",
                    "priority": "HIGH" if (curr_att and curr_att < 65) else "MEDIUM",
                })
            else:
                recommendations.append({
                    "action_type": "ATTENDANCE_MONITORING",
                    "title": "Mandatory Attendance Notification",
                    "description": f"Issue attendance advisory notice to student and proctor. Current attendance is {curr_att}%.",
                    "priority": "MEDIUM",
                })

        # 2. Failed Subjects Recommendations
        if "FAILED_SUBJECTS" in categories:
            fail_signal = next(s for s in signals if s.get("category") == "FAILED_SUBJECTS")
            failed_subs = fail_signal.get("affected_subjects", [])
            sub_list_str = ", ".join([s.get("subject_name", "") for s in failed_subs]) if failed_subs else "affected courses"
            
            recommendations.append({
                "action_type": "REMEDIAL_ENROLLMENT",
                "title": "Remedial Tutorial Sessions",
                "description": f"Recommend enrollment in departmental tutorial hours for failed course(s): {sub_list_str}.",
                "priority": "HIGH",
            })
            recommendations.append({
                "action_type": "FACULTY_CONSULTATION",
                "title": "Subject Faculty Diagnostic Review",
                "description": "Coordinate diagnostic feedback with respective course instructors to isolate syllabus learning gaps.",
                "priority": "MEDIUM",
            })

        # 3. Repeated Failure Recommendations
        if "REPEATED_FAILURE" in categories:
            rep_signal = next(s for s in signals if s.get("category") == "REPEATED_FAILURE")
            sub_name = rep_signal.get("evidence", {}).get("subject_name", "the repeated course")
            recommendations.append({
                "action_type": "FOCUSED_ACADEMIC_INTERVENTION",
                "title": "Intensive Academic Intervention Plan",
                "description": f"Student has recorded multi-semester backlog in {sub_name}. Assign designated faculty mentor for one-on-one progress tracking.",
                "priority": "CRITICAL",
            })

        # 4. SGPA Decline Recommendations
        if "SGPA_DECLINE" in categories or "CONSECUTIVE_DECLINE" in categories:
            decline_signal = next((s for s in signals if s.get("category") in ("CONSECUTIVE_DECLINE", "SGPA_DECLINE")), None)
            delta = decline_signal.get("evidence", {}).get("delta", 0) if decline_signal else 0
            is_consecutive = "CONSECUTIVE_DECLINE" in categories
            
            recommendations.append({
                "action_type": "ACADEMIC_MENTORING",
                "title": "Comprehensive Semester Performance Review",
                "description": f"{'Multi-semester consecutive SGPA decline' if is_consecutive else f'Performance drop of {abs(delta)} SGPA points'} warrants mentor-led study strategy evaluation.",
                "priority": "HIGH" if is_consecutive else "MEDIUM",
            })

        # 5. Combined Attendance + Performance
        if "COMBINED_ATTENDANCE_PERFORMANCE" in categories:
            recommendations.append({
                "action_type": "HOLISTIC_COUNSELING",
                "title": "Dual-Factor Academic Support",
                "description": "Both low attendance and low exam marks are concurrently present. Engage class teacher to assess potential personal, health, or schedule constraints.",
                "priority": "HIGH",
            })

        # Default fallback if no specific rule matched
        if not recommendations:
            recommendations.append({
                "action_type": "ROUTINE_MONITORING",
                "title": "Routine Academic Supervision",
                "description": "Maintain standard departmental progress observation through the class proctor.",
                "priority": "LOW",
            })

        return recommendations

    @classmethod
    def generate_subject_recommendations(cls, subject_data):
        """
        Produces departmental curriculum recommendations for a flagged subject.
        """
        recommends = []
        pass_pct = subject_data.get("passPercentage")
        avg_marks = subject_data.get("averageMarks")
        fail_count = subject_data.get("failCount", 0)

        if pass_pct is not None and pass_pct < 70.0:
            recommends.append({
                "action_type": "SYLLABUS_PACING_REVIEW",
                "title": "Curriculum Pacing & Tutorial Hours",
                "description": f"Pass rate is {pass_pct}%. Department may review lecture pacing and introduce 2 weekly problem-solving tutorial hours.",
                "priority": "HIGH",
            })

        if avg_marks is not None and avg_marks < 50.0:
            recommends.append({
                "action_type": "INTERNAL_ASSESSMENT_AUDIT",
                "title": "Internal Assessment Alignment",
                "description": f"Average mark is {avg_marks}/100. Review difficulty calibration of mid-term examinations and assignment problem sets.",
                "priority": "HIGH",
            })

        if fail_count >= 10:
            recommends.append({
                "action_type": "BRIDGE_COURSE",
                "title": "Organize Departmental Bridge Classes",
                "description": f"{fail_count} students recorded backlogs. Conduct weekend revision bootcamps before upcoming supplementary examinations.",
                "priority": "HIGH",
            })

        if not recommends:
            recommends.append({
                "action_type": "CURRICULUM_MONITORING",
                "title": "Maintain Curriculum Trajectory",
                "description": "Subject performance remains within expected departmental parameters.",
                "priority": "LOW",
            })

        return recommends

    @classmethod
    def generate_section_recommendations(cls, section_data):
        """
        Produces recommendations for an entire section cohort.
        """
        recommends = []
        avg_sgpa = section_data.get("averageSGPA")
        avg_att = section_data.get("averageAttendance")
        pass_pct = section_data.get("passPercentage")

        if avg_att is not None and avg_att < 75.0:
            recommends.append({
                "action_type": "SECTION_ATTENDANCE_DRIVE",
                "title": "Section-Wide Attendance Audit",
                "description": f"Section average attendance is {avg_att}%. Request section coordinator to verify biometric attendance records and follow up with parents.",
                "priority": "HIGH",
            })

        if pass_pct is not None and pass_pct < 75.0:
            recommends.append({
                "action_type": "COHORT_REMEDIAL_SCHEDULE",
                "title": "Cohort Remedial Timetable Optimization",
                "description": f"Section pass percentage is {pass_pct}%. Arrange remedial study blocks for courses showing heavy failure concentrations.",
                "priority": "HIGH",
            })

        if not recommends:
            recommends.append({
                "action_type": "SECTION_SUPERVISION",
                "title": "Routine Section Oversight",
                "description": "Section performance is balanced across curriculum subjects.",
                "priority": "LOW",
            })

        return recommends

    @classmethod
    def generate_ai_explanation(cls, structured_evidence):
        """
        Generates an optional AI-assisted explanatory synthesis strictly grounded in the provided evidence.
        If an external LLM is not configured, returns a deterministic evidence-based pedagogical synthesis.
        """
        # Strict rule: AI explanation is strictly bounded by deterministic facts.
        student_name = structured_evidence.get("student_name", "The student")
        roll = structured_evidence.get("roll_number", "")
        signals = structured_evidence.get("signals", [])
        
        reasons = [s.get("reason") for s in signals if s.get("reason")]
        if not reasons:
            return "Academic records reflect steady progression within normal departmental parameters."

        synthesis_points = "; ".join(reasons)
        return (
            f"Academic Diagnostic Summary for {student_name} ({roll}): "
            f"Departmental detection identified {len(signals)} attention signal(s): {synthesis_points}. "
            f"Timely mentor intervention and targeted academic support are advised to facilitate performance recovery."
        )
