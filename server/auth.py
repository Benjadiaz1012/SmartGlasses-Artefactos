
import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from config import API_TOKEN


token_header = APIKeyHeader(
    name="X-Token",
    auto_error=False
)


def verify_token(
    token: str = Security(token_header)
):

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token requerido"
        )

    if not secrets.compare_digest(
        token.encode("utf-8"),
        API_TOKEN.encode("utf-8")
    ):
        raise HTTPException(
            status_code=401,
            detail="Token incorrecto"
        )
