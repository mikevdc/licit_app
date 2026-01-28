import uuid
from app.core.logging_setup import request_id_var
from fastapi import Request


async def request_id_middleware(request: Request, call_next):
    # 1. Generar UUID único para esta petición
    request_id = str(uuid.uuid4())

    # 2. Guardar el request_id en el estado del objeto Request
    request.state.request_id = request_id

    # 2. Establecerlo en el contexto (esto lo hará disponible para todos los logs)
    token = request_id_var.set(request_id)

    try:
        response = await call_next(request)
        # 3. (Opcional) Devolver el ID al cliente en las cabeceras
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        # 4. Limpiar el contexto al terminar la petición
        request_id_var.reset(token)
