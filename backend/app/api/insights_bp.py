"""
Protected REST API Blueprint for Academic Problem Identification & Insights.
Strictly restricted to HOD and ADMIN roles via JWT verification.
Public users are blocked with 401/403 to prevent private academic records leakage.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.utils.decorators import role_required
from app.utils.response import api_response, api_error
from app.insights.service import InsightsService

insights_bp = Blueprint("insights_bp", __name__, url_prefix="/api/v1/insights")


@insights_bp.route("/overview", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def get_insights_overview():
    """
    Returns overarching problem identification metrics and priority insights feed.
    Query params: batch_id, academic_year_id, semester_id, section_id
    """
    batch_id = request.args.get("batch_id")
    academic_year_id = request.args.get("academic_year_id")
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")

    try:
        data = InsightsService.get_insights_overview(
            batch_id=batch_id,
            academic_year_id=academic_year_id,
            semester_id=semester_id,
            section_id=section_id,
        )
        return api_response(data=data, message="Academic insights overview retrieved successfully.")
    except Exception as e:
        return api_error(message=f"Failed to generate insights overview: {str(e)}", status_code=500)


@insights_bp.route("/students", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def get_student_watchlist():
    """
    Returns filtered and paginated student watchlist of identified academic issues.
    Query params: batch_id, academic_year_id, semester_id, section_id, severity, category, search, page, limit
    """
    batch_id = request.args.get("batch_id")
    academic_year_id = request.args.get("academic_year_id")
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")
    severity = request.args.get("severity")
    category = request.args.get("category")
    search = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 25, type=int)

    try:
        data = InsightsService.get_student_watchlist(
            batch_id=batch_id,
            academic_year_id=academic_year_id,
            semester_id=semester_id,
            section_id=section_id,
            severity=severity,
            category=category,
            search=search,
            page=page,
            limit=limit,
        )
        return api_response(data=data, message="Student watchlist retrieved successfully.")
    except Exception as e:
        return api_error(message=f"Failed to retrieve student watchlist: {str(e)}", status_code=500)


@insights_bp.route("/students/<student_id>", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def get_single_student_insights(student_id):
    """
    Returns comprehensive diagnostic signals and recommendations for an individual student.
    Query params: semester_id (optional)
    """
    semester_id = request.args.get("semester_id")
    try:
        data = InsightsService.get_single_student_insights(student_id, semester_id)
        if not data:
            return api_error(message="Student not found.", status_code=404)
        return api_response(data=data, message="Student insights profile retrieved successfully.")
    except ValueError as ve:
        return api_error(message=str(ve), status_code=404)
    except Exception as e:
        return api_error(message=f"Failed to retrieve student insights: {str(e)}", status_code=500)


@insights_bp.route("/subjects", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def get_subject_insights():
    """
    Returns curriculum subjects requiring departmental attention.
    Query params: semester_id (required), section_id (optional)
    """
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")

    if not semester_id:
        return api_error(message="Query parameter 'semester_id' is required.", status_code=400)

    try:
        data = InsightsService.get_subject_insights(semester_id, section_id)
        return api_response(data={"subjects": data}, message="Subject insights retrieved successfully.")
    except Exception as e:
        return api_error(message=f"Failed to generate subject insights: {str(e)}", status_code=500)


@insights_bp.route("/sections", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def get_section_insights():
    """
    Returns section cohorts showing comparative academic signals.
    Query params: semester_id (required)
    """
    semester_id = request.args.get("semester_id")

    if not semester_id:
        return api_error(message="Query parameter 'semester_id' is required.", status_code=400)

    try:
        data = InsightsService.get_section_insights(semester_id)
        return api_response(data={"sections": data}, message="Section insights retrieved successfully.")
    except Exception as e:
        return api_error(message=f"Failed to generate section insights: {str(e)}", status_code=500)


@insights_bp.route("/config", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def get_threshold_config():
    """
    Returns active configurable detection thresholds.
    """
    try:
        thresholds = InsightsService.get_thresholds()
        return api_response(data={"thresholds": thresholds}, message="Active thresholds retrieved successfully.")
    except Exception as e:
        return api_error(message=f"Failed to retrieve thresholds: {str(e)}", status_code=500)


@insights_bp.route("/config", methods=["POST"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def update_threshold_config():
    """
    Updates configurable detection thresholds at runtime.
    """
    payload = request.get_json() or {}
    try:
        updated = InsightsService.update_thresholds(payload)
        return api_response(data={"thresholds": updated}, message="Thresholds updated successfully.")
    except Exception as e:
        return api_error(message=f"Failed to update thresholds: {str(e)}", status_code=500)


@insights_bp.route("/recommendations/<entity_type>/<entity_id>", methods=["GET"])
@jwt_required()
@role_required(["ADMIN", "HOD"])
def get_entity_recommendations(entity_type, entity_id):
    """
    Retrieves grounded recommendations for a specific entity (STUDENT, SUBJECT, or SECTION).
    """
    entity_type_upper = entity_type.upper()
    try:
        if entity_type_upper == "STUDENT":
            insights = InsightsService.get_single_student_insights(entity_id)
            if not insights:
                return api_error(message="Student not found.", status_code=404)
            return api_response(
                data={
                    "entity_type": "STUDENT",
                    "entity_id": entity_id,
                    "recommendations": insights.get("recommendations", []),
                    "ai_explanation": insights.get("ai_explanation"),
                },
                message="Student recommendations retrieved.",
            )
        elif entity_type_upper == "SUBJECT":
            # entity_id is subject_id, need semester_id from query params
            semester_id = request.args.get("semester_id")
            if not semester_id:
                return api_error(message="Parameter 'semester_id' is required for subject recommendations.", status_code=400)
            subs = InsightsService.get_subject_insights(semester_id)
            matching = next((s for s in subs if s.get("entity_id") == entity_id), None)
            if not matching:
                return api_response(
                    data={"entity_type": "SUBJECT", "entity_id": entity_id, "recommendations": []},
                    message="No special recommendations required.",
                )
            return api_response(
                data={"entity_type": "SUBJECT", "entity_id": entity_id, "recommendations": matching.get("recommendations", [])},
                message="Subject recommendations retrieved.",
            )
        else:
            return api_error(message=f"Unsupported entity type: {entity_type}", status_code=400)
    except Exception as e:
        return api_error(message=f"Failed to fetch recommendations: {str(e)}", status_code=500)
