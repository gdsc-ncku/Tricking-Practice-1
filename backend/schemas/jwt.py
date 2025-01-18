from pydantic import BaseModel, Field, field_validator, ValidationError

from datetime import datetime, timedelta
from typing import Any
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc

from .user import UserView


class JWTPayload(UserView):
    iat: datetime = Field(default_factory=lambda: datetime.now(UTC))
    exp: datetime = Field(
        default_factory=lambda: datetime.now(UTC) + timedelta(days=7)
    )

    @field_validator("exp", "iat", mode="before")
    @classmethod
    def valid_exp(cls, value: Any):
        if isinstance(value, datetime):
            return value

        try:
            return datetime.fromtimestamp(value, tz=UTC)
        except:
            raise ValidationError


class JWT(BaseModel):
    token_type: str = "Bearer"
    access_token: str
