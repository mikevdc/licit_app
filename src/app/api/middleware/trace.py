import uuid
from app.core.logging_setup import request_id_var
from fastapi import Request


async def request_id_middleware(request: Request, call_next):
    # 1. Generar UUID único para esta petición
    rid = str(uuid.uuid4())

    # 2. Establecerlo en el contexto (esto lo hará disponible para todos los logs)
    token = request_id_var.set(rid)

    try:
        response = await call_next(request)
        # 3. (Opcional) Devolver el ID al cliente en las cabeceras
        response.headers["X-Request-ID"] = rid
        return response
    finally:
        # 4. Limpiar el contexto al terminar la petición
        request_id_var.reset(token)
