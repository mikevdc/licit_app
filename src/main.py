import uvicorn

from app.api.middleware.trace import request_id_middleware
from app.api.v1.api import api_router
from app.core.logging_setup import setup_logging
from app.core.config import settings
from app.domain.exceptions import setup_exception_handlers

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


setup_logging()

def create_application() -> FastAPI:
    """
    Factory para crear la instancia de FastAPI configurada.
    """
    app = FastAPI(
        title = settings.APP_NAME,
        version = "0.1.0",
        openapi_url = f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None
    )

    # 1. Configuración de Middlewares
    # (CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins = ["*"], # En producción hay que especificar dominios reales
        allow_credentials = True,
        allow_methods = ["*"],
        allow_headers = ["*"],
    )

    # (Request ID)
    app.middleware("http")(request_id_middleware)

    # 2. Registro de rutas
    app.include_router(api_router, prefix = settings.API_V1_STR)

    # 3. Configuración de Exception Handlers
    setup_exception_handlers(app)

    return app


# Instancia de la aplicación
app = create_application()

@app.get("/health", tags = ["Health"])
async def health_check():
    """Endpoint simple para verificar que la API está viva."""
    return {"status": "ok", "environment": "dev" if settings.DEBUG else "prod"}


if __name__ == '__main__':
    uvicorn.run("main:app", host = "127.0.0.1", port = 8000, reload = True, reload_dirs = ["src"], log_level = "debug")
