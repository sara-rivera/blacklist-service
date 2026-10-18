"""
Genera el Bearer token estático del servicio (sin expiración).
Se firma con la variable de entorno JWT_SECRET_KEY configurada en el ambiente.
"""
from flask_jwt_extended import create_access_token

from application import application

if __name__ == "__main__":
    with application.app_context():
        print(create_access_token(identity="blacklist-client", expires_delta=False))
