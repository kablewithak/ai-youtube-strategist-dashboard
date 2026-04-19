from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.recommendations import router as recommendations_router
from app.api.routes.runs import router as runs_router
from app.api.routes.synthesis import router as synthesis_router
from app.api.routes.uploads import router as uploads_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_allow_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(runs_router)
app.include_router(ingestion_router)
app.include_router(uploads_router)
app.include_router(synthesis_router)
app.include_router(recommendations_router)