# Stack Técnico Detallado

## Backend — Python + FastAPI

### Dependencias clave

```
fastapi
uvicorn[standard]
pydantic[v2]
python-jose[cryptography]   # JWT
passlib[bcrypt]             # hashing passwords
boto3                       # AWS SDK
sqlalchemy                  # ORM
alembic                     # migraciones DB
asyncpg / psycopg2          # driver postgres
httpx                       # HTTP client async
pytest / pytest-asyncio     # tests
```

### Estructura interna del backend

```
backend/app/
  api/
    routes/
      jobs.py       # POST /jobs, GET /jobs, GET /jobs/{id}
      auth.py       # POST /auth/login, POST /auth/register
    dependencies.py # Inyección de DB session, usuario autenticado
  core/
    config.py       # Settings con pydantic-settings (lee .env)
    auth.py         # JWT encode/decode
    db.py           # engine, session factory
    errors.py       # handlers globales de error
  models/
    job.py          # SQLAlchemy model + Pydantic schema
    user.py         # SQLAlchemy model + Pydantic schema
  services/
    job_service.py  # lógica de negocio: crear job, actualizar estado
    sqs_service.py  # publicar/consumir mensajes SQS
    s3_service.py   # guardar resultados
  worker/
    main.py         # entry point del worker
    processor.py    # lógica de procesamiento (sleep + dummy data)
    consumer.py     # polling SQS + despacho concurrente
```

### Autenticación JWT

```python
# Flujo básico
POST /auth/login { username, password }
→ { access_token, token_type: "bearer" }

# Header en requests protegidos
Authorization: Bearer <token>

# Decoded payload
{ sub: user_id, exp: timestamp }
```

### Manejo de Errores Centralizado

```python
# core/errors.py — NO try/except dispersos
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

@app.exception_handler(HTTPException)
async def http_error_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
```

---

## Worker — Concurrencia Python

### Opción recomendada: asyncio

```python
# worker/consumer.py
import asyncio
import aioboto3

async def poll_and_process():
    async with session.client("sqs") as sqs:
        while True:
            response = await sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20  # long polling
            )
            messages = response.get("Messages", [])
            if messages:
                tasks = [process_message(sqs, msg) for msg in messages]
                await asyncio.gather(*tasks)  # >=2 en paralelo

asyncio.run(poll_and_process())
```

### Estados del job durante procesamiento

```python
async def process_message(sqs, message):
    job_id = json.loads(message["Body"])["job_id"]
    try:
        await update_job_status(job_id, "PROCESSING")
        await asyncio.sleep(random.randint(5, 30))  # simula trabajo
        result = generate_dummy_report()
        result_url = await upload_to_s3(result)
        await update_job_status(job_id, "COMPLETED", result_url=result_url)
        await sqs.delete_message(...)  # solo se borra si exitoso
    except Exception:
        await update_job_status(job_id, "FAILED")
        # SQS reintenta automáticamente hasta MaxReceiveCount → DLQ
        raise
```

---

## Frontend — React

### Dependencias clave

```
react 18+
react-router-dom v6
axios / fetch
react-query o SWR       # para polling y caché de estado
tailwindcss             # styling responsive
react-hot-toast         # notificaciones (no alert())
```

### Polling del estado de jobs

```javascript
// hooks/useJobs.js — con react-query
import { useQuery } from '@tanstack/react-query';

export function useJobs() {
  return useQuery({
    queryKey: ['jobs'],
    queryFn: () => fetchJobs(),
    refetchInterval: 3000,  // polling cada 3s
    refetchIntervalInBackground: true,
  });
}
```

### Badge de colores por estado

```javascript
const STATUS_STYLES = {
  PENDING:    'bg-yellow-100 text-yellow-800',
  PROCESSING: 'bg-blue-100 text-blue-800 animate-pulse',
  COMPLETED:  'bg-green-100 text-green-800',
  FAILED:     'bg-red-100 text-red-800',
};
```

---

## Variables de Entorno (.env.example)

```env
# App
SECRET_KEY=your-jwt-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/prosperas

# AWS
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_DEFAULT_REGION=us-east-1
AWS_ENDPOINT_URL=http://localhost:4566  # solo en local con LocalStack

# SQS
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123/prosperas-jobs
SQS_DLQ_URL=https://sqs.us-east-1.amazonaws.com/123/prosperas-jobs-dlq

# S3
S3_BUCKET_NAME=prosperas-reports

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Tests — Pytest

```python
# Estructura de tests recomendada
backend/tests/
  unit/
    test_job_service.py      # lógica de negocio
    test_worker_processor.py # simulación de procesamiento
    test_auth.py             # JWT encode/decode
  integration/
    test_jobs_endpoint.py    # POST /jobs, GET /jobs
    test_worker_failure.py   # simula fallo → estado FAILED

# Correr tests
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html  # con cobertura
```

---

## Comandos Frecuentes

```bash
# Local — levantar todo
docker compose up --build

# Solo backend en desarrollo
cd backend && uvicorn app.main:app --reload

# Solo worker
cd backend && python -m app.worker.main

# Tests
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm run dev

# Inicializar AWS local (crear cola SQS, bucket S3)
./local/init-aws.sh

# Ver logs del worker
docker compose logs -f worker

# Deploy manual a producción
gh workflow run deploy.yml
```
