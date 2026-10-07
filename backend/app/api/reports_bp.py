"""
Protected REST API Blueprint for Academic Reports and Document Exports.
Strictly restricted to HOD and ADMIN roles via JWT authentication and RBAC.
Public users are rejected with 401/403 to prevent private academic records leakage.
"""

from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required
from app.utils.decorators import role_required
from app.utils.response import api_error, api_response
from app.reports.service import ReportsService

reports_bp = Blueprint("reports_bp", __name__, url_prefix="/api/v1/reports")


@reports_bp.route("/department", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def export_department_report():
    """
    Exports comprehensive departmental academic performance report.
    Query params: batch_id, academic_year_id, semester_id, format (pdf|excel|csv)
    """
    batch_id = request.args.get("batch_id")
    academic_year_id = request.args.get("academic_year_id")
    semester_id = request.args.get("semester_id")
    export_format = request.args.get("format", "pdf").lower()

    if export_format not in ["pdf", "excel", "csv"]:
        return api_error(message=f"Unsupported format '{export_format}'. Allowed: pdf, excel, csv", status_code=400)

    try:
        data = ReportsService.get_department_report_data(
            batch_id=batch_id,
            academic_year_id=academic_year_id,
            semester_id=semester_id,
        )
        content, mimetype, filename = ReportsService.export_report("department", data, export_format)

        return Response(
            content,
            mimetype=mimetype,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": mimetype,
            }
        )
    except Exception as e:
        return api_error(message=f"Failed to generate department report: {str(e)}", status_code=500)


@reports_bp.route("/section/<section_id>", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def export_section_report(section_id):
    """
    Exports section performance report with subject breakdown and attention watchlist.
    Query params: semester_id, format (pdf|excel|csv)
    """
    semester_id = request.args.get("semester_id")
    export_format = request.args.get("format", "pdf").lower()

    if export_format not in ["pdf", "excel", "csv"]:
        return api_error(message=f"Unsupported format '{export_format}'. Allowed: pdf, excel, csv", status_code=400)

    try:
        data = ReportsService.get_section_report_data(section_id, semester_id=semester_id)
        if not data:
            return api_error(message=f"Section with ID '{section_id}' not found.", status_code=404)

        content, mimetype, filename = ReportsService.export_report("section", data, export_format)

        return Response(
            content,
            mimetype=mimetype,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": mimetype,
            }
        )
    except Exception as e:
        return api_error(message=f"Failed to generate section report: {str(e)}", status_code=500)


@reports_bp.route("/student/<student_id>", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def export_student_report(student_id):
    """
    Exports individual student academic dossier with trajectory and pedagogical recommendations.
    Query params: semester_id, format (pdf|excel|csv)
    """
    semester_id = request.args.get("semester_id")
    export_format = request.args.get("format", "pdf").lower()

    if export_format not in ["pdf", "excel", "csv"]:
        return api_error(message=f"Unsupported format '{export_format}'. Allowed: pdf, excel, csv", status_code=400)

    try:
        data = ReportsService.get_student_report_data(student_id, semester_id=semester_id)
        if not data:
            return api_error(message=f"Student with ID or roll number '{student_id}' not found.", status_code=404)

        content, mimetype, filename = ReportsService.export_report("student", data, export_format)

        return Response(
            content,
            mimetype=mimetype,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": mimetype,
            }
        )
    except Exception as e:
        return api_error(message=f"Failed to generate student report: {str(e)}", status_code=500)


@reports_bp.route("/subject/<subject_id>", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def export_subject_report(subject_id):
    """
    Exports course performance diagnostic report across sections.
    Query params: semester_id, format (pdf|excel|csv)
    """
    semester_id = request.args.get("semester_id")
    export_format = request.args.get("format", "pdf").lower()

    if export_format not in ["pdf", "excel", "csv"]:
        return api_error(message=f"Unsupported format '{export_format}'. Allowed: pdf, excel, csv", status_code=400)

    try:
        data = ReportsService.get_subject_report_data(subject_id, semester_id=semester_id)
        if not data:
            return api_error(message=f"Subject with ID '{subject_id}' not found.", status_code=404)

        content, mimetype, filename = ReportsService.export_report("subject", data, export_format)

        return Response(
            content,
            mimetype=mimetype,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": mimetype,
            }
        )
    except Exception as e:
        return api_error(message=f"Failed to generate subject report: {str(e)}", status_code=500)


@reports_bp.route("/insights", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def export_insights_report():
    """
    Exports academic insights and diagnostic watchlist report.
    Query params: batch_id, academic_year_id, semester_id, section_id, format (pdf|excel|csv)
    """
    batch_id = request.args.get("batch_id")
    academic_year_id = request.args.get("academic_year_id")
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")
    export_format = request.args.get("format", "pdf").lower()

    if export_format not in ["pdf", "excel", "csv"]:
        return api_error(message=f"Unsupported format '{export_format}'. Allowed: pdf, excel, csv", status_code=400)

    try:
        data = ReportsService.get_insights_report_data(
            batch_id=batch_id,
            academic_year_id=academic_year_id,
            semester_id=semester_id,
            section_id=section_id,
        )
        content, mimetype, filename = ReportsService.export_report("insights", data, export_format)

        return Response(
            content,
            mimetype=mimetype,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": mimetype,
            }
        )
    except Exception as e:
        return api_error(message=f"Failed to generate insights report: {str(e)}", status_code=500)


@reports_bp.route("/preview", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def preview_report_data():
    """
    Returns JSON preview of report dataset before initiating file export.
    Query params: type (department|section|student|subject|insights), id, batch_id, semester_id, section_id
    """
    report_type = request.args.get("type", "department").lower()
    entity_id = request.args.get("id")
    batch_id = request.args.get("batch_id")
    academic_year_id = request.args.get("academic_year_id")
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")

    try:
        if report_type == "department":
            data = ReportsService.get_department_report_data(batch_id, academic_year_id, semester_id)
        elif report_type == "section":
            if not entity_id:
                return api_error("Section ID required for section report preview.", status_code=400)
            data = ReportsService.get_section_report_data(entity_id, semester_id)
        elif report_type == "student":
            if not entity_id:
                return api_error("Student ID required for student report preview.", status_code=400)
            data = ReportsService.get_student_report_data(entity_id, semester_id)
        elif report_type == "subject":
            if not entity_id:
                return api_error("Subject ID required for subject report preview.", status_code=400)
            data = ReportsService.get_subject_report_data(entity_id, semester_id)
        elif report_type == "insights":
            data = ReportsService.get_insights_report_data(batch_id, academic_year_id, semester_id, section_id)
        else:
            return api_error(f"Unknown report type: {report_type}", status_code=400)

        if data is None:
            return api_error("Requested entity data not found.", status_code=404)

        return api_response(data=data, message="Report preview retrieved successfully.")
    except Exception as e:
        return api_error(message=f"Failed to preview report: {str(e)}", status_code=500)
