"""
Reports Package Initialization.
Exports ReportsService facade for multi-format document generation.
"""

from app.reports.service import ReportsService

__all__ = ["ReportsService"]
