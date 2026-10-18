"""
Microservicio de Lista Negra Global de Emails
Flask + SQLAlchemy + RESTful + Marshmallow + JWT Extended + PostgreSQL (RDS)

AWS Elastic Beanstalk busca por defecto un objeto llamado `application`
dentro de `application.py`. No cambies esos nombres.
"""
import os
import uuid
from datetime import datetime, timezone

from flask import Flask, request
from flask_jwt_extended import JWTManager, jwt_required
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError, fields, validate

# Cambia este valor en cada despliegue (1.1, 1.2, ...) para ver en /ping
# qué versión responde mientras pruebas las estrategias de despliegue.
APP_VERSION = "1.0"


def build_database_uri():
    """Usa DATABASE_URL si existe; si no, arma la URL con las variables RDS_*;
    si tampoco hay, usa SQLite local (solo para desarrollo)."""
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    if os.environ.get("RDS_HOSTNAME"):
        return "postgresql://{u}:{p}@{h}:{port}/{db}".format(
            u=os.environ["RDS_USERNAME"],
            p=os.environ["RDS_PASSWORD"],
            h=os.environ["RDS_HOSTNAME"],
            port=os.environ.get("RDS_PORT", "5432"),
            db=os.environ.get("RDS_DB_NAME", "blacklistdb"),
        )
    return "sqlite:///local.db"


application = Flask(__name__)
application.config["SQLALCHEMY_DATABASE_URI"] = build_database_uri()
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
application.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "cambia-esta-clave-secreta-de-al-menos-32-caracteres")
application.config["PROPAGATE_EXCEPTIONS"] = True

db = SQLAlchemy(application)
ma = Marshmallow(application)
jwt = JWTManager(application)
api = Api(application)


# ---------------------------------------------------------------- Modelo
class Blacklist(db.Model):
    __tablename__ = "blacklist"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    app_uuid = db.Column(db.String(36), nullable=False)
    blocked_reason = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------- Esquemas
class BlacklistInputSchema(ma.Schema):
    email = fields.Email(required=True)
    app_uuid = fields.UUID(required=True)
    blocked_reason = fields.String(required=False, allow_none=True,
                                   validate=validate.Length(max=255))


class BlacklistOutputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Blacklist
        load_instance = True


input_schema = BlacklistInputSchema()
output_schema = BlacklistOutputSchema()


# ---------------------------------------------------------------- Errores JWT
@jwt.unauthorized_loader
def missing_token(reason):
    return {"msg": "Token de autorización faltante", "detail": reason}, 401


@jwt.invalid_token_loader
def invalid_token(reason):
    return {"msg": "Token inválido", "detail": reason}, 401


def client_ip():
    """Detrás del Load Balancer la IP real llega en X-Forwarded-For."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "desconocida"


# ---------------------------------------------------------------- Recursos
class BlacklistResource(Resource):
    @jwt_required()
    def post(self):
        payload = request.get_json(silent=True)
        if payload is None:
            return {"msg": "El cuerpo debe ser un JSON válido"}, 400
        try:
            data = input_schema.load(payload)
        except ValidationError as err:
            return {"msg": "Datos inválidos", "errors": err.messages}, 400

        email = data["email"].strip().lower()
        if Blacklist.query.filter_by(email=email).first():
            return {"msg": f"El email {email} ya está en la lista negra global"}, 409

        entry = Blacklist(
            email=email,
            app_uuid=str(data["app_uuid"]),
            blocked_reason=data.get("blocked_reason"),
            ip_address=client_ip(),
        )
        db.session.add(entry)
        db.session.commit()
        return {
            "msg": f"El email {email} fue agregado a la lista negra global",
            "data": output_schema.dump(entry),
        }, 201


class BlacklistCheckResource(Resource):
    @jwt_required()
    def get(self, email):
        entry = Blacklist.query.filter_by(email=email.strip().lower()).first()
        if entry is None:
            return {"email": email, "is_blacklisted": False, "blocked_reason": None}, 200
        return {"email": entry.email, "is_blacklisted": True,
                "blocked_reason": entry.blocked_reason}, 200


class HealthResource(Resource):
    def get(self):
        return {"status": "ok", "version": APP_VERSION}, 200


api.add_resource(BlacklistResource, "/blacklists")
api.add_resource(BlacklistCheckResource, "/blacklists/<string:email>")
api.add_resource(HealthResource, "/ping", "/")

with application.app_context():
    try:
        db.create_all()
    except Exception as exc:  # varias instancias arrancando a la vez
        print(f"create_all: {exc}")


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
