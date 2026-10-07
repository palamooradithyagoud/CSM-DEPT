from flask import jsonify


def api_response(data=None, message="Success", status_code=200, meta=None):
    """Standardized API success response envelope."""
    payload = {
        "success": True,
        "message": message,
        "data": data,
    }
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status_code


def api_error(message="An error occurred", status_code=400, details=None):
    """Standardized API error response envelope."""
    payload = {
        "success": False,
        "message": message,
        "error": {
            "code": status_code,
            "details": details,
        },
    }
    return jsonify(payload), status_code
