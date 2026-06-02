import asyncio
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware

from src.config import settings
from src.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    logger = logging.getLogger("uvicorn.access")
    console_formatter = uvicorn.logging.ColourizedFormatter(  # noqa
        "{asctime} {levelprefix} : {message}", style="{", use_colors=False
    )
    logger.handlers[0].setFormatter(console_formatter)

    yield



def run_migrations():
    if settings.DOCKERIZED == 1:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")


if settings.ENVIRONMENT == "DEV":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    app = FastAPI(
        title=settings.APP_NAME,
        lifespan=lifespan,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "syntaxHighlight.theme": "arta",
            "displayRequestDuration": True,
            "filter": True,
        },
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for error in exc.errors():
            loc = [str(location) for location in error["loc"] if location != "body"]
            errors.append({
                "field": ".".join(loc),
                "msg": error["msg"].replace("Value error, ", ""),
            })
        return JSONResponse(
            status_code=400,
            content={"detail": errors},
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=[
            "Content-Type",
            "Set-Cookie",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin",
            "Authorization",
            "X-Pow-Hash",
            "X-TS",
        ],
        expose_headers=["Authorization"],
    )
    app.include_router(api_router)


elif settings.ENVIRONMENT == "PROD":
    ...

if __name__ == "__main__":
    run_migrations()
    uvicorn.run(app, host="0.0.0.0", port=settings.APP_PORT)
