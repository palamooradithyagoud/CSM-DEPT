"""
Structured Serializers for Problem Insights & Watchlist Entries.
Ensures uniform, explainable schemas across all insight endpoints.
"""


class InsightSerializer:
    """Serializes student, subject, and section insights into consistent JSON structures."""

    @classmethod
    def serialize_student_insight(cls, detected_obj):
        """Standardizes a single student's detected insight profile."""
        if not detected_obj:
            return None

        return {
            "entity_type": "STUDENT",
            "entity_id": detected_obj["student_id"],
            "roll_number": detected_obj["roll_number"],
            "name": detected_obj["name"],
            "section_name": detected_obj.get("section_name"),
            "severity": detected_obj["overall_severity"],
            "requires_attention": detected_obj["requires_attention"],
            "signals_count": detected_obj["signals_count"],
            "primary_reasons": detected_obj["primary_reasons"],
            "signals": detected_obj["signals"],
            "recommendations": detected_obj["recommendations"],
            "ai_explanation": detected_obj.get("ai_explanation"),
        }

    @classmethod
    def serialize_subject_insight(cls, detected_subj):
        """Standardizes a flagged subject insight."""
        return {
            "entity_type": "SUBJECT",
            "entity_id": detected_subj["subject_id"],
            "subject_code": detected_subj["subject_code"],
            "subject_name": detected_subj["subject_name"],
            "credits": detected_subj.get("credits"),
            "enrolled_students": detected_subj.get("enrolled_students"),
            "average_marks": detected_subj.get("average_marks"),
            "pass_percentage": detected_subj.get("pass_percentage"),
            "fail_count": detected_subj.get("fail_count"),
            "severity": detected_subj["severity"],
            "signals": detected_subj["signals"],
            "recommendations": detected_subj["recommendations"],
            "reason": detected_subj["reason"],
        }

    @classmethod
    def serialize_section_insight(cls, detected_sec):
        """Standardizes a flagged section insight."""
        return {
            "entity_type": "SECTION",
            "entity_id": detected_sec["section_id"],
            "section_name": detected_sec["section_name"],
            "total_students": detected_sec.get("total_students"),
            "average_sgpa": detected_sec.get("average_sgpa"),
            "average_attendance": detected_sec.get("average_attendance"),
            "pass_percentage": detected_sec.get("pass_percentage"),
            "severity": detected_sec["severity"],
            "signals": detected_sec["signals"],
            "recommendations": detected_sec["recommendations"],
            "reason": detected_sec["reason"],
        }
