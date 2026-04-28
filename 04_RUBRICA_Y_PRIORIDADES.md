# Rúbrica de Evaluación y Prioridades de Implementación

## Puntaje por Criterio

| Criterio | Puntos | Prioridad |
|----------|--------|-----------|
| Manejo de Colas & Mensajería | 15 pts | 🔴 CRÍTICO |
| Concurrencia & Workers | 15 pts | 🔴 CRÍTICO |
| Despliegue en producción AWS | 15 pts | 🔴 CRÍTICO |
| Arquitectura & Diseño AWS | 10 pts | 🟠 ALTO |
| API REST (FastAPI) | 10 pts | 🟠 ALTO |
| Frontend (React) | 10 pts | 🟠 ALTO |
| Pipeline CI/CD | 10 pts | 🟠 ALTO |
| Documentación (TECHNICAL_DOCS.md) | 10 pts | 🟡 MEDIO |
| AI Skill (SKILL.md) | 5 pts | 🟡 MEDIO |
| **TOTAL CORE** | **100 pts** | |
| Bonus B1–B6 | +25 pts | 🟢 OPCIONAL |

**Mínimo aprobatorio:** 60 / 100  
**Para avanzar a entrevista:** 70+ puntos o 80+ con bonus

---

## Orden Recomendado de Implementación

### Semana — Distribución sugerida

**Día 1-2: Backend Core + DB**
- [ ] Setup proyecto FastAPI con estructura de carpetas
- [ ] Modelo de datos Job (Pydantic + ORM)
- [ ] Endpoints POST /jobs, GET /jobs/{id}, GET /jobs (paginado)
- [ ] JWT auth básico
- [ ] Manejo centralizado de errores
- [ ] Conexión a DB (local con SQLite o LocalStack)

**Día 2-3: Cola + Worker**
- [ ] Integración con SQS (boto3)
- [ ] Worker que consume la cola con asyncio
- [ ] Procesamiento concurrente (≥2 en paralelo)
- [ ] Actualización de estados en DB
- [ ] Dead Letter Queue para fallos

**Día 3-4: Frontend**
- [ ] Setup React (Vite o Next.js)
- [ ] Formulario de solicitud de reporte
- [ ] Lista de jobs con badges de colores
- [ ] Polling automático cada 3s
- [ ] Manejo de errores visual
- [ ] Responsive design

**Día 4-5: Docker + LocalStack**
- [ ] Dockerfile backend
- [ ] docker-compose.yml con LocalStack
- [ ] Script init-aws.sh (crea SQS, bucket S3, tabla)
- [ ] Verificar `docker compose up` funciona desde cero

**Día 5-6: AWS Real + CI/CD**
- [ ] Setup cuenta AWS
- [ ] Crear recursos: SQS, RDS/DynamoDB, ECR
- [ ] Pipeline GitHub Actions (build → push ECR → deploy ECS o EC2)
- [ ] Verificar URL pública accesible con HTTPS

**Día 6-7: Documentación + Pulido**
- [ ] TECHNICAL_DOCS.md (con Claude Code)
- [ ] SKILL.md (con Claude Code)
- [ ] AI_WORKFLOW.md (evidencia de uso de IA)
- [ ] README completo con badge y URL
- [ ] Tests básicos (si se busca bonus B6)
- [ ] Crear usuario IAM para revisión

---

## Lo que el Evaluador Mirará Primero

1. ¿Funciona `docker compose up`? → Si no, FAIL inmediato
2. ¿Hay URL pública de producción? → Si no, FAIL inmediato
3. ¿El pipeline GitHub Actions está verde? → Si no, penalización severa
4. ¿Los workers procesan en paralelo? → Core del challenge
5. ¿Existen TECHNICAL_DOCS.md y SKILL.md? → Si no, FAIL

---

## Checklist Final Antes de Entregar

### Obligatorios
- [ ] Repo público GitHub con nombre correcto
- [ ] `docker compose up` levanta todo sin errores
- [ ] URL pública de producción accesible
- [ ] GitHub Actions badge en verde
- [ ] JWT auth funcionando
- [ ] Los 3 endpoints de /jobs implementados
- [ ] Worker procesa ≥2 jobs en paralelo
- [ ] Estados se actualizan: PENDING → PROCESSING → COMPLETED/FAILED
- [ ] DLQ configurada para mensajes fallidos
- [ ] Frontend actualiza sin recargar
- [ ] TECHNICAL_DOCS.md presente y completo
- [ ] SKILL.md presente y completo
- [ ] AI_WORKFLOW.md con evidencia de IA
- [ ] .env.example con todas las variables
- [ ] CERO credenciales hardcodeadas en el código
- [ ] Usuario IAM creado con AdministratorAccess

### Seguridad crítica
- [ ] `.env` en `.gitignore`
- [ ] Credenciales AWS solo en GitHub Secrets (no en código)
- [ ] JWT secret en variable de entorno
- [ ] Revisar git log que no haya commit con credenciales

---

## Bonus Recomendados (si hay tiempo)

**B3 — WebSockets** (más impacto visual en demo)  
**B6 — Tests avanzados** (10 pts extra, fácil con pytest)  
**B4 — Back-off exponencial** (mejora real de la resiliencia, relativamente simple)  

**No priorizar:**  
B1 (prioridad de colas) y B2 (Circuit Breaker) son más complejos y el retorno es menor.

---

## Tips para la Defensa (30 min)

- Saber explicar **por qué elegiste cada servicio AWS** (SQS vs otros, RDS vs DynamoDB)
- Saber explicar **cómo funciona la concurrencia** en el worker (asyncio, gather, etc.)
- Saber explicar **qué pasa cuando un job falla** (visibilidad SQS, DLQ, retry)
- Estar preparado para **extender una funcionalidad en vivo** (ej: agregar un nuevo report_type)
- SKILL.md será abierto en Claude sin acceso al código — debe responder todo
