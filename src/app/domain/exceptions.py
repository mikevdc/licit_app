from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class LicitError(Exception):
    """Clase base para todos los errores de la aplicación"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AuctionNotFoundError(LicitError):
    """Lanzada cuando una subasta no existe."""
    pass

class UserNotFoundError(LicitError):
    """Lanzada cuando un usuario no existe."""
    pass

class InvalidBidError(LicitError):
    """Lanzada cuando una puja no cumple las reglas (precio bajo, tiempo expirado...)."""
    pass

class InfraestructureError(LicitError):
    """Lanzada cuando algo falla en la perisistencia o en servicios externos."""


class DomainError(Exception):
    status_code = 400


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(LicitError)
    async def licit_generic_handler(request: Request, exc: LicitError):
        # Error genérico 400 para errores de negocio no especificados
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {"error_code": "BUSINESS_RULE_VIOLATION", "message": exc.message}
        )
    

    @app.exception_handler(AuctionNotFoundError)
    async def auction_not_found_handler(request: Request, exc: AuctionNotFoundError):
        return JSONResponse(
            status_code = status.HTTP_404_NOT_FOUND,
            content = {"error_code": "AUCTION_NOT_FOUND", "message": exc.message}
        )
    

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        return JSONResponse(
            status_code = status.HTTP_404_NOT_FOUND,
            content = {"error_code": "USER_NOT_FOUND", "message": exc.message}
        )
    

    @app.exception_handler(InvalidBidError)
    async def invalid_bid_handler(request: Request, exc: InvalidBidError):
        return JSONResponse(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            content = {"error_code": "INVALID_BID", "message": exc.message}
        )


    @app.exception_handler(Exception)
    async def universal_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            content = {"error_code": "INTERNAL_SERVER_ERROR", "message": "Ha ocurrido un error inesperado en el servidor. Por favor, contacte con soporte."}
        )
