# Prueba Técnica — Prosperas · Full-Stack Developer

## Contexto General

**Empresa:** Prosperas  
**Rol:** Full-Stack Developer (nivel Semi-senior obligatorio, Senior con bonus)  
**Plazo:** 7 días calendario desde recepción  
**Entrega:** Repositorio público GitHub — `{tu-nombre}-prosperas-challenge`  
**Stack requerido:** Python 3.11+ · FastAPI · React 18+ · AWS

---

## El Problema a Resolver

Una plataforma SaaS de analítica necesita un sistema que permita a usuarios generar **reportes bajo demanda de forma asíncrona**. Los reportes pueden tardar entre 5 segundos y varios minutos, por lo que el procesamiento NO puede ser síncrono.

**El sistema debe:**
- Recibir solicitudes y responder de inmediato (sin bloquear)
- Encolar el trabajo en AWS para procesamiento asíncrono
- Procesar al menos 2 jobs en paralelo con workers concurrentes
- Persistir el estado: `PENDING → PROCESSING → COMPLETED / FAILED`
- Mostrar actualizaciones en tiempo real en el frontend (sin recarga)
- Ser resiliente ante fallos

> **Nota:** El procesamiento del reporte puede simularse con `sleep` aleatorio (5–30 s) + datos dummy. No se requiere integración real.

---

## Stack y Servicios

| Capa | Tecnología | Dónde corre |
|------|------------|-------------|
| Backend API | Python 3.11+ / FastAPI | Docker / AWS |
| Cola de mensajes | AWS (a elección) | AWS real |
| Base de datos | AWS (a elección) | AWS real |
| Workers | Python async / concurrent | Docker / AWS |
| Frontend | React 18+ | AWS real |
| Dev local | LocalStack | Docker Compose |
| CI/CD | GitHub Actions | → deploys a AWS |

---

## Estructura de Repositorio Sugerida

```
{nombre}-prosperas-challenge/
  backend/
    app/
      api/        # routers FastAPI
      core/       # config, auth, db
      models/     # Pydantic + ORM models
      services/   # business logic
      worker/     # queue consumer + processor
    Dockerfile
  frontend/
    src/
      components/
      hooks/
      services/
  local/          # docker-compose + LocalStack (dev)
  infra/          # IaC producción AWS
  .github/
    workflows/    # GitHub Actions pipeline
  .env.example
  TECHNICAL_DOCS.md
  SKILL.md
  README.md
```

---

## Proceso de Entrega

1. **Repo público** GitHub: `{tu-nombre}-prosperas-challenge`
2. **Despliegue real** en AWS con URL pública accesible
3. **Usuario IAM** con `AdministratorAccess` — compartir credenciales al entregar
4. **README** con: URL producción, diagrama de arquitectura, setup local, decisiones
5. **Enviar**: repo + URL prod + credenciales IAM a `hiring@prosperas.co`
6. **Defensa**: 30 min revisando código, infraestructura y decisiones de diseño

---

## Costos AWS

Diseñada para **free tier** de AWS. Si hay costos, Prosperas reembolsa hasta **USD $10**.
