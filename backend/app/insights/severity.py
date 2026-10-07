"""
Deterministic & Explainable Severity Classification Model.
Zero opaque 'AI risk scores'. Every severity assignment has an explicit, traceable reason.
"""


class SeverityLevel:
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

    RANK = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
        "INFO": 0,
    }


class InsightSeverityClassifier:
    """
    Evaluates individual and composite academic signals to assign an explainable severity level.
    """

    @classmethod
    def evaluate_student_signals(cls, signals):
        """
        Calculates overall student severity from a collection of detected signals.
        Returns (highest_severity, primary_reasons).
        """
        if not signals:
            return SeverityLevel.INFO, ["No academic distress signals detected."]

        severities = [s.get("severity", SeverityLevel.INFO) for s in signals]
        highest_rank = max(SeverityLevel.RANK.get(sev, 0) for sev in severities)
        
        # Invert rank lookup to get top severity
        rank_to_sev = {v: k for k, v in SeverityLevel.RANK.items()}
        highest_severity = rank_to_sev.get(highest_rank, SeverityLevel.INFO)

        # Composite escalation rule:
        # Multiple HIGH signals escalate to CRITICAL
        high_count = sum(1 for s in signals if s.get("severity") == SeverityLevel.HIGH)
        critical_count = sum(1 for s in signals if s.get("severity") == SeverityLevel.CRITICAL)
        
        if critical_count > 0 or high_count >= 2:
            highest_severity = SeverityLevel.CRITICAL
        elif high_count == 1:
            highest_severity = SeverityLevel.HIGH

        reasons = [s.get("reason") for s in signals if s.get("reason")]
        return highest_severity, reasons

    @classmethod
    def compare_severity(cls, sev1, sev2):
        """Returns positive if sev1 > sev2, negative if sev1 < sev2, 0 if equal."""
        return SeverityLevel.RANK.get(sev1, 0) - SeverityLevel.RANK.get(sev2, 0)
