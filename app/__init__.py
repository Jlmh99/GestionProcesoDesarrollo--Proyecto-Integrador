import os

from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

from app.models import db
from app.routes import api
from app.schemas import error


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    os.makedirs(app.instance_path, exist_ok=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + os.path.join(app.instance_path, "webapp.db")
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["BACKUP_DIR"] = os.path.join(
        app.instance_path,
        "backups"
    )

    # Permite modificar la configuración cuando se ejecutan pruebas
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    app.register_blueprint(api)

    swagger_url = "/swagger"
    swagger_api_url = "/static/swagger.json"

    swagger_blueprint = get_swaggerui_blueprint(
        swagger_url,
        swagger_api_url,
        config={"app_name": "WebApp API - Practica DevOps"}
    )

    app.register_blueprint(
        swagger_blueprint,
        url_prefix=swagger_url
    )

    @app.get("/")
    def inicio():
        return jsonify({
            "statusCode": 200,
            "data": {
                "mensaje": "WebApp API funcionando",
                "documentacion": "/swagger"
            }
        }), 200

    @app.errorhandler(404)
    def no_encontrado(_):
        return jsonify(
            error(404, "Recurso no encontrado.")
        ), 404

    @app.errorhandler(405)
    def metodo_no_permitido(_):
        return jsonify(
            error(405, "Método HTTP no permitido.")
        ), 405

    @app.errorhandler(500)
    def error_servidor(_):
        db.session.rollback()
        return jsonify(
            error(500, "Error interno del servidor.")
        ), 500

    with app.app_context():
        db.create_all()

    return app