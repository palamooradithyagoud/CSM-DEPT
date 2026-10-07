"""
Problem Identification & Intelligent Academic Insights Package.
Transforms verified Phase 2 & 3 data into deterministic, explainable academic insights.
"""

from app.insights.rules import InsightRules, DEFAULT_INSIGHT_THRESHOLDS
from app.insights.severity import SeverityLevel, InsightSeverityClassifier
from app.insights.recommendations import RecommendationEngine
from app.insights.detectors import AcademicDetectors
from app.insights.serializers import InsightSerializer
from app.insights.service import InsightsService

__all__ = [
    "InsightRules",
    "DEFAULT_INSIGHT_THRESHOLDS",
    "SeverityLevel",
    "InsightSeverityClassifier",
    "RecommendationEngine",
    "AcademicDetectors",
    "InsightSerializer",
    "InsightsService",
]
