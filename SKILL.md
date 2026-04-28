# SKILL.md — Contexto para Agente IA

Este archivo está diseñado para ser inyectado como contexto en un agente de IA.
Al leerlo, la IA puede operar sobre el proyecto sin necesidad de leer el código fuente.

---

## 1. Descripción del Sistema

**Prosperas Reports** es una plataforma SaaS de reportes asincrónicos.

- El usuario solicita un reporte vía formulario web → el sistema responde **inmediatamente** con `{ job_id, status: "PENDING" }`.
- Un worker en background toma el trabajo de una cola SQS y lo procesa (simula 5-30s de trabajo).
- El estado evoluciona: `PENDING → PROCESSING → COMPLETED / FAILED`.
- El frontend hace polling cada 3s y actualiza los badges de color automáticamente.

**Stack:** Python 3.11 / FastAPI · AWS SQS + DLQ · AWS RDS PostgreSQL · AWS S3 · React 18 + Vite · Docker Compose / LocalStack (local) · ECS Fargate (producción) · GitHub Actions (CI/CD).

---

## 2. Mapa del Repositorio

```
prosperas-challenge/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies.py     # inyección de usuario autenticado
│   │   │   └── routes/
│   │   │       ├── auth.py         # POST /auth/register, POST /auth/login
│   │   │       └── jobs.py         # POST /jobs, GET /jobs, GET /jobs/{id}
│   │   ├── core/
│   │   │   ├── auth.py             # JWT encode/decode + bcrypt
│   │   │   ├── config.py           # Settings desde .env (pydantic-settings)
│   │   │   ├── db.py               # SQLAlchemy async engine + sesión
│   │   │   └── errors.py           # Handlers globales de error
│   │   ├── models/
│   │   │   ├── job.py              # SQLAlchemy Job + enum JobStatus
│   │   │   └── user.py             # SQLAlchemy User
│   │   ├── services/
│   │   │   ├── job_service.py      # CRUD de jobs (create, get, list, update)
│   │   │   ├── sqs_service.py      # publish / receive / delete mensajes SQS
│   │   │   └── s3_service.py       # upload de reportes JSON a S3
│   │   ├── worker/
│   │   │   ├── consumer.py         # polling SQS + asyncio.gather (concurrencia)
│   │   │   ├── processor.py        # procesa un job: PROCESSING → COMPLETED/FAILED
│   │   │   └── main.py             # entry point: asyncio.run(poll_and_process())
│   │   └── main.py                 # FastAPI app: routers + middleware + lifespan
│   ├── tests/
│   │   ├── unit/                   # tests de lógica aislada
│   │   └── integration/            # tests de endpoints y worker
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/             # JobForm, JobList, JobBadge
│       ├── hooks/                  # useJobs (polling), useAuth
│       └── services/               # api.js (axios hacia FastAPI)
├── local/
│   ├── init-aws.sh                 # crea SQS, DLQ y S3 en LocalStack
│   └── wait-for-it.sh              # espera host:port antes de continuar
├── infra/                          # IaC producción AWS (Terraform / CDK)
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD: tests → build → ECR → ECS → S3
├── docs/
│   └── AI_WORKFLOW.md              # evidencia de uso de IA
├── docker-compose.yml              # orquesta: postgres + localstack + backend + worker + frontend
├── .env.example                    # plantilla de variables de entorno
├── TECHNICAL_DOCS.md               # documentación técnica completa
├── SKILL.md                        # este archivo
└── README.md                       # badge CI + URL producción + setup rápido
```

---

## 3. Patrones del Proyecto

### Cómo agregar una nueva ruta al backend

1. Crear o editar un archivo en `backend/app/api/routes/`.
2. Definir el router con `APIRouter(prefix="/ruta", tags=["tag"])`.
3. Usar `Depends(get_current_user)` para proteger con JWT.
4. Usar `Depends(get_db)` para obtener la sesión de base de datos.
5. Registrar el router en `backend/app/main.py` con `app.include_router(...)`.

```python
# Ejemplo mínimo
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/nuevo", tags=["nuevo"])

@router.get("")
async def mi_endpoint(current_user = Depends(get_current_user)):
    return {"user": current_user.username}
```

### Cómo publicar un mensaje a SQS

```python
from app.services.sqs_service import publish_job

await publish_job(job_id="uuid-del-job")
# Publica {"job_id": "uuid-del-job"} a la cola SQS configurada en SQS_QUEUE_URL
```

### Cómo leer el estado de un job

```python
from app.services.job_service import get_job_by_id

job = await get_job_by_id(db, job_id="uuid", user_id="uuid-del-usuario")
# Retorna None si no existe o no pertenece al usuario
# job.status → "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED"
# job.result_url → URL de S3 con el reporte (solo si COMPLETED)
```

### Cómo actualizar el estado de un job

```python
from app.services.job_service import update_job_status
from app.models.job import JobStatus

await update_job_status(db, job_id="uuid", status=JobStatus.COMPLETED, result_url="https://...")
```

### Cómo agrega un nuevo tipo de reporte

Ver sección 6 de este documento.

---

## 4. Comandos Frecuentes

```bash
# Levantar todo el entorno local desde cero
docker compose up --build

# Solo el backend en modo desarrollo (sin Docker)
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env  # editar variables
uvicorn app.main:app --reload

# Solo el worker
cd backend
python -m app.worker.main

# Frontend en desarrollo
cd frontend
npm install
npm run dev

# Correr tests
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html

# Ver logs en vivo (Docker)
docker compose logs -f worker
docker compose logs -f backend

# Inspeccionar cola SQS (local)
aws --endpoint-url=http://localhost:4566 sqs get-queue-attributes \
  --queue-url http://localhost:4566/000000000000/prosperas-jobs \
  --attribute-names All

# Ver mensajes en DLQ (local)
aws --endpoint-url=http://localhost:4566 sqs receive-message \
  --queue-url http://localhost:4566/000000000000/prosperas-jobs-dlq

# Limpiar Docker completamente
docker compose down -v
```

---

## 5. Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `pydantic_settings.env_file not found` | No existe el `.env` | `cp .env.example .env` |
| `Connection refused` al backend | El contenedor aún no arrancó | Esperar healthcheck: `docker compose ps` |
| `NoCredentialsError` en worker | AWS_ACCESS_KEY_ID no definido | Verificar `.env` y que `docker compose` lo carga |
| `QueueDoesNotExist` en SQS | `init-aws.sh` no corrió | `docker compose run init-aws` manualmente |
| `asyncpg.InvalidPasswordError` | DATABASE_URL incorrecta | Verificar usuario/pass de Postgres en `.env` |
| `401 Unauthorized` en endpoints | Token expirado o inválido | Hacer login de nuevo: `POST /auth/login` |
| `404 Not Found` en job | Job pertenece a otro usuario | La API filtra por `user_id` del token JWT |
| Worker no procesa mensajes | SQS_WAIT_SECONDS muy alto y sin mensajes | Normal — long polling. Crear un job desde el frontend |

---

## 6. Cómo Extender: Agregar un Nuevo Tipo de Reporte

Para agregar un nuevo `report_type` (ej: `"revenue_by_country"`):

**Paso 1 — backend/app/worker/processor.py**

Editar `_generate_dummy_report` para manejar el nuevo tipo:

```python
def _generate_dummy_report(job_id: str, report_type: str) -> dict:
    base = {"job_id": job_id, "report_type": report_type, "generated_at": ...}

    if report_type == "revenue_by_country":
        base["data"] = [
            {"country": "Colombia", "revenue": 150000},
            {"country": "Mexico", "revenue": 320000},
        ]
    else:
        base["summary"] = {"total_revenue": ..., "total_users": ...}

    return base
```

**Paso 2 — frontend**

Agregar el nuevo tipo al selector del formulario en `src/components/JobForm.jsx`:

```jsx
<option value="revenue_by_country">Revenue por país</option>
```

**Paso 3 — (opcional) validación en backend**

Si se quiere validar que solo se acepten tipos conocidos, agregar un `Enum` en `backend/app/api/routes/jobs.py`:

```python
from enum import Enum

class ReportType(str, Enum):
    sales_summary = "sales_summary"
    revenue_by_country = "revenue_by_country"
    user_activity = "user_activity"

class CreateJobRequest(BaseModel):
    report_type: ReportType  # validación automática con Pydantic
    date_range: str
    format: str
```

No se requiere migración de base de datos — `report_type` es `String` libre en el modelo.
