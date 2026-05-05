from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web.backend.dependencies import get_settings
from web.backend.routers import benchmarks, experiments, infrastructure, models, results


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Thesis Experiment Platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(experiments.router, prefix="/api")
    app.include_router(models.router, prefix="/api")
    app.include_router(results.router, prefix="/api")
    app.include_router(infrastructure.router, prefix="/api")
    app.include_router(benchmarks.router, prefix="/api")

    @app.get("/health")
    async def health():
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
