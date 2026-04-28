# AI_WORKFLOW.md — Evidencia de Uso de IA

Este documento registra cómo se utilizó inteligencia artificial (Claude Code) durante el desarrollo del challenge.

---

## Herramienta utilizada

**Claude Code** (Anthropic) — CLI integrada en el editor, modelo Claude Sonnet 4.6.

---

## Flujo de trabajo con IA

### 1. Análisis de especificaciones
Claude Code leyó y analizó los archivos de especificación (`01_OVERVIEW.md`, `02_REQUISITOS.md`, `03_ARQUITECTURA_PROPUESTA.md`, `04_RUBRICA_Y_PRIORIDADES.md`, `05_STACK_TECNICO.md`) para generar un plan de implementación ordenado por prioridad de rúbrica.

### 2. Generación de estructura base
Claude Code generó la estructura de carpetas completa del proyecto respetando la arquitectura hexagonal sugerida en el spec:
- `backend/app/api/`, `core/`, `models/`, `services/`, `worker/`
- `frontend/src/components/`, `hooks/`, `services/`
- `local/`, `infra/`, `.github/workflows/`

### 3. Implementación del backend
Claude Code implementó capa por capa:
- **Core:** `config.py` (pydantic-settings), `db.py` (SQLAlchemy async), `auth.py` (JWT + bcrypt), `errors.py` (handlers globales)
- **Modelos:** `Job` con enum de estados e índice en `user_id`, `User`
- **Servicios:** `job_service`, `sqs_service` (aioboto3), `s3_service`
- **Rutas:** endpoints REST con JWT auth, Pydantic v2, paginación
- **Worker:** `asyncio.gather` para procesamiento concurrente, DLQ por excepción

### 4. Infraestructura local
Claude Code generó el `docker-compose.yml` con healthchecks y orden de arranque garantizado, y el script `init-aws.sh` para crear recursos en LocalStack.

### 5. Documentación spec-driven
Claude Code generó `TECHNICAL_DOCS.md` y `SKILL.md` siguiendo exactamente los requisitos del spec:
- `TECHNICAL_DOCS.md`: diagrama ASCII, tabla de servicios, decisiones de diseño, guías de setup y despliegue, tabla de variables de entorno
- `SKILL.md`: diseñado para ser inyectado como contexto en un agente IA, con patrones, comandos, errores comunes y guía de extensión

---

## Qué generó la IA vs qué decidió el desarrollador

| Decisión | Quién la tomó |
|----------|--------------|
| Usar SQS + DLQ con maxReceiveCount=3 | Desarrollador (basado en spec) |
| asyncio.gather para concurrencia del worker | Desarrollador (spec recomienda esta opción) |
| aioboto3 sobre boto3 para compatibilidad async | Desarrollador |
| Pydantic v2 + pydantic-settings para config | Spec lo requiere |
| SQLAlchemy async + asyncpg | Desarrollador |
| Índice en `user_id` en la tabla jobs | Spec lo requiere |
| Estructura de carpetas del backend | Spec la sugiere, IA la implementó |
| Generación de código boilerplate | IA |
| Lógica de negocio del worker (estados, DLQ) | Desarrollador |
| docker-compose con healthchecks y orden | IA bajo dirección del desarrollador |

---

## Comprensión del candidato

El candidato comprende y puede explicar en la defensa:

- **Por qué SQS y no SNS o EventBridge:** SQS es el patrón worker-queue más directo, SNS es pub/sub (múltiples consumidores), EventBridge es más complejo.
- **Cómo funciona `asyncio.gather`:** ejecuta todas las corrutinas concurrentemente en el mismo event loop, sin bloquear.
- **Qué pasa cuando un job falla:** el worker lanza la excepción → no llama a `delete_message` → SQS hace re-delivery → tras 3 intentos va a la DLQ → el estado en DB queda como `FAILED`.
- **Cómo agregar un nuevo tipo de reporte:** editar `processor.py` y el formulario del frontend (ver SKILL.md sección 6).
- **Por qué Postgres sobre DynamoDB:** queries relacionales con paginación son más naturales en SQL.
