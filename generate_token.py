"""
Genera el token estático (Bearer) que usarás en Postman.
Ejecuta:  JWT_SECRET_KEY=<la-misma-clave-de-beanstalk> python generate_token.py
El token no expira, así que lo generas una sola vez.
"""
from flask_jwt_extended import create_access_token

from application import application

with application.app_context():
    token = create_access_token(identity="blacklist-client", expires_delta=False)
    print(token)
