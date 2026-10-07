import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.academic import UploadHistory
from app.services.ingestion_service import IngestionService, TEMP_UPLOAD_CACHE
from app.utils.decorators import role_required

uploads_bp = Blueprint("uploads", __name__, url_prefix="/api/v1/uploads")


@uploads_bp.route("/validate", methods=["POST"])
@role_required(["ADMIN", "HOD"])
def validate_upload():
    """
    Step 1 - 7 of upload pipeline:
    Receives file and academic context:
    batchId, academicYearId, semesterId, sectionId, dataType.
    Parses file, runs full schema and row-level validation, checks duplicates,
    and returns comprehensive validation summary with paginated preview.
    """
    batch_id = request.form.get("batchId") or request.form.get("batch_id")
    academic_year_id = request.form.get("academicYearId") or request.form.get("academic_year_id")
    semester_id = request.form.get("semesterId") or request.form.get("semester_id")
    section_id = request.form.get("sectionId") or request.form.get("section_id")
    data_type = (request.form.get("dataType") or request.form.get("data_type") or "").strip().upper()

    # Rule: Attendance must be section-wise (A, B, C); Results default to overall year (all sections A, B, C)
    if data_type == "ATTENDANCE":
        if not section_id or str(section_id).strip().upper() in ["OVERALL", "ALL", "NONE", ""]:
            return jsonify({
                "success": False,
                "message": "Attendance must be Section-Wise. Please select Section A, B, or C.",
            }), 400
    else:
        if not section_id or str(section_id).strip().upper() in ["OVERALL", "ALL", "NONE", ""]:
            section_id = "OVERALL"

    if not all([batch_id, academic_year_id, semester_id, section_id, data_type]):
        return jsonify({
            "success": False,
            "message": "All context fields are required: batchId, academicYearId, semesterId, sectionId, dataType.",
        }), 400

    if data_type not in IngestionService.SUPPORTED_DATA_TYPES:
        return jsonify({
            "success": False,
            "message": f"Unsupported dataType '{data_type}'. Must be one of: {', '.join(IngestionService.SUPPORTED_DATA_TYPES)}",
        }), 400

    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded. Please provide an Excel or CSV file."}), 400

    uploaded_file = request.files["file"]
    filename = uploaded_file.filename
    if not filename:
        return jsonify({"success": False, "message": "Empty filename."}), 400

    try:
        # 1. Parse raw rows
        raw_rows, _ = IngestionService.parse_file_to_rows(uploaded_file, filename)

        # 2. Normalize rows (Matrix or Tabular)
        normalized_records = IngestionService.normalize_tabular_data(raw_rows, data_type)
        if not normalized_records:
            return jsonify({
                "success": False,
                "message": "No valid data records could be extracted from this file format.",
            }), 400

        # 3. Validate entire dataset against academic context & database
        validation_report = IngestionService.validate_dataset(
            normalized_records,
            batch_id=batch_id,
            academic_year_id=academic_year_id,
            semester_id=semester_id,
            section_id=section_id,
            data_type=data_type,
        )

        # 4. Cache valid dataset for confirmation step
        file_token = str(uuid.uuid4())
        user_identity = get_jwt_identity()
        user_email = user_identity.get("email") if isinstance(user_identity, dict) else "HOD"

        TEMP_UPLOAD_CACHE[file_token] = {
            "valid_records": validation_report["valid_records"],
            "batch_id": batch_id,
            "academic_year_id": academic_year_id,
            "semester_id": semester_id,
            "section_id": section_id,
            "data_type": data_type,
            "filename": filename,
            "uploaded_by": user_email,
        }

        # Keep cache bounded
        if len(TEMP_UPLOAD_CACHE) > 50:
            oldest_key = next(iter(TEMP_UPLOAD_CACHE))
            TEMP_UPLOAD_CACHE.pop(oldest_key, None)

        return jsonify({
            "success": True,
            "fileToken": file_token,
            "filename": filename,
            "dataType": data_type,
            "summary": {
                "totalRows": validation_report["total_rows"],
                "validRows": validation_report["valid_rows"],
                "invalidRows": validation_report["invalid_rows"],
                "duplicatesCount": validation_report["duplicates_count"],
                "totalErrors": validation_report["total_errors"],
            },
            "errors": validation_report["errors"],
            "warnings": validation_report["warnings"],
            "previewRows": validation_report["preview_rows"],
            "extractedSubjects": validation_report.get("extracted_subjects", []),
        }), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Validation failed: {str(e)}"}), 500


@uploads_bp.route("/confirm", methods=["POST"])
@role_required(["ADMIN", "HOD"])
def confirm_upload():
    """
    Step 8 - 10 of upload pipeline:
    Receives fileToken and duplicateStrategy: 'SKIP' | 'REPLACE' | 'CANCEL'.
    Executes atomic database transaction and commits or rolls back completely.
    """
    data = request.get_json() or {}
    file_token = data.get("fileToken")
    duplicate_strategy = (data.get("duplicateStrategy") or "SKIP").strip().upper()

    if not file_token or file_token not in TEMP_UPLOAD_CACHE:
        return jsonify({
            "success": False,
            "message": "Invalid or expired fileToken. Please re-validate the file before confirming.",
        }), 400

    if duplicate_strategy not in ["SKIP", "REPLACE", "CANCEL"]:
        return jsonify({
            "success": False,
            "message": "duplicateStrategy must be one of 'SKIP', 'REPLACE', or 'CANCEL'.",
        }), 400

    cached = TEMP_UPLOAD_CACHE[file_token]

    try:
        import_result = IngestionService.execute_transactional_import(
            valid_records=cached["valid_records"],
            batch_id=cached["batch_id"],
            academic_year_id=cached["academic_year_id"],
            semester_id=cached["semester_id"],
            section_id=cached["section_id"],
            data_type=cached["data_type"],
            duplicate_strategy=duplicate_strategy,
            uploaded_by=cached["uploaded_by"],
            filename=cached["filename"],
        )

        # Clear cache on successful import
        TEMP_UPLOAD_CACHE.pop(file_token, None)

        return jsonify({
            "success": True,
            "message": "Academic records imported successfully with atomic transaction.",
            "data": import_result,
        }), 200

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Unexpected import error: {str(e)}"}), 500


@uploads_bp.route("/history", methods=["GET"])
@role_required(["ADMIN", "HOD"])
def get_upload_history():
    """
    Audit log of all uploaded academic datasets.
    """
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))

    query = UploadHistory.query.order_by(UploadHistory.uploaded_at.desc())
    total = query.count()
    records = query.offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        "success": True,
        "data": [r.to_dict() for r in records],
        "page": page,
        "limit": limit,
        "total": total,
    }), 200
