import logging
from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI

from src.router import api_router
from src.users.router import router as users_router

@asynccontextmanager
async def lifespan(app: FastAPI): # noqa
    logger = logging.getLogger("uvicorn.access")
    console_formatter = uvicorn.logging.ColourizedFormatter( # noqa
    "{asctime} {levelprefix} : {message}", style="{", use_colors=False
    )
    logger.handlers[0].setFormatter(console_formatter)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
app.include_router(users_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
