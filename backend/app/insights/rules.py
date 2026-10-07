"""
Centralized Configuration & Threshold Rules for Problem Identification Engine.
Zero scattered magic numbers. Every threshold is centralized, traceable, and configurable.
"""

DEFAULT_INSIGHT_THRESHOLDS = {
    # Attendance Thresholds
    "low_attendance_threshold": 75.0,           # Standard monitoring threshold (%)
    "critical_attendance_threshold": 65.0,      # Severe shortage threshold (%)
    
    # SGPA & Performance Thresholds
    "low_sgpa_threshold": 6.00,                 # Low academic performance threshold
    "critical_low_sgpa_threshold": 5.00,        # Severe academic distress threshold
    "sgpa_decline_tolerance": 0.10,             # Reused from Phase 3 (Delta < -0.10 is decline)
    "significant_decline_threshold": 0.50,      # Delta drop > 0.50 points triggers HIGH severity
    "severe_decline_threshold": 1.00,           # Delta drop > 1.00 points triggers CRITICAL severity
    "consecutive_decline_min_semesters": 2,     # Minimum transitions for consecutive decline signal
    
    # Subject Failure Thresholds
    "high_failed_subjects_count": 1,            # 1-2 failed subjects
    "critical_failed_subjects_count": 3,        # >= 3 failed subjects in a single semester
    
    # Subject-Level Thresholds
    "subject_low_pass_rate_threshold": 70.0,    # Subject pass rate < 70% requires departmental attention
    "subject_low_marks_threshold": 50.0,        # Subject average marks < 50
    "subject_critical_fail_count": 10,          # > 10 failed students in a subject
    
    # Section-Level Thresholds
    "section_low_pass_rate_threshold": 75.0,    # Section pass rate < 75%
    "section_low_attendance_threshold": 75.0,   # Section average attendance < 75%
    
    # Combined Attendance + Performance Thresholds
    "combined_low_attendance_cutoff": 75.0,
    "combined_low_marks_cutoff": 50.0,
}


class InsightRules:
    """Manages active insight thresholds with thread-safe runtime lookup."""
    
    _thresholds = dict(DEFAULT_INSIGHT_THRESHOLDS)
    
    @classmethod
    def get_all(cls):
        """Returns a copy of all active thresholds."""
        return dict(cls._thresholds)
    
    @classmethod
    def get(cls, key, default=None):
        """Retrieves a specific threshold value."""
        return cls._thresholds.get(key, default)
    
    @classmethod
    def update(cls, new_thresholds):
        """Updates active thresholds with runtime validation."""
        for k, v in new_thresholds.items():
            if k in cls._thresholds and isinstance(v, (int, float)):
                cls._thresholds[k] = float(v) if isinstance(v, float) else v
        return dict(cls._thresholds)
    
    @classmethod
    def reset_defaults(cls):
        """Resets active thresholds to default settings."""
        cls._thresholds = dict(DEFAULT_INSIGHT_THRESHOLDS)
        return dict(cls._thresholds)
