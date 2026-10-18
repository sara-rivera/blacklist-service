# Blacklist Service – Lista negra global de emails

Microservicio en **Flask** desplegado en **AWS Elastic Beanstalk** con **PostgreSQL en RDS**.

## Endpoints

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| POST | `/blacklists` | Bearer | Agrega un email (`email`, `app_uuid`, `blocked_reason` opcional ≤ 255). Guarda IP y fecha/hora. |
| GET | `/blacklists/<email>` | Bearer | Indica si el email está en la lista negra y el motivo. |
| GET | `/ping` | — | Health check. Devuelve la versión desplegada. |

## Correr en local

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python application.py             # usa SQLite local si no hay variables de RDS
```

## Generar el token estático

```bash
JWT_SECRET_KEY="la-misma-clave-que-pongas-en-beanstalk" python generate_token.py
```
En Windows PowerShell: `$env:JWT_SECRET_KEY="..."; python generate_token.py`

Ese token va en la variable `token` del environment de Postman.

## Variables de entorno en Beanstalk

| Variable | Ejemplo |
|---|---|
| `RDS_HOSTNAME` | `blacklist-db.xxxx.us-east-1.rds.amazonaws.com` |
| `RDS_PORT` | `5432` |
| `RDS_DB_NAME` | `blacklistdb` |
| `RDS_USERNAME` | `postgres` |
| `RDS_PASSWORD` | `********` |
| `JWT_SECRET_KEY` | una clave de 32+ caracteres |

(O una sola variable `DATABASE_URL=postgresql://usuario:clave@host:5432/blacklistdb`.)

## Crear el .zip para Beanstalk

Los archivos deben quedar en la **raíz** del zip (no dentro de una carpeta):

```bash
zip -r deploy-v1.0.zip application.py requirements.txt Procfile .ebextensions
```
En Windows: selecciona `application.py`, `requirements.txt`, `Procfile` y `.ebextensions` → clic derecho → Comprimir.

## Validar despliegues

Cambia `APP_VERSION` en `application.py` antes de cada despliegue y ejecuta:

```bash
./monitor_deploy.sh http://TU-AMBIENTE.elasticbeanstalk.com      # Mac/Linux
.\monitor_deploy.ps1 -Url http://TU-AMBIENTE.elasticbeanstalk.com # Windows
```

## Postman

Importa `postman/Blacklist_API.postman_collection.json` y `postman/Blacklist_AWS.postman_environment.json`.
La colección trae 9 escenarios con tests y ejemplos de respuesta.
