from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    Esquema para validar el contenido interno (payload) del token
    cuando lo decodificamos en 'get_current_user'.
    """
    sub: str | None = None
