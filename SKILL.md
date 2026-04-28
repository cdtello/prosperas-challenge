# SKILL.md — Contexto para Agente IA

Este archivo está diseñado para ser inyectado como contexto en un agente de IA.
Al leerlo, la IA puede operar sobre el proyecto sin leer el código fuente.

---

## 1. Descripción del Sistema

**Prosperas Reports** es una plataforma SaaS de generación de reportes asincrónicos.

- Usuario llena formulario → API responde **inmediatamente** con `{job_id, status: "PENDING"}`
- El job se encola en **AWS SQS** — el usuario NO espera
- Un **worker Python asyncio** consume la cola y procesa ≥2 jobs en paralelo
- Estado evoluciona: `PENDING → PROCESSING → COMPLETED / FAILED`
- **Frontend React 18** hace polling cada 3s con React Query — badges actualizan automáticamente
- Resultado del reporte se guarda en **AWS S3** como JSON

**Stack:** Python 3.11 / FastAPI · Hexagonal Architecture · AWS SQS + DLQ · AWS RDS PostgreSQL 15 · AWS S3 · AWS CloudFront · React 18 + Vite + TypeScript · Docker Compose / LocalStack · EC2 t3.micro · GitHub Actions CI/CD

**URLs de producción:**
- Frontend: `https://d2v3qmq1azg45r.cloudfront.net`
- API docs: `http://34.229.46.113:8000/docs`

---

## 2. Mapa del Repositorio

```
prosperas-challenge/
├── backend/
│   ├── app/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── job.py          # Dataclass Job (puro Python, sin ORM)
│   │   │   │   └── user.py         # Dataclass User
│   │   │   ├── value_objects/
│   │   │   │   └── job_status.py   # Enum PENDING/PROCESSING/COMPLETED/FAILED
│   │   │   └── ports/
│   │   │       ├── job_repository.py   # Protocol IJobRepository
│   │   │       ├── user_repository.py  # Protocol IUserRepository
│   │   │       ├── message_queue.py    # Protocol IMessageQueue
│   │   │       └── file_storage.py     # Protocol IFileStorage
│   │   ├── use_cases/
│   │   │   ├── create_job.py       # Crea job en DB + publica a SQS
│   │   │   ├── get_job.py          # Obtiene job por ID (filtra por user_id)
│   │   │   ├── list_jobs.py        # Lista paginada de jobs del usuario
│   │   │   ├── process_job.py      # Worker: PROCESSING → sleep → COMPLETED/FAILED
│   │   │   └── authenticate.py     # RegisterUseCase + LoginUseCase
│   │   ├── adapters/
│   │   │   ├── inbound/http/
│   │   │   │   ├── routes/
│   │   │   │   │   ├── auth.py     # POST /auth/register, POST /auth/login
│   │   │   │   │   └── jobs.py     # POST /jobs, GET /jobs, GET /jobs/{id}
│   │   │   │   ├── dependencies.py # get_current_user_id, get_job_repository, etc.
│   │   │   │   └── schemas.py      # Pydantic schemas I/O (separados del dominio)
│   │   │   └── outbound/
│   │   │       ├── persistence/
│   │   │       │   ├── models.py           # SQLAlchemy ORM: JobModel, UserModel
│   │   │       │   ├── sql_job_repository.py  # Implementa IJobRepository
│   │   │       │   └── sql_user_repository.py # Implementa IUserRepository
│   │   │       ├── queue/
│   │   │       │   └── sqs_queue.py        # Implementa IMessageQueue (aioboto3)
│   │   │       └── storage/
│   │   │           └── s3_storage.py       # Implementa IFileStorage (aioboto3)
│   │   ├── infrastructure/
│   │   │   ├── config.py           # Settings pydantic-settings (lee .env)
│   │   │   ├── db.py               # SQLAlchemy async engine + sesión
│   │   │   ├── auth.py             # JWT encode/decode + bcrypt
│   │   │   ├── aws.py              # Cliente aioboto3 compartido
│   │   │   ├── errors.py           # Exception handlers globales + logging traceback
│   │   │   └── middleware.py       # RequestContextMiddleware (X-Request-ID)
│   │   ├── worker/
│   │   │   ├── consumer.py         # Polling SQS + asyncio.gather + Semaphore
│   │   │   └── main.py             # Entry point: asyncio.run(poll_and_process())
│   │   └── main.py                 # FastAPI app + lifespan + routers
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── use_cases/          # 5 archivos: test de cada use case con AsyncMock
│   │   │   ├── adapters/           # test_sql_repositories.py, test_aws_adapters.py
│   │   │   ├── test_consumer.py    # tests del worker consumer
│   │   │   ├── test_error_handlers.py
│   │   │   └── test_infrastructure.py
│   │   └── integration/
│   │       ├── conftest.py         # SQLite in-memory + override get_db
│   │       ├── test_auth_endpoints.py
│   │       └── test_jobs_endpoints.py
│   ├── Dockerfile                  # python:3.11-slim, expone 8000
│   ├── requirements.txt
│   └── pyproject.toml              # ruff config + pytest config (fail_under=90)
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── App.tsx             # Router, QueryClient, AuthProvider, Toaster
│       │   └── index.css           # Tailwind + glass morphism CSS classes
│       ├── features/
│       │   ├── auth/
│       │   │   ├── api/authApi.ts      # POST /auth/register, POST /auth/login
│       │   │   ├── model/authContext.tsx # AuthProvider + useAuthContext
│       │   │   ├── model/useAuth.ts     # login(), register(), logout()
│       │   │   ├── ui/LoginPage.tsx
│       │   │   └── ui/RegisterPage.tsx
│       │   └── jobs/
│       │       ├── api/jobsApi.ts       # create, getById, list
│       │       ├── model/useJobs.ts     # useJobs (polling 3s), useCreateJob
│       │       ├── ui/JobsPage.tsx      # Dashboard principal
│       │       ├── ui/JobCard.tsx       # Tarjeta individual con animación
│       │       ├── ui/JobBadge.tsx      # Badge por estado (4 colores + glow)
│       │       ├── ui/CreateJobForm.tsx # Formulario: report_type, date_range, format
│       │       └── ui/StatsBar.tsx      # Contadores por estado
│       └── shared/
│           ├── ui/                 # Button, Card, Input, Select, Spinner, Navbar, Layout
│           ├── lib/axios.ts        # Axios con interceptor JWT + auto-logout en 401
│           └── types/index.ts      # Job, PaginatedJobs, TokenResponse, CreateJobPayload
├── local/
│   ├── init-aws.sh                 # Crea SQS + DLQ + S3 en LocalStack
│   └── wait-for-it.sh
├── infra/
│   └── aws-resources.md            # Referencia de recursos AWS reales creados
├── docs/
│   └── AI_WORKFLOW.md              # Evidencia de uso de IA
├── .github/
│   └── workflows/deploy.yml        # CI/CD: test → backend EC2 + frontend S3/CF → smoke
├── docker-compose.yml              # postgres + localstack + init-aws + backend + worker + frontend
├── .env.example                    # Plantilla variables de entorno (sin valores reales)
├── TECHNICAL_DOCS.md               # Documentación técnica completa (este proyecto)
├── SKILL.md                        # Este archivo
└── README.md                       # Badge CI + URLs producción + setup rápido
```

---

## 3. Patrones del Proyecto

### Cómo agregar una nueva ruta al backend

1. Crear/editar router en `backend/app/adapters/inbound/http/routes/`
2. Definir `router = APIRouter(prefix="/ruta", tags=["tag"])`
3. Proteger con `Depends(get_current_user_id)` para JWT
4. Usar `Depends(get_job_repository)` para obtener el repositorio
5. Registrar en `backend/app/main.py` con `app.include_router(...)`

```python
# Ejemplo mínimo
from fastapi import APIRouter, Depends
from app.adapters.inbound.http.dependencies import get_current_user_id

router = APIRouter(prefix="/nuevo", tags=["nuevo"])

@router.get("")
async def mi_endpoint(user_id: str = Depends(get_current_user_id)):
    return {"user_id": user_id}
```

### Cómo publicar un mensaje a SQS

```python
from app.adapters.outbound.queue.sqs_queue import SqsMessageQueue

queue = SqsMessageQueue()
await queue.publish("uuid-del-job")
# Publica {"job_id": "uuid-del-job"} a SQS_QUEUE_URL
```

### Cómo leer el estado de un job

```python
from app.use_cases.get_job import GetJobUseCase

use_case = GetJobUseCase(job_repo)
job = await use_case.execute(job_id="uuid", user_id="user-uuid")
# job es None si no existe o no pertenece al usuario
# job.status → JobStatus.PENDING | PROCESSING | COMPLETED | FAILED
# job.result_url → URL S3 si COMPLETED, None si no
```

### Cómo actualizar el estado de un job

```python
from app.domain.value_objects.job_status import JobStatus

updated = await job_repo.update_status(job_id, JobStatus.COMPLETED, result_url="https://...")
```

---

## 4. Comandos Frecuentes

```bash
# Levantar entorno local completo desde cero
docker compose up --build

# Backend en desarrollo (sin Docker)
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env  # editar variables
uvicorn app.main:app --reload

# Worker en desarrollo
cd backend
python -m app.worker.main

# Frontend en desarrollo
cd frontend
npm install
npm run dev  # http://localhost:3000

# Tests con cobertura
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=90

# Linter
cd backend
ruff check app/

# Ver logs en vivo (Docker)
docker compose logs -f worker
docker compose logs -f backend

# Deploy manual a producción (trigger pipeline)
git push origin main

# Ver mensajes en DLQ (producción)
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/990151165442/prosperas-jobs-dlq

# Invalidar caché CloudFront manualmente
aws cloudfront create-invalidation \
  --distribution-id E1XFRPD5RHC3NR \
  --paths "/*"

# Limpiar Docker completamente
docker compose down -v
```

---

## 5. Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `pydantic_settings ValidationError` | `.env` no existe | `cp .env.example .env` |
| `Connection refused` al backend | Contenedor no listo aún | Esperar healthcheck: `docker compose ps` |
| `NoCredentialsError` en worker | `AWS_ACCESS_KEY_ID` no definido | Verificar `.env` y que docker compose lo carga |
| `QueueDoesNotExist` en SQS local | `init-aws` no corrió | `docker compose run init-aws` |
| `asyncpg.InvalidPasswordError` | `DATABASE_URL` incorrecta | Verificar user/pass de Postgres en `.env` |
| `401 Unauthorized` en endpoints | Token expirado o inválido | Hacer login de nuevo: `POST /auth/login` |
| `404 Not Found` en job | Job de otro usuario | La API filtra por `user_id` del token JWT |
| Frontend CORS error | `VITE_API_URL` incorrecto | En producción debe apuntar a CloudFront URL |
| Worker no procesa | SQS vacío o Semaphore lleno | Normal — crear un job desde el frontend |

---

## 6. Cómo Extender: Agregar Nuevo Tipo de Reporte

**Paso 1** — `backend/app/use_cases/process_job.py`

Editar `_generate_dummy_report` para manejar el nuevo tipo:

```python
def _generate_dummy_report(job_id: str, report_type: str) -> dict:
    base = {"job_id": job_id, "report_type": report_type, "generated_at": ...}

    if report_type == "revenue_by_country":
        base["data"] = [
            {"country": "Colombia", "revenue": 150000},
            {"country": "Mexico", "revenue": 320000},
        ]
    else:  # fallback genérico
        base["summary"] = {"total_revenue": ..., "total_users": ...}

    return base
```

**Paso 2** — `frontend/src/features/jobs/ui/CreateJobForm.tsx`

Agregar al array `REPORT_TYPES`:

```tsx
const REPORT_TYPES = [
  // ... existentes ...
  { value: "revenue_by_country", label: "Revenue by Country" },
]
```

**Paso 3 (opcional)** — Validación en backend

Si quieres validar que solo se acepten tipos conocidos, editar `schemas.py`:

```python
from enum import Enum

class ReportType(str, Enum):
    sales_summary = "sales_summary"
    revenue_by_country = "revenue_by_country"

class CreateJobRequest(BaseModel):
    report_type: ReportType  # Pydantic valida automáticamente
    date_range: str
    format: str
```

No se requiere migración de base de datos — `report_type` es `String` libre.

---

## 7. Cómo Funciona el Worker y Qué Pasa si Falla

### Flujo normal

```
1. SQS contiene mensaje: {"job_id": "uuid"}
2. consumer.py recibe el mensaje (long polling, WaitTimeSeconds=20)
3. asyncio.gather() despacha N mensajes concurrentemente (Semaphore(4))
4. ProcessJobUseCase.execute():
   a. update_status(PROCESSING)
   b. asyncio.sleep(5-30s)  ← simula trabajo
   c. upload_report() → S3
   d. update_status(COMPLETED, result_url)
   e. queue.delete() ← solo si todo salió bien
```

### Qué pasa si falla

```
1. Exception en ProcessJobUseCase
2. update_status(FAILED) en DB
3. NO se llama queue.delete()
4. SQS re-entrega el mensaje cuando expira VisibilityTimeout (120s)
5. Si falla 3 veces → SQS mueve el mensaje a la DLQ automáticamente
6. DLQ: prosperas-jobs-dlq (inspección manual sin bloquear la cola principal)
```
