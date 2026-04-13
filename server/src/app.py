import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.log_sync import sync_invite_hub_logs
from src.routes.students import router as students_router
from src.settings import (
    get_invite_hub_background_sync_enabled,
    get_invite_hub_background_sync_interval_s,
    is_invite_hub_sync_configured,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()


def get_allowed_origins() -> list[str]:
    configured_origins = os.getenv("BACKEND_CORS_ORIGINS", "")
    if configured_origins.strip():
        return [
            origin.strip()
            for origin in configured_origins.split(",")
            if origin.strip()
        ]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


async def run_invite_hub_sync_loop(stop_event: asyncio.Event) -> None:
    interval_s = get_invite_hub_background_sync_interval_s()
    logger.info("Invite Hub background sync started with interval=%ss.", interval_s)
    while not stop_event.is_set():
        try:
            synced_count = await asyncio.to_thread(sync_invite_hub_logs)
            if synced_count:
                logger.info(
                    "Invite Hub background sync fetched %s new records.",
                    synced_count,
                )
        except Exception:
            logger.exception("Invite Hub background sync failed.")

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval_s)
        except asyncio.TimeoutError:
            continue


@asynccontextmanager
async def lifespan(_: FastAPI):
    stop_event: asyncio.Event | None = None
    sync_task: asyncio.Task[None] | None = None

    if get_invite_hub_background_sync_enabled():
        if is_invite_hub_sync_configured():
            stop_event = asyncio.Event()
            sync_task = asyncio.create_task(
                run_invite_hub_sync_loop(stop_event),
                name="invite-hub-background-sync",
            )
        else:
            logger.info(
                "Invite Hub background sync is enabled but no Invite Hub credentials were found."
            )
    else:
        logger.info("Invite Hub background sync is disabled by configuration.")

    try:
        yield
    finally:
        if stop_event is not None and sync_task is not None:
            stop_event.set()
            await sync_task


app = FastAPI(title="Pedagogical AI Agent API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(students_router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
