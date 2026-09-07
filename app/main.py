import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services.notifications import process_pending_jobs
from app.routes import auth, dashboard, public, widgets


logging.basicConfig(level=logging.INFO)


async def notification_worker():
    while True:
        try:
            await asyncio.to_thread(process_pending_jobs)
        except Exception:
            logging.exception(
                "Notification worker failed"
            )

        await asyncio.sleep(5)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(widgets.router)
app.include_router(public.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.on_event("startup")
async def startup():
    asyncio.create_task(notification_worker())