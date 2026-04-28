# TECHNICAL_DOCS.md

Documentación técnica del sistema de reportes asincrónicos — Prosperas Challenge.

---

## 1. Diagrama de Arquitectura

```
┌────────────────────────────────────────────────────────────────────────┐
│                        USUARIO (Browser)                               │
│              React 18 + Vite + TypeScript + TailwindCSS                │
│         Polling cada 3s (React Query) — iOS glass morphism UI          │
└──────────────────────────────┬─────────────────────────────────────────┘
                               │ HTTPS
                               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    AWS CloudFront (d2v3qmq1azg45r.cloudfront.net)        │
│                                                                          │
│  /* (default)  → S3 prosperas-frontend (React SPA, static)              │
│  /auth/*       → EC2:8000 (FastAPI, no-cache)                           │
│  /jobs*        → EC2:8000 (FastAPI, no-cache)                           │
│  /health       → EC2:8000 (FastAPI)                                      │
└────────────────┬─────────────────────────────────────────────────────────┘
                 │ proxy HTTP → EC2
                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│              FastAPI Backend — EC2 t3.micro (Python 3.11)                │
│                  Hexagonal Architecture (Ports & Adapters)               │
│                                                                          │
│  POST /auth/register   POST /auth/login                                  │
│  POST /jobs            GET /jobs           GET /jobs/{id}                │
│                                                                          │
│  JWT HS256 · Pydantic v2 · X-Request-ID traceability                   │
│  Centralized error handlers · RequestContextMiddleware                   │
└────────────┬──────────────────────────────────────────┬──────────────────┘
             │ SQLAlchemy async                          │ aioboto3
             ▼                                          ▼
┌──────────────────────────┐          ┌──────────────────────────────────────┐
│   AWS RDS PostgreSQL 15  │          │           AWS SQS                    │
│   (db.t3.micro)          │          │   prosperas-jobs (main)              │
│                          │          │   prosperas-jobs-dlq (DLQ)           │
│   Table: jobs            │          │   maxReceiveCount: 3                 │
│   Table: users           │          └──────────────────┬───────────────────┘
│   Index: user_id         │                             │ polling asyncio
└──────────┬───────────────┘                             ▼
           │ updates status            ┌─────────────────────────────────────┐
           └───────────────────────────┤     Worker (Python asyncio)         │
                                       │                                     │
                                       │  asyncio.gather(*tasks)             │
                                       │  Semaphore(WORKER_CONCURRENCY=4)   │
                                       │  ≥2 jobs procesándose en paralelo  │
                                       │                                     │
                                       │  PENDING → PROCESSING               │
                                       │         → COMPLETED / FAILED        │
                                       │  Exception → no delete_message      │
                                       │  → SQS retry × 3 → DLQ             │
                                       └──────────────┬──────────────────────┘
                                                      │ upload resultado
                                                      ▼
                                       ┌──────────────────────────────────────┐
                                       │            AWS S3                    │
                                       │  prosperas-reports                   │
                                       │  reports/{job_id}.json               │
                                       └──────────────────────────────────────┘
```

---

## 2. Servicios AWS

| Servicio | Para qué | Por qué |
|----------|----------|---------|
| **CloudFront** | CDN + HTTPS para frontend + proxy API | HTTPS gratuito vía ACM, CDN global, un solo dominio elimina CORS y mixed-content |
| **S3 prosperas-frontend** | Hosting estático del build de React | Sin servidor que gestionar, costo mínimo, integra nativamente con CloudFront |
| **SQS Standard Queue** | Cola principal backend→worker | Free tier generoso, DLQ nativa, at-least-once delivery |
| **SQS Dead Letter Queue** | Mensajes fallidos (>3 reintentos) | Evita bloqueo de cola, permite inspección manual |
| **RDS PostgreSQL 15** | Persistencia de jobs y usuarios | SQL estructurado, LIMIT/OFFSET con índices, free tier t3.micro |
| **S3 prosperas-reports** | Almacenar resultados de reportes | Escalable, URLs directas para result_url |
| **EC2 t3.micro** | Backend FastAPI + Worker | Free tier 750h/mes, sin gestión de K8s, docker compose simple |
| **ECR prosperas-app** | Imagen Docker única (backend + worker) | Integración nativa con GitHub Actions, una sola imagen para dos servicios |
| **CloudWatch** | Logs del backend y worker | Nativo, sin costo adicional en free tier |

---

## 3. Decisiones de Diseño

### Hexagonal Architecture (Ports & Adapters)
Separa el dominio del negocio de la infraestructura. Los use cases no conocen FastAPI, SQLAlchemy ni AWS. Los puertos son Python `Protocol` (PEP 544, structural typing).

- **domain/**: entidades puras (`Job`, `User`, `JobStatus`) y contratos (`IJobRepository`, `IMessageQueue`, `IFileStorage`)
- **use_cases/**: `CreateJobUseCase`, `ProcessJobUseCase`, `RegisterUseCase`, etc. — solo orquestan dominio + puertos
- **adapters/inbound/**: FastAPI routes + schemas Pydantic
- **adapters/outbound/**: `SqlJobRepository`, `SqsMessageQueue`, `S3FileStorage`

### CloudFront como proxy unificado (un solo dominio)
En lugar de dos URLs (frontend en S3 y API en EC2), una sola distribución CloudFront maneja ambas con path routing. Esto elimina problemas de CORS y mixed-content sin configuración adicional.

### SQS vs SNS vs EventBridge
SQS gana: patrón worker-queue directo, DLQ nativa, visibilidad configurable. SNS es pub/sub (múltiples consumidores). EventBridge agrega complejidad innecesaria.

### EC2 t3.micro vs ECS Fargate
EC2 gana en esta escala: **100% free tier**, Docker Compose simple, deploy por SSH. ECS Fargate cobra por vCPU/hora (~$0.50/día, excede los $10 del reembolso).

### asyncio.gather + Semaphore para concurrencia
`asyncio.gather(*tasks)` procesa múltiples mensajes en paralelo en el mismo event loop. `Semaphore(WORKER_CONCURRENCY)` limita el máximo de jobs simultáneos sin bloquear el loop.

### Una sola imagen Docker (backend + worker)
Backend (`uvicorn app.main:app`) y worker (`python -m app.worker.main`) comparten el mismo código. El worker solo sobreescribe el CMD. Una imagen = un build en CI, menos espacio en ECR.

---

## 4. Setup Local (LocalStack)

### Prerequisitos
- Docker Desktop (o Colima) instalado y corriendo
- Git

### Pasos exactos

```bash
# 1. Clonar
git clone https://github.com/cdtello/prosperas-challenge.git
cd prosperas-challenge

# 2. Crear .env local
cp .env.example .env

# 3. Levantar todo
docker compose up --build
```

El orden de arranque es automático:
```
LocalStack → init-aws (SQS + S3) → Postgres → Backend → Worker → Frontend
```

### Verificar
```bash
curl http://localhost:8000/health         # → {"status":"ok"}
open http://localhost:3000                 # React app
open http://localhost:8000/docs            # Swagger UI
```

### Comandos útiles
```bash
docker compose logs -f worker              # logs del worker
docker compose logs -f backend             # logs del backend
docker compose down -v                     # limpieza total
```

---

## 5. Guía de Despliegue (CI/CD)

El pipeline en `.github/workflows/deploy.yml` se dispara en cada push a `main`:

```
Push → main
  ├── test (paralelo)
  │     ├── ruff check app/           (linter, 0 violations)
  │     └── pytest --cov-fail-under=90 (95.38% coverage)
  │
  ├── build-and-deploy-backend (necesita: test)
  │     ├── docker build → push ECR prosperas-app:latest
  │     └── SSH → EC2: docker compose pull + up + /health check
  │
  ├── build-and-deploy-frontend (necesita: test)
  │     ├── npm install + npm run build (VITE_API_URL=CloudFront URL)
  │     ├── aws s3 sync dist/ → s3://prosperas-frontend
  │     └── cloudfront create-invalidation /*
  │
  └── smoke-test (necesita: backend + frontend)
        ├── curl backend /health
        └── curl CloudFront URL
```

**Secrets en GitHub:**
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `EC2_HOST`, `EC2_SSH_KEY`, `CLOUDFRONT_DIST_ID`

---

## 6. Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave para firmar JWT — aleatoria y larga | `openssl rand -hex 32` |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token | `30` |
| `DATABASE_URL` | Cadena SQLAlchemy a PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `AWS_ACCESS_KEY_ID` | ID de llave AWS | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | Llave secreta AWS | `...` |
| `AWS_DEFAULT_REGION` | Región AWS | `us-east-1` |
| `AWS_ENDPOINT_URL` | Solo local: URL LocalStack. Omitir en producción | `http://localstack:4566` |
| `SQS_QUEUE_URL` | URL completa de la cola SQS principal | `https://sqs...amazonaws.com/.../prosperas-jobs` |
| `SQS_DLQ_URL` | URL completa de la Dead Letter Queue | `https://sqs...amazonaws.com/.../prosperas-jobs-dlq` |
| `S3_BUCKET_NAME` | Bucket S3 para reportes | `prosperas-reports` |
| `WORKER_CONCURRENCY` | Máximo de jobs procesándose en paralelo | `4` |
| `SQS_VISIBILITY_TIMEOUT` | Segundos que SQS oculta el mensaje mientras se procesa | `120` |
| `SQS_MAX_MESSAGES` | Máximo mensajes por llamada ReceiveMessage | `10` |
| `SQS_WAIT_SECONDS` | Long polling: segundos que SQS espera | `20` |

---

## 7. Tests

```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Correr todos los tests
pytest tests/ -v

# Con cobertura (95.38% — fail_under=90)
pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=90

# Solo tests unitarios
pytest tests/unit/ -v

# Solo tests de integración (usa SQLite in-memory)
pytest tests/integration/ -v

# Linter
ruff check app/
```

### Qué cubre cada suite

| Suite | Archivos | Qué prueba |
|-------|----------|-----------|
| `unit/use_cases/` | 5 archivos | Use cases con AsyncMock de puertos — sin DB ni AWS |
| `unit/adapters/` | 2 archivos | Repositories (SQLite in-memory) + AWS adapters (aioboto3 mock) |
| `unit/test_consumer.py` | 1 archivo | Worker consumer con mocks |
| `unit/test_error_handlers.py` | 1 archivo | Middleware X-Request-ID + error handlers |
| `unit/test_infrastructure.py` | 1 archivo | auth decode, aws client_kwargs, validation 422 |
| `integration/` | 2 archivos | HTTP endpoints completos (FastAPI TestClient + SQLite) |
