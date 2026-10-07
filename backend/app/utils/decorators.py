from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.utils.response import api_error


def role_required(allowed_roles):
    """
    Decorator to restrict endpoint access based on JWT role claim.
    Example: @role_required(['ADMIN', 'HOD'])
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get("role")
                if not user_role or user_role not in allowed_roles:
                    return api_error(
                        message="Forbidden: You do not have sufficient permissions to access this academic resource.",
                        status_code=403,
                        details={"requiredRoles": allowed_roles, "yourRole": user_role}
                    )
                return fn(*args, **kwargs)
            except Exception as e:
                return api_error(message="Unauthorized: Invalid or expired authentication token.", status_code=401, details=str(e))
        return decorator
    return wrapper
