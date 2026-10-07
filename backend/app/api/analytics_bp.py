from flask import Blueprint, request, jsonify
from app.analytics.service import AnalyticsService
from app.utils.decorators import role_required

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/v1/analytics")


@analytics_bp.route("/overview", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_overview_kpis():
    """
    Overarching departmental KPI summary:
    Total students, Average SGPA, Average CGPA, Average Attendance %, Pass %, Passed/Failed counts.
    """
    batch_id = request.args.get("batch_id")
    academic_year_id = request.args.get("academic_year_id")
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")

    try:
        data = AnalyticsService.get_overview(
            batch_id=batch_id,
            academic_year_id=academic_year_id,
            semester_id=semester_id,
            section_id=section_id,
        )
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to compute overview analytics: {str(e)}"}), 500


@analytics_bp.route("/sections", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_section_comparison():
    """
    Cross-Section comparative performance for a semester:
    Compares Sections A, B, C... on Enrolled Count, Avg SGPA, Avg Attendance, Pass %.
    """
    semester_id = request.args.get("semester_id")
    if not semester_id:
        return jsonify({"success": False, "message": "semester_id is required for section comparison."}), 400

    try:
        data = AnalyticsService.get_section_comparison(semester_id)
        return jsonify({"success": True, "data": data}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to compute section comparison: {str(e)}"}), 500


@analytics_bp.route("/subjects", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_subject_analytics():
    """
    Subject-level performance:
    Average marks, Highest, Lowest, Pass count, Fail count, Pass %, Average Attendance, Grade breakdown.
    """
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")
    subject_id = request.args.get("subject_id")

    if not semester_id:
        return jsonify({"success": False, "message": "semester_id is required for subject analytics."}), 400

    try:
        data = AnalyticsService.get_subject_analytics(
            semester_id=semester_id,
            section_id=section_id,
            subject_id=subject_id,
        )
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to compute subject analytics: {str(e)}"}), 500


@analytics_bp.route("/semester-comparison", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_semester_comparison():
    """
    Longitudinal Semester-to-Semester progression analysis:
    Previous SGPA vs Current SGPA, Delta, Deterministic classification (IMPROVED, DECLINED, STABLE).
    """
    batch_id = request.args.get("batch_id")
    sem1_id = request.args.get("sem1_id")
    sem2_id = request.args.get("sem2_id")
    section_id = request.args.get("section_id")
    tolerance = float(request.args.get("tolerance", 0.10))

    if not sem1_id or not sem2_id:
        return jsonify({"success": False, "message": "sem1_id and sem2_id are required for semester comparison."}), 400

    try:
        data = AnalyticsService.get_semester_comparison(
            batch_id=batch_id,
            sem1_id=sem1_id,
            sem2_id=sem2_id,
            section_id=section_id,
            tolerance=tolerance,
        )
        return jsonify({"success": True, "data": data}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to compute semester comparison: {str(e)}"}), 500


@analytics_bp.route("/student/<student_id>", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_student_analytics(student_id):
    """
    Individual student analytical profile:
    Current CGPA, Latest SGPA, Overall Attendance, Progression Trajectory, Performance Trend, Subject Breakdown.
    """
    try:
        data = AnalyticsService.get_student_analytics(student_id)
        return jsonify({"success": True, "data": data}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to compute student analytics: {str(e)}"}), 500


@analytics_bp.route("/student/<student_id>/trajectory", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_student_trajectory(student_id):
    """
    Returns only the semester progression trajectory for charting.
    """
    try:
        data = AnalyticsService.get_student_analytics(student_id)
        return jsonify({"success": True, "data": data["trajectory"]}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to retrieve trajectory: {str(e)}"}), 500


@analytics_bp.route("/attendance-performance", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_attendance_performance():
    """
    Statistical association between subject attendance % and examination marks:
    Pearson correlation r, sample size, scatter points, trendline.
    """
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")
    subject_id = request.args.get("subject_id")

    if not semester_id:
        return jsonify({"success": False, "message": "semester_id is required for attendance-performance analysis."}), 400

    try:
        data = AnalyticsService.get_attendance_vs_performance(
            semester_id=semester_id,
            section_id=section_id,
            subject_id=subject_id,
        )
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to compute attendance-performance association: {str(e)}"}), 500


@analytics_bp.route("/grades", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_grade_distribution():
    """
    Dynamic distribution of official grades (O, A+, A, B+, B, C, P, F, AB).
    """
    semester_id = request.args.get("semester_id")
    section_id = request.args.get("section_id")
    subject_id = request.args.get("subject_id")

    if not semester_id:
        return jsonify({"success": False, "message": "semester_id is required for grade distribution."}), 400

    try:
        data = AnalyticsService.get_grade_distribution(
            semester_id=semester_id,
            section_id=section_id,
            subject_id=subject_id,
        )
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to compute grade distribution: {str(e)}"}), 500


@analytics_bp.route("/leaderboard", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_leaderboard():
    """
    Department Academic Leaderboard & Merit Standings.
    Maps student performance across Semester 1, Semester 2, and cumulative CGPA.
    Supports overall year ranking and section-wise filtering.
    """
    batch_id = request.args.get("batch_id")
    academic_year_id = request.args.get("academic_year_id")
    section_id = request.args.get("section_id")
    view_mode = (request.args.get("view_mode") or "cumulative").lower()
    limit = int(request.args.get("limit", 100))
    search = request.args.get("search")

    try:
        data = AnalyticsService.get_leaderboard(
            batch_id=batch_id,
            academic_year_id=academic_year_id,
            section_id=section_id,
            view_mode=view_mode,
            limit=limit,
            search=search,
        )
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to compute leaderboard: {str(e)}"}), 500
