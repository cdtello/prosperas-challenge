# Prosperas Reports — Async Report Generation Platform

![CI/CD](https://github.com/cdtello/prosperas-challenge/actions/workflows/deploy.yml/badge.svg?branch=main)

Sistema SaaS de reportes asincrónicos construido con FastAPI, AWS SQS, PostgreSQL y React 18.

**URL de producción:** `http://34.229.46.113:8000`  
**Docs API:** `http://34.229.46.113:8000/docs`

---

## Inicio Rápido (Local)

```bash
git clone https://github.com/cdtello/prosperas-challenge.git
cd prosperas-challenge
cp .env.example .env
docker compose up --build
```

- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **Docs API (Swagger):** http://localhost:8000/docs

---

## Documentación

| Documento | Descripción |
|-----------|-------------|
| [TECHNICAL_DOCS.md](./TECHNICAL_DOCS.md) | Arquitectura, servicios AWS, decisiones de diseño, setup local, CI/CD, variables de entorno, tests |
| [SKILL.md](./SKILL.md) | Contexto para agente IA: mapa del repo, patrones, comandos, errores comunes, cómo extender |
| [docs/AI_WORKFLOW.md](./docs/AI_WORKFLOW.md) | Evidencia del uso de IA en el desarrollo |

---

## Arquitectura

```
React 18 → FastAPI → SQS → Worker (asyncio) → PostgreSQL + S3
```

Ver diagrama completo en [TECHNICAL_DOCS.md](./TECHNICAL_DOCS.md#1-diagrama-de-arquitectura).

---

## Stack

| Capa | Tecnología |
|------|------------|
| Backend API | Python 3.11 / FastAPI |
| Cola | AWS SQS + Dead Letter Queue |
| Base de datos | AWS RDS PostgreSQL |
| Workers | Python asyncio (`asyncio.gather`) |
| Almacenamiento | AWS S3 |
| Frontend | React 18 + Vite + TailwindCSS |
| Local | LocalStack + Docker Compose |
| CI/CD | GitHub Actions → ECS Fargate |

---

## Credenciales de revisión

Usuario IAM con `AdministratorAccess` para revisión del evaluador:

```
Account: 990151165442
# Las credenciales se envían por correo separado — nunca en el repo
```
