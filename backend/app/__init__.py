import os
from flask import Flask, jsonify
from app.config import config_by_name
from app.extensions import db, jwt, cors, migrate
from app.api.auth_bp import auth_bp
from app.api.public_bp import public_bp
from app.api.academic_bp import academic_bp
from app.api.uploads_bp import uploads_bp
from app.api.analytics_bp import analytics_bp
from app.utils.response import api_error, api_response



def create_app(config_name=None):
    """Flask application factory."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # JWT Error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return api_error(message="Missing authentication token. Please log in.", status_code=401)

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return api_error(message="Invalid authentication token signature.", status_code=401)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return api_error(message="Token has expired. Please refresh session or log in again.", status_code=401)

    # Register blueprints
    app.register_blueprint(public_bp, url_prefix="/api/v1/public")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(academic_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(analytics_bp)



    # System Health Check
    @app.route("/api/v1/health", methods=["GET"])
    def health_check():
        return api_response(
            data={"status": "online", "service": "Student Academic Management API", "version": "1.0.0"},
            message="System is operational."
        )

    # Standard error handlers
    @app.errorhandler(404)
    def not_found(e):
        return api_error(message="Requested API resource not found.", status_code=404)

    @app.errorhandler(500)
    def internal_error(e):
        return api_error(message="An internal server error occurred.", status_code=500, details=str(e))

    return app
