"""
Configuración de pruebas.
Se usa SQLite en memoria: las pruebas NO dependen de PostgreSQL/RDS,
así CodeBuild puede ejecutarlas sin levantar un motor de base de datos.
"""
import os
import sys

import pytest

# Las variables se definen ANTES de importar la app.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "clave-solo-para-pruebas-unitarias-de-32-caracteres"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask_jwt_extended import create_access_token  # noqa: E402

from application import application, db  # noqa: E402


@pytest.fixture
def client():
    application.config["TESTING"] = True
    with application.app_context():
        db.drop_all()
        db.create_all()
        yield application.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def headers():
    with application.app_context():
        token = create_access_token(identity="pruebas-ci", expires_delta=False)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def payload():
    return {
        "email": "bloqueado@test.com",
        "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "blocked_reason": "Fraude",
    }
