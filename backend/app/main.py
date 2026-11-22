import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .config import settings
from .database import init_db
from .integrations.telegram_bot import telegram_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("nexus")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info(
        "NEXUS starting | mode=%s | llm=%s | telegram=%s",
        "demo" if settings.demo_mode else "live",
        "configured" if settings.llm_configured else "not configured",
        "configured" if settings.telegram_configured else "not configured",
    )
    await telegram_manager.start()
    yield
    await telegram_manager.stop()


app = FastAPI(
    title="NEXUS — Autonomous Mission Control",
    description="Transforms objectives into coordinated multi-agent workflows.",
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

app.include_router(router)


@app.get("/")
def root():
    return {
        "app": "NEXUS",
        "status": "online",
        "mode": "demo" if settings.demo_mode else "live",
        "docs": "/docs",
        "api": "/api/health",
    }
