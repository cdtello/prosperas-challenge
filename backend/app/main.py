from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.inbound.http.routes import auth, jobs
from app.adapters.outbound.persistence.models import JobModel, UserModel  # noqa: F401
from app.infrastructure.db import Base, engine
from app.infrastructure.errors import register_error_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Prosperas Reports API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(auth.router)
app.include_router(jobs.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
