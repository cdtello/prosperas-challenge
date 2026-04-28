# Arquitectura Propuesta — Decisiones AWS

## Diagrama General

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USUARIO (Browser)                          │
│                        React 18 Frontend                            │
└──────────────────────────┬────────────────────────────────┬─────────┘
                           │ HTTP/REST                      │ Polling / WebSocket (B3)
                           ▼                                ▼
┌──────────────────────────────────────────┐
│              FastAPI Backend             │
│  POST /jobs  GET /jobs  GET /jobs/{id}   │
│         JWT Auth + Pydantic v2           │
└──────┬─────────────────────┬────────────┘
       │ Persiste            │ Publica mensaje
       ▼                     ▼
┌─────────────┐    ┌─────────────────────┐
│  AWS RDS    │    │    AWS SQS          │
│  (Postgres) │    │  cola estándar      │
│  o DynamoDB │    │  + DLQ para fallos  │
└─────────────┘    └──────────┬──────────┘
       ▲                      │ Consume
       │ Actualiza estado      ▼
       │           ┌──────────────────────┐
       └───────────┤   Worker (Python)    │
                   │  asyncio concurrent  │
                   │  >=2 tareas paralelo │
                   │  PENDING→PROCESSING  │
                   │  →COMPLETED/FAILED   │
                   └──────────────────────┘
```

---

## Servicios AWS Recomendados

| Servicio | Para qué | Por qué elegirlo |
|----------|----------|-----------------|
| **SQS (Standard Queue)** | Cola de mensajes asíncrona | Free tier generoso, DLQ nativa, simple de integrar con boto3, at-least-once delivery |
| **RDS (PostgreSQL)** | Persistencia de jobs | SQL estructurado, consultas eficientes por user_id con índices, free tier t3.micro |
| **ECS Fargate** | Correr backend + worker | Sin gestión de servidores, auto-scaling, se integra bien con CI/CD |
| **ECR** | Registro de imágenes Docker | Nativo de AWS, integrado con ECS y GitHub Actions |
| **S3** | Guardar resultados de reportes (result_url) | Barato, escalable, URLs presignadas |
| **ALB** | Load balancer para el backend | HTTPS, health checks, integrado con ECS |
| **CloudWatch** | Logs y métricas (B5) | Nativo, sin costo adicional en free tier básico |

> **Alternativa liviana si se quiere simplicidad máxima:**  
> En vez de ECS Fargate → una sola instancia **EC2 t3.micro** con Docker Compose.  
> Más fácil de configurar, pero menos escalable. Válido para una prueba técnica.

---

## Flujo Completo de un Job

```
1. Usuario llena formulario → POST /jobs
2. API crea job en DB con status=PENDING
3. API publica mensaje a SQS con job_id
4. API responde { job_id, status: "PENDING" } inmediatamente
5. Worker(s) hacen polling a SQS (asyncio / ThreadPoolExecutor)
6. Worker toma mensaje → actualiza DB a PROCESSING
7. Worker simula procesamiento (sleep 5-30s + datos dummy)
8. Si éxito → actualiza DB a COMPLETED, guarda result_url en S3
   Si falla  → actualiza DB a FAILED, SQS reintenta N veces → DLQ
9. Frontend hace polling a GET /jobs o recibe push (B3 WebSocket)
10. UI actualiza badge de color automáticamente
```

---

## Estrategia de Concurrencia del Worker

```python
# Opción A — asyncio (recomendada para Python moderno)
async def process_jobs():
    tasks = [process_single_job(msg) for msg in batch]
    await asyncio.gather(*tasks)

# Opción B — ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(process_job, messages)
```

**Clave:** El worker hace `ReceiveMessage` con `MaxNumberOfMessages=10` y procesa varios en paralelo. La visibilidad del mensaje en SQS se extiende mientras se procesa (`ChangeMessageVisibility`).

---

## Estrategia Anti-Fallos

| Mecanismo | Cómo funciona |
|-----------|---------------|
| **SQS Visibility Timeout** | Si el worker no hace delete del mensaje en X tiempo, SQS lo re-entrega a otro worker |
| **MaxReceiveCount** | Después de N reintentos fallidos → el mensaje va a la **Dead Letter Queue (DLQ)** |
| **DLQ** | Mensajes muertos se guardan para inspección/retry manual sin bloquear la cola principal |
| **DB status=FAILED** | Worker captura excepciones y actualiza el estado correctamente en BD |

---

## Estrategia de Actualización en Frontend

**Opción Core (polling):**
```javascript
// Cada 3 segundos consulta el estado
useEffect(() => {
  const interval = setInterval(() => fetchJobs(), 3000);
  return () => clearInterval(interval);
}, []);
```

**Opción Bonus B3 (WebSocket con FastAPI):**
```python
@app.websocket("/ws/jobs/{user_id}")
async def job_status_ws(websocket: WebSocket, user_id: str):
    # Notifica al cliente cuando el worker actualiza el estado
```

---

## Setup Local con LocalStack

```yaml
# docker-compose.yml
services:
  localstack:
    image: localstack/localstack
    environment:
      - SERVICES=sqs,s3,dynamodb  # o rds si se usa postgres local
    ports:
      - "4566:4566"

  backend:
    build: ./backend
    environment:
      - AWS_ENDPOINT_URL=http://localstack:4566
      - AWS_DEFAULT_REGION=us-east-1
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
    depends_on:
      - localstack

  worker:
    build: ./backend
    command: python -m app.worker.main
    depends_on:
      - localstack

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
```

**Inicialización de LocalStack:**
```bash
# Script de init que crea la cola SQS, bucket S3, tabla en DB
./local/init-aws.sh
```

---

## Pipeline CI/CD Propuesto

```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main]

jobs:
  deploy:
    steps:
      - Checkout código
      - Run tests (pytest)
      - Build Docker images
      - Push a ECR
      - Deploy a ECS Fargate (backend + worker)
      - Deploy frontend (S3 + CloudFront o Amplify)
      - Smoke test de URL pública
```

**Alternativa más simple:** EC2 + SSH deploy via GitHub Actions (menos infraestructura, más fácil de razonar).

---

## Notas de Decisiones Importantes

1. **SQS vs SNS vs EventBridge:** SQS es la opción más directa para worker-queue pattern. SNS es pub/sub (múltiples consumidores), EventBridge es más complejo. SQS gana en simplicidad para este caso.

2. **RDS vs DynamoDB:** RDS/Postgres es mejor para queries relacionales (listar jobs por usuario con paginación). DynamoDB requiere diseño cuidadoso de partition keys. RDS es más familiar.

3. **ECS Fargate vs EC2 vs Lambda:** Lambda tiene cold starts y límite de 15 min — malo para workers largos. EC2 es simple pero manual. ECS Fargate es el punto medio ideal.

4. **Polling vs WebSocket (frontend):** Polling cada 3s es suficiente para el core. WebSocket es el bonus B3 — más elegante pero más complejo de implementar y de mantener conexión abierta.
