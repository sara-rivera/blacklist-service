# Blacklist Service

Microservicio REST para la gestión de la **lista negra global de emails** de la organización. Permite que los sistemas internos agreguen emails a la lista negra y consulten si un email está bloqueado.

Proyecto 1 · Entrega 1 · Despliegue manual de un microservicio sobre PaaS (AWS Elastic Beanstalk).

## Arquitectura

```
Cliente (Postman)
      │  HTTP + Bearer Token
      ▼
Application Load Balancer  ──  health check GET /ping
      │
      ▼
Auto Scaling Group (mín. 3 · máx. 6 instancias EC2)
Elastic Beanstalk · Python · Gunicorn · Flask
      │
      ▼
Amazon RDS · PostgreSQL
```

## Stack

| Componente | Uso |
|---|---|
| Python 3 + Flask | Framework web |
| Flask-RESTful | Recursos REST |
| Flask-SQLAlchemy | ORM |
| Flask-Marshmallow | Validación y serialización |
| Flask-JWT-Extended | Autorización con Bearer Token |
| Werkzeug | WSGI |
| PostgreSQL (AWS RDS) | Persistencia |
| Gunicorn | Servidor de aplicación |

## API

Todas las rutas de `/blacklists` requieren el encabezado `Authorization: Bearer <token>`.

### POST `/blacklists`

Agrega un email a la lista negra global. El servicio registra internamente la IP de origen y la fecha/hora de la solicitud.

| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `email` | String | Sí | Formato de email válido |
| `app_uuid` | String | Sí | UUID válido |
| `blocked_reason` | String | No | Máximo 255 caracteres |

```json
{
  "email": "cliente@ejemplo.com",
  "app_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "blocked_reason": "Solicitud del cliente"
}
```

| Código | Significado |
|---|---|
| 201 | Email agregado |
| 400 | Datos inválidos |
| 401 | Token faltante o inválido |
| 409 | El email ya está en la lista negra |

### GET `/blacklists/<email>`

Indica si el email está en la lista negra global y el motivo.

```json
{
  "email": "cliente@ejemplo.com",
  "is_blacklisted": true,
  "blocked_reason": "Solicitud del cliente"
}
```

### GET `/ping`

Health check del servicio. No requiere autorización.

```json
{ "status": "ok", "version": "1.0" }
```

## Modelo de datos

Tabla `blacklist`: `id`, `email` (único), `app_uuid`, `blocked_reason`, `ip_address`, `created_at`.

## Estructura del repositorio

```
├── application.py                 Aplicación Flask (entrypoint de Beanstalk)
├── requirements.txt               Dependencias
├── Procfile                       Comando de arranque (Gunicorn)
├── .ebextensions/
│   └── 01-healthcheck.config      Health check, enhanced health y auto scaling
├── generate_token.py              Generación del Bearer token estático
├── monitor_deploy.sh / .ps1       Monitor de /ping durante los despliegues
└── postman/
    ├── Blacklist_API.postman_collection.json
    └── Blacklist_AWS.postman_environment.json
```

## Configuración

Variables de entorno del ambiente de Elastic Beanstalk:

| Variable | Descripción |
|---|---|
| `RDS_HOSTNAME` | Endpoint de la instancia RDS |
| `RDS_PORT` | Puerto (5432) |
| `RDS_DB_NAME` | Nombre de la base (`blacklistdb`) |
| `RDS_USERNAME` | Usuario de la base |
| `RDS_PASSWORD` | Contraseña de la base |
| `JWT_SECRET_KEY` | Clave de firma del token |

## Ejecución local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python application.py
```

Sin variables de RDS, la aplicación usa SQLite local.

## Token de autorización

```bash
JWT_SECRET_KEY="<clave-del-ambiente>" python generate_token.py
```

## Despliegue

Paquete de despliegue con los archivos en la raíz del zip:

```bash
zip -r deploy-v1.0.zip application.py requirements.txt Procfile .ebextensions
```

Estrategias de despliegue evaluadas: All at once, Rolling, Rolling with additional batch e Immutable. Cada versión expone su número en `/ping`, y `monitor_deploy` registra la transición entre versiones durante el despliegue.

## Pruebas

La colección de Postman (`postman/`) contiene 9 escenarios con tests automáticos y ejemplos de respuesta: health check, creación exitosa, duplicado, UUID inválido, motivo mayor a 255 caracteres, solicitud sin token y consultas de emails bloqueados y no bloqueados.
