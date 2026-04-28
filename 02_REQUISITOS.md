# Requisitos del Sistema — Detalle Completo

## Core Obligatorio

### 3.1 Backend — Python + FastAPI

| Endpoint | Descripción |
|----------|-------------|
| `POST /jobs` | Crea un job → responde `{ job_id, status: 'PENDING' }` inmediatamente |
| `GET /jobs/{job_id}` | Estado actual + resultado si completado |
| `GET /jobs` | Lista jobs del usuario autenticado (paginado, mín. 20 por página) |

**Requisitos técnicos:**
- Autenticación JWT (sin OAuth externo)
- Validación de payloads con **Pydantic v2**
- Manejo centralizado de errores (handlers globales, NO try/except dispersos)
- `Dockerfile` funcional para AWS

---

### 3.2 Cola de Mensajes y Workers — AWS

- Al crear un job → API publica mensaje a **cola AWS** (elección del candidato)
- Worker(s) consumen mensajes y procesan jobs **de forma asíncrona**
- Worker actualiza estado en DB: `PROCESSING → COMPLETED` o `FAILED`
- **Mínimo 2 mensajes procesándose en paralelo** sin bloquearse
- **Estrategia para mensajes fallidos** que no bloqueen la cola (Dead Letter Queue u similar)

---

### 3.3 Persistencia — AWS

**Modelo de datos mínimo:**

| Campo | Tipo |
|-------|------|
| `job_id` | UUID (PK) |
| `user_id` | string (FK) |
| `status` | enum: PENDING / PROCESSING / COMPLETED / FAILED |
| `report_type` | string |
| `created_at` | timestamp |
| `updated_at` | timestamp |
| `result_url` | string (nullable) |

**Requisitos:**
- Servicio de base de datos AWS (elección del candidato)
- Consultas por usuario eficientes (índices en `user_id`)
- Script o instrucción para inicializar el esquema desde cero

---

### 3.4 Frontend — React 18+

**Pantallas / funcionalidades requeridas:**
- **Formulario** para solicitar reporte: campos `report_type`, `date_range`, `format`
- **Lista de jobs** con badge de colores por estado:
  - `PENDING` → amarillo/gris
  - `PROCESSING` → azul/spinner
  - `COMPLETED` → verde
  - `FAILED` → rojo
- **Actualización automática** del estado (sin recargar la página)
- **Manejo de errores** con feedback visual (NO `alert()` nativo)
- **Responsive** — funciona bien en móvil y desktop

---

### 3.5 Infraestructura

**Dos ambientes:**

| Ambiente | Cómo | Detalle |
|----------|------|---------|
| Desarrollo local | LocalStack + Docker Compose | `docker compose up` — sin config adicional |
| Producción | AWS real | URL pública accesible desde internet |

**Reglas de oro:**
- Variables de entorno con `.env.example`
- **NUNCA** hardcodear credenciales o secretos en el repo
- README con instrucciones para ambos ambientes

---

### 3.6 Pipeline CI/CD — OBLIGATORIO

- **GitHub Actions** que hace deploy automático a AWS al hacer push a la rama principal
- La app debe estar **viva en una URL pública real** (no local, no LocalStack)
- README debe mostrar:
  - Badge de GitHub Actions en **verde**
  - URL pública de producción

**Lo que se evalúa:**
- Que el pipeline realmente despliega a AWS
- Decisiones detrás del diseño del pipeline
- Coherencia con el sistema construido

---

### 3.7 Documentación Técnica + AI Skill — OBLIGATORIO

**IMPORTANTE:** Ambos artefactos deben generarse con IA (Claude Code, Cursor, Copilot, etc.)  
Se debe incluir evidencia del uso de IA en README o `AI_WORKFLOW.md`.

#### Artefacto 1 — `TECHNICAL_DOCS.md`

Contenido mínimo:
- Diagrama de arquitectura (ASCII art o Mermaid)
- Tabla de servicios AWS: qué servicio, para qué, por qué se eligió
- Decisiones de diseño: trade-offs y alternativas descartadas
- Guía de setup local (LocalStack, pasos exactos)
- Guía de despliegue (cómo funciona el pipeline)
- Variables de entorno: descripción de cada variable del `.env.example`
- Instrucciones para correr tests

#### Artefacto 2 — `SKILL.md`

Un archivo diseñado para ser **inyectado como contexto en un agente de IA**.  
La IA que lo lea debe operar sobre el proyecto sin leer el código.

Contenido mínimo:
- Descripción del sistema
- Mapa del repositorio
- Patrones del proyecto (cómo agregar ruta, publicar a cola, leer estado de job)
- Comandos frecuentes
- Errores comunes y soluciones
- Cómo extender: agregar un nuevo tipo de reporte

**Test en vivo del SKILL.md en la entrevista:** El evaluador abrirá Claude con el SKILL.md como único contexto y hará preguntas como:
- ¿Cómo funciona el worker? ¿Qué pasa si falla?
- ¿Qué servicio de AWS se usa para la cola y por qué?
- ¿Cómo agrego un nuevo tipo de reporte?
- ¿Cómo levanto el entorno local desde cero?

---

## Bonus Senior (opcionales)

| ID | Reto | Descripción |
|----|------|-------------|
| B1 | Prioridad de mensajes | 2 colas: alta prioridad y estándar. Worker prefiere alta prioridad |
| B2 | Circuit Breaker | Si el worker falla N veces consecutivas → estado 'open', pausa ese tipo |
| B3 | Notificaciones real-time | WebSockets u otro mecanismo push (reemplaza polling) |
| B4 | Retry con back-off exponencial | Back-off exponencial antes de reintentar mensaje fallido |
| B5 | Observabilidad | Structured logging + métricas a AWS + `GET /health` con estado de dependencias |
| B6 | Tests avanzados | Cobertura ≥ 70% con pytest: unit tests worker, integration tests POST /jobs, test de fallo |

---

## Criterios de DESCALIFICACIÓN AUTOMÁTICA

- Credenciales AWS / tokens JWT / passwords en el repo
- El sistema NO arranca con `docker compose up` siguiendo el README
- App NO está desplegada en AWS real con URL pública
- No existe pipeline GitHub Actions o nunca corrió
- No se usa ningún servicio de mensajería/colas de AWS
- El worker es completamente síncrono (sin concurrencia)
- No se crea el usuario IAM de acceso para revisión
- Ausencia de `TECHNICAL_DOCS.md` o `SKILL.md`
- Código íntegramente generado por IA sin comprensión del candidato
