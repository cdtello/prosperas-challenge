# TECHNICAL_DOCS.md

Documentación técnica del sistema de reportes asincrónicos — Prosperas Challenge.

---

## 1. Diagrama de Arquitectura

```
┌────────────────────────────────────────────────────────────────────┐
│                        USUARIO (Browser)                           │
│                  React 18 + Vite + TailwindCSS                     │
│           Polling cada 3s → GET /jobs (react-query)                │
└─────────────────────────────┬──────────────────────────────────────┘
                              │ HTTP/REST  (JWT Bearer)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (Python 3.11)                  │
│                                                                     │
│  POST /auth/register   POST /auth/login                             │
│  POST /jobs            GET /jobs           GET /jobs/{id}           │
│                                                                     │
│  JWT auth · Pydantic v2 · Manejo centralizado de errores           │
└──────────────┬──────────────────────────────┬───────────────────────┘
               │ SQLAlchemy async              │ boto3 / aioboto3
               ▼                              ▼
┌──────────────────────┐          ┌───────────────────────────────────┐
│   AWS RDS Postgres   │          │           AWS SQS                 │
│                      │          │   Cola: prosperas-jobs            │
│  Tabla: jobs         │          │   DLQ:  prosperas-jobs-dlq        │
│  Tabla: users        │          │   maxReceiveCount: 3              │
│  Índice: user_id     │          └───────────────┬───────────────────┘
└──────────┬───────────┘                          │ polling asyncio
           │ actualiza estado                     ▼
           │                    ┌─────────────────────────────────────┐
           └────────────────────┤        Worker (Python asyncio)      │
                                │                                     │
                                │  asyncio.gather(*tasks)             │
                                │  ≥2 jobs procesándose en paralelo  │
                                │                                     │
                                │  PENDING → PROCESSING               │
                                │         → COMPLETED / FAILED        │
                                │                                     │
                                │  Si falla: SQS reintenta (×3)      │
                                │  Tras 3 fallos → DLQ               │
                                └──────────────┬──────────────────────┘
                                               │ upload resultado
                                               ▼
                                ┌──────────────────────────────────────┐
                                │            AWS S3                    │
                                │  Bucket: prosperas-reports           │
                                │  Key: reports/{job_id}.json          │
                                └──────────────────────────────────────┘
```

---

## 2. Servicios AWS

| Servicio | Para qué se usa | Por qué se eligió |
|----------|-----------------|-------------------|
| **SQS Standard Queue** | Cola de mensajes asíncrona entre API y workers | Free tier generoso, DLQ nativa, at-least-once delivery, simple con boto3 |
| **SQS Dead Letter Queue** | Captura mensajes que fallaron ≥3 veces | Evita que mensajes problemáticos bloqueen la cola principal |
| **RDS PostgreSQL** | Persistencia de jobs y usuarios | SQL estructurado, queries eficientes con índices, free tier t3.micro, paginación simple |
| **S3** | Almacenar resultados de reportes (result_url) | Escalable, barato, URLs directas, sin gestión de servidores |
| **ECS Fargate** | Correr backend y worker como contenedores | Sin gestión de servidores, integrado con ECR y ALB, auto-scaling |
| **ECR** | Registro de imágenes Docker | Nativo AWS, integrado con GitHub Actions y ECS |
| **ALB** | Load balancer HTTPS para el backend | Health checks automáticos, HTTPS, integrado con ECS |
| **CloudWatch** | Logs del backend y worker | Nativo, sin costo adicional en free tier básico |

---

## 3. Decisiones de Diseño

### SQS vs SNS vs EventBridge
- **SQS** gana: patrón worker-queue directo, un solo consumidor, DLQ nativa, visibilidad configurable.
- SNS es pub/sub (múltiples consumidores) — más de lo necesario.
- EventBridge agrega complejidad innecesaria para este caso.

### RDS Postgres vs DynamoDB
- **RDS/Postgres** gana: queries relacionales con paginación (`LIMIT/OFFSET`), índice en `user_id`, modelo de datos fijo.
- DynamoDB requiere diseño cuidadoso de partition keys para queries por usuario.

### ECS Fargate vs EC2 vs Lambda
- **ECS Fargate** gana: sin gestión de servidores, workers de larga duración (Lambda tiene límite 15 min — inaceptable para jobs de 30s+).
- EC2 es más simple pero requiere gestión manual.

### Concurrencia del worker — asyncio vs ThreadPoolExecutor
- **asyncio** gana: Python moderno, `asyncio.gather` procesa múltiples mensajes SQS en paralelo sin bloqueo, compatible con aioboto3.

### Polling vs WebSocket (frontend)
- **Polling cada 3s** es el core: simple, confiable, sin estado en servidor.
- WebSocket es el bonus B3: más elegante pero más complejo.

### Estrategia anti-fallos
| Mecanismo | Comportamiento |
|-----------|---------------|
| SQS Visibility Timeout | Si el worker no hace `delete_message` en 120s → SQS re-entrega |
| maxReceiveCount = 3 | Después de 3 fallos → mensaje va a DLQ |
| DLQ | Mensajes muertos se guardan para inspección sin bloquear la cola |
| DB status=FAILED | Worker captura excepciones y actualiza estado correctamente |

---

## 4. Setup Local (LocalStack)

### Prerequisitos
- Docker Desktop instalado y corriendo
- Git

### Pasos exactos

```bash
# 1. Clonar el repositorio
git clone https://github.com/cdtello/prosperas-challenge.git
cd prosperas-challenge

# 2. Crear archivo de entorno local (ya tiene valores para LocalStack)
cp .env.example .env

# 3. Levantar todos los servicios
docker compose up --build

# El orden de arranque es automático:
#   LocalStack → init-aws (crea SQS + S3) → Postgres → backend → worker → frontend
```

### Verificar que todo está corriendo
```bash
# API health check
curl http://localhost:8000/health
# → {"status": "ok"}

# Frontend
open http://localhost:3000

# Docs interactivos de la API
open http://localhost:8000/docs
```

### Comandos útiles
```bash
# Ver logs del worker
docker compose logs -f worker

# Ver logs del backend
docker compose logs -f backend

# Ver mensajes en la cola SQS (LocalStack)
aws --endpoint-url=http://localhost:4566 sqs get-queue-attributes \
  --queue-url http://localhost:4566/000000000000/prosperas-jobs \
  --attribute-names All

# Detener y limpiar todo
docker compose down -v
```

---

## 5. Guía de Despliegue (CI/CD)

El pipeline en `.github/workflows/deploy.yml` se dispara automáticamente en cada push a `main`:

```
Push a main
    │
    ▼
Run tests (pytest)
    │
    ▼
Build Docker images (backend + worker + frontend)
    │
    ▼
Push a ECR (Amazon Elastic Container Registry)
    │
    ▼
Deploy backend + worker → ECS Fargate
    │
    ▼
Deploy frontend → S3 + CloudFront
    │
    ▼
Smoke test → GET /health → 200 OK
```

**Secrets necesarios en GitHub:**
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
ECR_REGISTRY
ECR_BACKEND_REPOSITORY
ECR_WORKER_REPOSITORY
ECS_CLUSTER
ECS_BACKEND_SERVICE
ECS_WORKER_SERVICE
DATABASE_URL
SECRET_KEY
SQS_QUEUE_URL
SQS_DLQ_URL
S3_BUCKET_NAME
```

---

## 6. Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta para firmar JWT — debe ser aleatoria y larga | `openssl rand -hex 32` |
| `ALGORITHM` | Algoritmo de firma JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tiempo de expiración del token en minutos | `30` |
| `DATABASE_URL` | Cadena de conexión SQLAlchemy a PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `AWS_ACCESS_KEY_ID` | ID de llave de acceso AWS | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | Llave secreta AWS | `...` |
| `AWS_DEFAULT_REGION` | Región AWS | `us-east-1` |
| `AWS_ENDPOINT_URL` | Solo en local: URL de LocalStack. Omitir en producción | `http://localstack:4566` |
| `SQS_QUEUE_URL` | URL completa de la cola SQS principal | `https://sqs.us-east-1.amazonaws.com/.../prosperas-jobs` |
| `SQS_DLQ_URL` | URL completa de la Dead Letter Queue | `https://sqs.us-east-1.amazonaws.com/.../prosperas-jobs-dlq` |
| `S3_BUCKET_NAME` | Nombre del bucket S3 para reportes | `prosperas-reports` |
| `WORKER_CONCURRENCY` | Número de mensajes procesados en paralelo | `4` |
| `SQS_VISIBILITY_TIMEOUT` | Segundos que SQS oculta el mensaje mientras se procesa | `120` |
| `SQS_MAX_MESSAGES` | Máximo de mensajes por llamada a ReceiveMessage | `10` |
| `SQS_WAIT_SECONDS` | Long polling: segundos que SQS espera si no hay mensajes | `20` |

---

## 7. Correr Tests

```bash
# Instalar dependencias localmente (sin Docker)
cd backend
pip install -r requirements.txt

# Correr todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html

# Solo tests unitarios
pytest tests/unit/ -v

# Solo tests de integración
pytest tests/integration/ -v
```
