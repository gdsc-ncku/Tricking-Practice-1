from jwt import encode
from pydantic import BaseModel

from typing import Union

from config import JWT_KEY
from schemas.jwt import JWT, JWTPayload


def generate_jwt(payload: Union[JWTPayload, BaseModel, dict]) -> JWT:
    if isinstance(payload, JWTPayload):
        data = payload.model_dump()
    elif isinstance(payload, BaseModel):
        data = JWTPayload(**payload.model_dump()).model_dump()
    else:
        data = JWTPayload(**payload).model_dump()

    token = encode(
        payload=data,
        key=JWT_KEY
    )
    return JWT(access_token=token)
