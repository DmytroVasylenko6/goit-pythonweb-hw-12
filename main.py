import asyncio
import logging
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from alembic import command
from alembic.config import Config
from src.api import auth, contacts, users, utils
from src.services.limiter import limiter
from src.services.redis_cache import redis_cache

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)
logging.getLogger("uvicorn.access").setLevel(logging.DEBUG)
logging.getLogger("fastapi.middleware").setLevel(logging.DEBUG)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handle rate limit exceptions.

    :param request: Incoming request object.
    :param exc: Raised RateLimitExceeded exception.
    :return: JSON response with a 429 status code.
    """
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded. Try again later."},
    )


app.include_router(contacts.router, prefix="/api")
app.include_router(utils.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")


def run_migrations():
    """
    Apply database migrations using Alembic.
    """
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@app.on_event("startup")
async def startup_event():
    """
    Run database migrations when the application starts.
    """
    try:
        await asyncio.to_thread(run_migrations)
        await redis_cache.connect()
    except Exception as e:
        import traceback

        print("Startup error:", e)
        traceback.print_exc()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
