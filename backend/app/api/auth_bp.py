from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from app.extensions import db
from app.models.user import User
from app.utils.response import api_response, api_error

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate HOD / Admin credentials.
    Body: { "email": str, "password": str }
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return api_error(message="Email and password are required.", status_code=400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return api_error(message="Invalid credentials. Please verify your email and password.", status_code=401)

    if not user.is_active:
        return api_error(message="Your account is deactivated. Contact Department Administrator.", status_code=403)

    user.last_login = datetime.utcnow()
    db.session.commit()

    # Additional claims for token
    additional_claims = {
        "role": user.role,
        "name": user.full_name,
        "department": user.department,
    }

    access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.id, additional_claims=additional_claims)

    return api_response(
        data={
            "user": user.to_dict(),
            "accessToken": access_token,
            "refreshToken": refresh_token,
        },
        message="Login successful. Welcome to the Academic Intelligence System."
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Generate a new access token using a valid refresh token."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return api_error(message="User not found or account inactive.", status_code=401)

    additional_claims = {
        "role": user.role,
        "name": user.full_name,
        "department": user.department,
    }
    new_access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
    return api_response(
        data={"accessToken": new_access_token},
        message="Access token refreshed successfully."
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Get current authenticated user profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return api_error(message="User session not found.", status_code=404)

    return api_response(data={"user": user.to_dict()})
