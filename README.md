# Prosperas Reports — Async Report Generation Platform

![CI/CD](https://github.com/cdtello/prosperas-challenge/actions/workflows/deploy.yml/badge.svg?branch=main)

Sistema SaaS de reportes asincrónicos construido con FastAPI, AWS SQS, PostgreSQL y React 18.

**Frontend (producción):** `https://d2v3qmq1azg45r.cloudfront.net`
**API (producción):** `http://34.229.46.113:8000`
**API Docs:** `http://34.229.46.113:8000/docs`

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

## Arquitectura

```
Browser (HTTPS)
    │
    ├─ https://d2v3qmq1azg45r.cloudfront.net/         → CloudFront → S3 (React SPA)
    └─ https://d2v3qmq1azg45r.cloudfront.net/jobs     → CloudFront → EC2:8000 (FastAPI)
                                                                            │
                                                                     AWS SQS + DLQ
                                                                            │
                                                                     Worker (asyncio)
                                                                            │
                                                              RDS PostgreSQL + S3
```

Ver diagrama completo en [TECHNICAL_DOCS.md](./TECHNICAL_DOCS.md#1-diagrama-de-arquitectura).

---

## Stack

| Capa | Tecnología | Dónde |
|------|------------|-------|
| Frontend | React 18 + Vite + TailwindCSS | S3 + CloudFront (HTTPS) |
| Backend API | Python 3.11 / FastAPI | EC2 t3.micro |
| Workers | Python asyncio + Semaphore | EC2 t3.micro |
| Cola | AWS SQS + Dead Letter Queue | AWS |
| Base de datos | AWS RDS PostgreSQL 15 | AWS |
| Almacenamiento | AWS S3 | AWS |
| Imágenes Docker | AWS ECR | AWS |
| Local dev | LocalStack + Docker Compose | Docker |
| CI/CD | GitHub Actions | → EC2 + S3 + CloudFront |

---

## CI/CD Pipeline

```
push → main
  ├── test:   ruff lint + pytest (95% coverage, fail_under=90)
  ├── backend: build Docker → ECR → SSH EC2 → docker compose up
  ├── frontend: npm build → S3 sync → CloudFront invalidation
  └── smoke-test: curl /health + curl CloudFront
```

---

## Documentación

| Documento | Descripción |
|-----------|-------------|
| [TECHNICAL_DOCS.md](./TECHNICAL_DOCS.md) | Arquitectura, servicios AWS, decisiones de diseño, setup local, CI/CD, variables de entorno, tests |
| [SKILL.md](./SKILL.md) | Contexto para agente IA: mapa del repo, patrones, comandos, errores comunes, cómo extender |
| [docs/AI_WORKFLOW.md](./docs/AI_WORKFLOW.md) | Evidencia del uso de IA en el desarrollo |

---

## Credenciales de revisión

Usuario IAM con `AdministratorAccess` para revisión del evaluador:

```
Account: 990151165442
# Las credenciales se envían por correo separado — nunca en el repo
```
